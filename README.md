# Dashboard de Análise Estatística de E-commerce

Aplicação web desenvolvida com Dash para apresentar os sete gráficos do notebook de análise de e-commerce.

## Arquivos

- `app.py`: aplicação Dash e construção dos gráficos.
- `ecommerce_estatistica.csv`: base de dados utilizada pela aplicação.
- `analise_ecommerce_estatistica.ipynb`: notebook original com a análise exploratória.
- `requirements.txt`: bibliotecas necessárias.
- `assets/style.css`: estilos visuais da aplicação.

## Como executar localmente

1. Instale o Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. (Opcional, recomendado) Crie e ative um ambiente virtual:

   **Windows**
   ```bash
   python -m venv venv
   venv\\Scripts\\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

5. Inicie a aplicação:

   ```bash
   python app.py
   ```

6. Abra no navegador: http://127.0.0.1:8050

## Publicação

O GitHub armazena o código. Para gerar um link público em que qualquer pessoa possa abrir o dashboard, publique a aplicação em um serviço de hospedagem compatível com Python/Dash (por exemplo, Render). Consulte a documentação do serviço para configurar o comando de inicialização `gunicorn app:server`; para isso, adicione `gunicorn` ao `requirements.txt` e acrescente `server = app.server` em `app.py`.
