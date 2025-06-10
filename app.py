from flask import Flask, request, render_template
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# Criando instância da aplicação flask
app = Flask(__name__)

# String de conexão com o SQL SERVER
conn_str = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')}"
)

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para tratar os dados enviados pelo formulário (método POST)
@app.route('/enviar', methods=['POST'])
def enviar():
    # Captura os dados do formulário HTML enviados pelo usuário
    nome = request.form['nome']
    sobrenome = request.form['sobrenome']
    email = request.form['email']
    mensagem = request.form['mensagem']



    try:
        # Abre a conexão com o banco usando a string de conexão definida
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Executa o comando SQL para inserir os dados na tabela Contatos
        # Os "?" são usados como parâmetros para prevenir SQL Injection
        cursor.execute("INSERT INTO tbl_contato (nome, sobrenome, email, mensagem) VALUES (?, ?, ?, ?)", (nome, sobrenome, email, mensagem))

        # Salva as mudanças no banco de dados
        conn.commit()

        # Fecha o cursor e a conexão
        cursor.close()
        conn.close()

        # Mensagem de sucesso com link para voltar ao formulário
        return f"<h2>Dados salvos com sucesso!</h2><a href='/'>Voltar</a>"

    except Exception as e:
        # Em caso de erro, exibe o erro no navegador
        return f"<h2>Erro ao salvar no banco:</h2><pre>{e}</pre>"

# Iniciar o servidor Flask em modo debug
if __name__ == '__main__':
    app.run(debug=True)