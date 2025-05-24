import os
import socket
import ipaddress
import math
import argparse
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import werkzeug.exceptions

# Importações do Tkinter
import tkinter
from tkinter import filedialog

# --- Configurações Dinâmicas da Pasta ---
DIRETORIO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_A_COMPARTILHAR = None
NOME_SUBPASTA_COMPARTILHADA = None
NOME_PADRAO_SUBPASTA = "Arquivos_Compartilhados_WebApp"
PORTA = 5000
# --------------------------------------

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_melhor_aqui_e_unica'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024
# app.config['UPLOAD_FOLDER'] será definido após PASTA_A_COMPARTILHAR ser determinada


def garantir_pasta_compartilhada(caminho_da_pasta):
    if not os.path.exists(caminho_da_pasta):
        try:
            os.makedirs(caminho_da_pasta)
            print(f"Pasta de compartilhamento '{caminho_da_pasta}' criada com sucesso.")
        except Exception as e:
            print(f"ERRO CRÍTICO: Não foi possível criar a pasta de compartilhamento '{caminho_da_pasta}': {e}")
            print("Verifique as permissões no diretório especificado ou crie a pasta manualmente.")
            exit(1)
    if not os.access(caminho_da_pasta, os.W_OK | os.R_OK):
        print(f"ERRO CRÍTICO: Sem permissão de escrita/leitura na pasta '{caminho_da_pasta}'.")
        print("Verifique as permissões da pasta.")
        exit(1)

def obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        ip_local = s.getsockname()[0]
    except Exception:
        try:
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            if ip_local == "127.0.0.1":
                ips = socket.gethostbyname_ex(hostname)[2]
                ip_local = next((ip for ip in ips if not ipaddress.ip_address(ip).is_loopback), None)
                if not ip_local:
                    ips = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None) if i[0] == socket.AF_INET]
                    ip_local = next((ip for ip in ips if not ipaddress.ip_address(ip).is_loopback and not ipaddress.ip_address(ip).is_link_local), ips[0] if ips else None)
        except socket.gaierror:
            ip_local = "Não foi possível determinar o IP."
    finally:
        if 's' in locals():
            s.close()
    return ip_local if ip_local else "127.0.0.1 (Verifique IP manualmente)"

def format_file_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.log(size_bytes, 1024)) if size_bytes > 0 else 0
    p = pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# --- Função para selecionar pasta com GUI Tkinter ---
def selecionar_pasta_gui():
    """Abre uma caixa de diálogo para o usuário selecionar uma pasta."""
    root = tkinter.Tk()
    root.withdraw() # Esconde a janela principal do Tkinter
    caminho_pasta_padrao = os.path.join(DIRETORIO_DO_SCRIPT, NOME_PADRAO_SUBPASTA)
    
    # Tenta criar o diretório padrão se ele não existir, para que apareça na sugestão
    # Isso é opcional, mas pode melhorar a experiência do usuário
    if not os.path.exists(caminho_pasta_padrao):
        try:
            os.makedirs(caminho_pasta_padrao, exist_ok=True)
        except Exception:
            pass # Se não puder criar, a caixa de diálogo abrirá no diretório atual

    caminho_selecionado = filedialog.askdirectory(
        initialdir=DIRETORIO_DO_SCRIPT, # Começa no diretório do script
        title="Selecione a pasta para compartilhamento"
    )
    root.destroy() # Fecha a instância do Tkinter
    return caminho_selecionado
# ----------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado!'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado!'}), 400
        if file:
            filename = secure_filename(file.filename)
            if not filename:
                 return jsonify({'success': False, 'message': 'Nome de arquivo inválido ou inseguro.'}), 400
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return jsonify({'success': True, 'message': f'Arquivo "{filename}" enviado com sucesso!', 'filename': filename})
            except werkzeug.exceptions.RequestEntityTooLarge as e:
                app.logger.error(f"Erro ao salvar o arquivo {filename}: Arquivo muito grande. {e.description}")
                return jsonify({'success': False, 'message': f'Erro: Arquivo muito grande. Limite: {format_file_size(app.config["MAX_CONTENT_LENGTH"])}'}), 413
            except Exception as e:
                app.logger.error(f"Erro ao salvar o arquivo {filename}: {e}")
                return jsonify({'success': False, 'message': f'Erro ao salvar o arquivo: {str(e)}'}), 500
        return jsonify({'success': False, 'message': 'Erro inesperado no upload.'}), 500

    items = []
    show_content = True
    try:
        for item_name in sorted(os.listdir(PASTA_A_COMPARTILHAR)):
            item_path = os.path.join(PASTA_A_COMPARTILHAR, item_name)
            is_dir = os.path.isdir(item_path)
            try:
                size_bytes = os.path.getsize(item_path) if not is_dir else 0
                size_readable = format_file_size(size_bytes)
            except OSError:
                size_readable = "N/A"
            items.append({'name': item_name, 'is_dir': is_dir, 'size': size_readable})
    except Exception as e:
        flash(f"ERRO ao listar conteúdo da pasta '{PASTA_A_COMPARTILHAR}': {e}", 'error_fatal')
        show_content = False
    return render_template('index.html',
                           items=items,
                           pasta_base=NOME_SUBPASTA_COMPARTILHADA,
                           show_content=show_content)

@app.route('/download/<path:filename>')
def download_file(filename):
    safe_base = os.path.abspath(app.config['UPLOAD_FOLDER'])
    s_filename = secure_filename(filename)
    if not s_filename:
        flash("Nome de arquivo inválido para download.", "danger")
        return redirect(url_for('index'))
    requested_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], s_filename))
    if not requested_path.startswith(safe_base):
        flash("Tentativa de acesso inválida (Path Traversal).", "danger")
        return redirect(url_for('index'))
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], s_filename, as_attachment=True)
    except FileNotFoundError:
        flash(f"Arquivo '{s_filename}' não encontrado para download.", "warning")
    except Exception as e:
        flash(f"Erro ao baixar o arquivo '{s_filename}': {e}", "danger")
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    safe_base = os.path.abspath(app.config['UPLOAD_FOLDER'])
    file_to_delete = secure_filename(filename)
    if not file_to_delete:
        flash("Nome de arquivo inválido para exclusão.", "danger")
        return redirect(url_for('index'))
    requested_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], file_to_delete))
    if not requested_path.startswith(safe_base):
        flash("Tentativa de acesso inválida para apagar arquivo (Path Traversal).", "danger")
        return redirect(url_for('index'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_to_delete)
    try:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                os.remove(file_path)
                flash(f'Arquivo "{file_to_delete}" apagado com sucesso!', 'success')
            elif os.path.isdir(file_path):
                 flash(f'"{file_to_delete}" é um diretório e não pode ser apagado por esta função.', 'warning')
            else:
                flash(f'"{file_to_delete}" não é um arquivo regular e não pode ser apagado.', 'warning')
        else:
            flash(f'Arquivo "{file_to_delete}" não encontrado para apagar.', 'warning')
    except PermissionError:
        flash(f'Sem permissão para apagar o arquivo "{file_to_delete}". Verifique as permissões do servidor.', 'danger')
    except Exception as e:
        flash(f'Erro ao apagar o arquivo "{file_to_delete}": {e}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Servidor Flask para compartilhamento de arquivos.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-f", "--folder",
        type=str,
        help=(
            "Caminho para a pasta a ser compartilhada.\n"
            "Se não especificado, uma caixa de diálogo GUI será exibida para seleção.\n"
            f"O padrão interativo (se a GUI for cancelada ou falhar) é criar/usar '{NOME_PADRAO_SUBPASTA}' no diretório do script."
        )
    )
    args = parser.parse_args()

    caminho_final_escolhido = None

    if args.folder:
        caminho_final_escolhido = args.folder
        print(f"Usando pasta especificada por argumento: {caminho_final_escolhido}")
    else:
        print("Abrindo caixa de diálogo para seleção de pasta...")
        caminho_gui = selecionar_pasta_gui()
        if caminho_gui: # Se o usuário selecionou uma pasta
            caminho_final_escolhido = caminho_gui
            print(f"Pasta selecionada via GUI: {caminho_final_escolhido}")
        else: # Usuário cancelou a caixa de diálogo
            print("Nenhuma pasta selecionada através da GUI. Encerrando o servidor.")
            # Alternativamente, poderia usar um padrão aqui:
            # print(f"Nenhuma pasta selecionada. Usando padrão: {os.path.join(DIRETORIO_DO_SCRIPT, NOME_PADRAO_SUBPASTA)}")
            # caminho_final_escolhido = os.path.join(DIRETORIO_DO_SCRIPT, NOME_PADRAO_SUBPASTA)
            exit(0) # Sai do script se o usuário cancelar

    # Define PASTA_A_COMPARTILHAR e NOME_SUBPASTA_COMPARTILHADA globalmente
    PASTA_A_COMPARTILHAR = os.path.abspath(caminho_final_escolhido)
    NOME_SUBPASTA_COMPARTILHADA = os.path.basename(PASTA_A_COMPARTILHAR)
    
    if not NOME_SUBPASTA_COMPARTILHADA:
        try:
            drive_letter = os.path.splitdrive(PASTA_A_COMPARTILHAR)[0]
            if drive_letter:
                 NOME_SUBPASTA_COMPARTILHADA = f"Raiz_{drive_letter.replace(':', '')}"
            else:
                NOME_SUBPASTA_COMPARTILHADA = "Raiz_do_Sistema"
        except Exception:
             NOME_SUBPASTA_COMPARTILHADA = "Pasta_Raiz_Selecionada"

    app.config['UPLOAD_FOLDER'] = PASTA_A_COMPARTILHAR
    garantir_pasta_compartilhada(PASTA_A_COMPARTILHAR)

    meu_ip_local = obter_ip_local()
    print(f"Servidor Flask iniciado.")
    print(f"Pasta de compartilhamento (caminho completo): {PASTA_A_COMPARTILHAR}")
    print(f"Nome da pasta na interface: {NOME_SUBPASTA_COMPARTILHADA}")
    print(f"Acesse de outro dispositivo na rede através de: http://{meu_ip_local}:{PORTA}")
    print(f"Ou acesse localmente em: http://127.0.0.1:{PORTA}")
    print("****************************************************************************")
    print("ATENÇÃO MÁXIMA: Funcionalidade de APAGAR ARQUIVOS está ATIVA!")
    print("Qualquer pessoa com o link pode APAGAR arquivos PERMANENTEMENTE.")
    print("Use esta ferramenta apenas em redes 100% confiáveis e por sua conta e risco.")
    print("****************************************************************************")
    print("Pressione Ctrl+C para parar o servidor.")
    app.run(host='0.0.0.0', port=PORTA, debug=False)