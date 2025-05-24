# flask-lan-file-sharer

Um servidor web simples construído com Flask para compartilhar arquivos facilmente em sua rede local (LAN). Permite fazer upload, download e apagar arquivos através de uma interface web amigável.

## Funcionalidades Principais

*   **Interface Web Intuitiva:** Navegue, envie e gerencie arquivos pelo seu navegador.
*   **Upload de Arquivos:** Envie arquivos para a pasta compartilhada com barra de progresso e opção de cancelamento.
*   **Download de Arquivos:** Baixe arquivos diretamente pelo navegador.
*   **Exclusão de Arquivos:** Apague arquivos da pasta compartilhada (com confirmação).
*   **Seleção Dinâmica da Pasta:**
    *   Especifique a pasta a ser compartilhada via argumento de linha de comando.
    *   Ou selecione interativamente usando uma caixa de diálogo GUI (Tkinter) ao iniciar o servidor (se nenhum argumento for fornecido).
*   **Visualização de Tamanho de Arquivo:** Mostra o tamanho dos arquivos de forma legível.
*   **Responsivo (Bootstrap):** Interface se adapta a diferentes tamanhos de tela.
*   **Configuração de Limite de Upload:** Limite de upload de arquivos configurável (padrão 5GB).

## Tecnologias Utilizadas

*   **Python 3**
*   **Flask:** Microframework web para o backend.
*   **Tkinter:** (Opcional, para a GUI de seleção de pasta) Para a interface gráfica de seleção de diretório.
*   **HTML5, CSS3 (Bootstrap 5), JavaScript:** Para o frontend.
*   **Werkzeug:** Para utilitários WSGI, incluindo `secure_filename`.

## Pré-requisitos

*   Python 3.x
*   Pip (gerenciador de pacotes Python)

## Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-seu-repositorio.git](https://github.com/rafaelmarinatoassis/flask-lan-file-sharer.git)
    cd nome-do-seu-repositorio
    ```

2.  **(Opcional, mas recomendado) Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Flask Werkzeug
    ```
    *(Nota: Tkinter geralmente já vem com a instalação padrão do Python, mas se não, pode ser necessário instalá-lo separadamente dependendo do seu sistema operacional e como o Python foi instalado.)*

4.  **Execute o servidor:**

    *   **Com seleção de pasta via GUI (padrão se nenhum argumento for fornecido):**
        ```bash
        python app.py
        ```
        Uma caixa de diálogo aparecerá para você selecionar a pasta a ser compartilhada.

    *   **Especificando a pasta via linha de comando:**
        ```bash
        python app.py --folder /caminho/para/sua/pasta
        ```
        ou
        ```bash
        python app.py -f "C:\Caminho\Para\Sua\Pasta"
        ```

5.  **Acesse a aplicação:**
    Após iniciar, o console mostrará os endereços para acesso:
    *   De outros dispositivos na mesma rede: `http://<SEU_IP_LOCAL>:<PORTA>` (ex: `http://192.168.1.10:5000`)
    *   Localmente: `http://127.0.0.1:5000`

    A porta padrão é `5000`.

## Atenção

⚠️ **A funcionalidade de apagar arquivos está ATIVA por padrão.** Qualquer pessoa com acesso à interface web poderá apagar arquivos permanentemente da pasta compartilhada. Utilize esta ferramenta com extrema cautela e apenas em redes 100% confiáveis e por sua conta e risco.

## Como Contribuir (Opcional)

Contribuições são bem-vindas! Se você tem ideias para melhorias ou encontrou algum bug:

1.  Faça um Fork do projeto.
2.  Crie uma Branch para sua feature (`git checkout -b feature/NovaFuncionalidade`).
3.  Faça o Commit de suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`).
4.  Faça o Push para a Branch (`git push origin feature/NovaFuncionalidade`).
5.  Abra um Pull Request.

## Licença (Opcional)

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
*(Se você não adicionar um arquivo LICENSE, esta seção pode ser omitida ou você pode escolher outra licença.)*

---

Autor: Rafael Marinato Assis / github.com/rafaelmarinatoassis
