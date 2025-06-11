from flask import Flask, request, render_template, redirect, url_for, session, flash
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para sessões (login)

# Conexão com o SQL Server
conn_str = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    "Encrypt=no;"
)

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Verifica se o usuário existe e está ATIVO
            cursor.execute("""
                SELECT id_cliente, nome, status FROM tbl_cliente 
                WHERE email = ? AND senha = ?
            """, (email, senha))
            
            cliente = cursor.fetchone()

            cursor.close()
            conn.close()

            if cliente:
                if cliente.status == 'ATIVO':
                    session['id_cliente'] = cliente.id_cliente
                    session['nome'] = cliente.nome
                    return redirect(url_for('dashboard'))
                else:
                    flash('Conta inativa ou desativada.', 'erro')
            else:
                flash('Email ou senha inválidos.', 'erro')

        except Exception as e:
            return f"<h2>Erro ao acessar o banco de dados:</h2><pre>{e}</pre>"

    return render_template('login.html')

# Página protegida
@app.route('/dashboard')
def dashboard():
    if 'id_cliente' in session:
        return f"<h2>Bem-vindo(a), {session['nome']}!</h2><a href='/logout'>Sair</a>"
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Formulário de contato
@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    sobrenome = request.form['sobrenome']
    email = request.form['email']
    mensagem = request.form['mensagem']

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tbl_contato (nome, sobrenome, email, mensagem) VALUES (?, ?, ?, ?)",
                       (nome, sobrenome, email, mensagem))
        conn.commit()
        cursor.close()
        conn.close()
        return f"<h2>Dados salvos com sucesso!</h2><a href='/'>Voltar</a>"
    except Exception as e:
        return f"<h2>Erro ao salvar no banco:</h2><pre>{e}</pre>"

# Formulário de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    sobrenome = request.form['sobrenome']
    telefone = request.form['telefone']
    email = request.form['email']
    senha = request.form['senha']
    rg = request.form['rg']
    cpf = request.form['cpf']
    data_nascimento = request.form['data_nascimento']

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tbl_cliente 
            (nome, sobrenome, telefone, email, senha, rg, cpf, data_nascimento) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, sobrenome, telefone, email, senha, rg, cpf, data_nascimento))
        conn.commit()
        cursor.close()
        conn.close()
        return f"<h2>Cadastro realizado com sucesso!</h2><a href='/'>Voltar</a>"
    except Exception as e:
        return f"<h2>Erro ao salvar no banco:</h2><pre>{e}</pre>"

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
