from flask import Flask, request, render_template, redirect, url_for, session, flash
import pyodbc
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = f"SERVER={os.getenv('SECRET_KEY')};"  # Necessária para sessões (login)

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

@app.route('/meus_agendamentos')
def meus_agendamentos():
    if 'id_cliente' not in session:
        flash("Faça login para ver os agendamentos.", "erro")
        return redirect(url_for('login'))
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id_agendamento,
                a.data_hora_inicio,
                a.status,

                ts.nome AS tipo_servico,
                ts.tempo_estimado_minutos,
                c.nome AS categoria,

                e.nome AS espaco,

                eq.nome AS equipamento,
                eq.descricao AS equipamento_descricao,
                eq.em_manutencao,

                f.nome AS funcionario,
                f.funcao,
                f.especialidade
            FROM tbl_agendamento a
            JOIN tbl_tipo_servico ts ON a.id_tipo_servico = ts.id_tipo_servico
            JOIN tbl_categoria c ON ts.id_categoria = c.id_categoria
            JOIN tbl_espaco e ON a.id_espaco = e.id_espaco

            LEFT JOIN tbl_agendamento_equipamento ae ON a.id_agendamento = ae.id_agendamento
            LEFT JOIN tbl_equipamento eq ON ae.id_equipamento = eq.id_equipamento

            LEFT JOIN tbl_agendamento_funcionario af ON a.id_agendamento = af.id_agendamento
            LEFT JOIN tbl_funcionario f ON af.id_funcionario = f.id_funcionario

            WHERE a.id_cliente = ?
            ORDER BY a.data_hora_inicio DESC;
        """, (session['id_cliente'],))
        
        colunas = [col[0] for col in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar agendamentos:</h2><pre>{e}</pre>"

    return render_template('agendamentos.html', agendamentos=resultados)

# Página de meu perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'id_cliente' not in session:
        flash("Faça login para acessar seu perfil.", "erro")
        return redirect(url_for('login'))

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        if request.method == 'POST':
            nome = request.form['nome']
            descricao = request.form['descricao']
            cursor.execute("""
                INSERT INTO tbl_equipamento_cliente (id_cliente, nome, descricao)
                VALUES (?, ?, ?);
            """, (session['id_cliente'], nome, descricao))
            conn.commit()
            flash("Equipamento adicionado com sucesso!", "sucesso")

        # Dados do cliente
        cursor.execute("""
            SELECT nome, sobrenome, telefone, email
            FROM tbl_cliente
            WHERE id_cliente = ?;
        """, (session['id_cliente'],))
        cliente = cursor.fetchone()

        # Equipamentos do cliente
        cursor.execute("""
            SELECT id_equipamento_cliente, nome, descricao
            FROM tbl_equipamento_cliente
            WHERE id_cliente = ?;
        """, (session['id_cliente'],))
        equipamentos = cursor.fetchall()

        conn.close()

    except Exception as e:
        return f"<h2>Erro ao carregar perfil:</h2><pre>{e}</pre>"

    return render_template("perfil.html", cliente=cliente, equipamentos=equipamentos)

# excluir e editar
@app.route('/excluir_equipamento/<int:id>', methods=['POST'])
def excluir_equipamento(id):
    if 'id_cliente' not in session:
        return redirect(url_for('login'))

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM tbl_equipamento_cliente
            WHERE id_equipamento_cliente = ? AND id_cliente = ?;
        """, (id, session['id_cliente']))
        conn.commit()
        conn.close()
        flash("Equipamento excluído com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao excluir equipamento: {e}", "erro")

    return redirect(url_for('perfil'))


@app.route('/editar_equipamento/<int:id>', methods=['GET', 'POST'])
def editar_equipamento(id):
    if 'id_cliente' not in session:
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        cursor.execute("""
            UPDATE tbl_equipamento_cliente
            SET nome = ?, descricao = ?
            WHERE id_equipamento_cliente = ? AND id_cliente = ?;
        """, (nome, descricao, id, session['id_cliente']))
        conn.commit()
        conn.close()
        flash("Equipamento atualizado com sucesso!", "sucesso")
        return redirect(url_for('perfil'))

    cursor.execute("""
        SELECT nome, descricao
        FROM tbl_equipamento_cliente
        WHERE id_equipamento_cliente = ? AND id_cliente = ?;
    """, (id, session['id_cliente']))
    equipamento = cursor.fetchone()
    conn.close()

    return render_template("editar_equipamento.html", equipamento=equipamento, id=id)

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
                    return redirect(url_for('index'))
                else:
                    flash('Conta inativa ou desativada.', 'erro')
            else:
                flash('Email ou senha inválidos.', 'erro')

        except Exception as e:
            return f"<h2>Erro ao acessar o banco de dados:</h2><pre>{e}</pre>"

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
        flash('Contato enviado com sucesso!')
    except Exception as e:
        flash(f'Erro ao enviar o contato: {e}')

    return redirect(url_for('index'))

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
        flash('Conta criada com sucesso!')
    except Exception as e:
        flash(f'Erro criar a conta: {e}')

    return redirect(url_for('index'))


# Início do fluxo de agendamento (após login obrigatório)
@app.route('/agendar', methods=['GET', 'POST'])
def agendar_datahora():
    if 'id_cliente' not in session:
        flash("Faça login para agendar.", "erro")
        return redirect(url_for('login'))

    if request.method == 'POST':
        session['data'] = request.form['data']
        session['hora'] = request.form['hora']
        return redirect(url_for('agendar_espaco'))

    return render_template('agendar_datahora.html')

@app.route('/agendar/espaco', methods=['GET', 'POST'])
def agendar_espaco():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT id_espaco, nome FROM tbl_espaco")
        espacos = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar espaços:</h2><pre>{e}</pre>"

    if request.method == 'POST':
        session['espaco_id'] = request.form['espaco_id']
        return redirect(url_for('agendar_servico'))

    return render_template('agendar_espaco.html', espacos=espacos)

@app.route('/agendar/servico', methods=['GET', 'POST'])
def agendar_servico():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT id_tipo_servico, nome FROM tbl_tipo_servico")
        servicos = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar espaços:</h2><pre>{e}</pre>"

    if request.method == 'POST':
        session['servico_id'] = request.form['servico_id']
        return redirect(url_for('agendar_funcionarios'))

    return render_template('agendar_servico.html', servicos=servicos)

@app.route('/agendar/funcionarios', methods=['GET', 'POST'])
def agendar_funcionarios():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT id_funcionario, nome FROM tbl_funcionario")
        funcionarios = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar funcionários:</h2><pre>{e}</pre>"

    if request.method == 'POST':
        session['funcionarios_ids'] = request.form.getlist('funcionarios')
        return redirect(url_for('agendar_equipamentos'))

    return render_template('agendar_funcionarios.html', funcionarios=funcionarios)

@app.route('/agendar/equipamentos', methods=['GET', 'POST'])
def agendar_equipamentos():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT id_equipamento, nome FROM tbl_equipamento")
        equipamentos = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar equipamentos:</h2><pre>{e}</pre>"

    if request.method == 'POST':
        session['equipamentos_ids'] = request.form.getlist('equipamentos')
        return redirect(url_for('confirmar_agendamento'))

    return render_template('agendar_equipamentos.html', equipamentos=equipamentos)

@app.route('/agendar/confirmar', methods=['GET', 'POST'])
def confirmar_agendamento():
    if request.method == 'POST':
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Junta data e hora da sessão em um único datetime
            data_str = session['data']        # ex: '2025-06-12'
            hora_str = session['hora']        # ex: '14:30'
            data_hora_str = f"{data_str} {hora_str}:00"  # '2025-06-12 14:30:00'
            data_hora_inicio = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M:%S')

            # Insere agendamento com datetime combinado
            cursor.execute("""
                INSERT INTO tbl_agendamento (id_cliente, id_tipo_servico, id_espaco, data_hora_inicio)
                VALUES (?, ?, ?, ?)
            """, (
                session['id_cliente'],
                session['servico_id'],
                session['espaco_id'],
                data_hora_inicio
            ))
            conn.commit()

            # ID do agendamento criado
            cursor.execute("SELECT id_agendamento FROM tbl_agendamento")
            id_agendamento = cursor.fetchone()[0]

            # Funcionários
            for funcionario_id in session.get('funcionarios_ids', []):
                cursor.execute("""
                    INSERT INTO tbl_agendamento_funcionario (id_agendamento, id_funcionario)
                    VALUES (?, ?)
                """, (id_agendamento, funcionario_id))

            # Equipamentos
            for equipamento_id in session.get('equipamentos_ids', []):
                cursor.execute("""
                    INSERT INTO tbl_agendamento_equipamento (id_agendamento, id_equipamento)
                    VALUES (?, ?)
                """, (id_agendamento, equipamento_id))

            conn.commit()
            cursor.close()
            conn.close()

            # Limpa sessões temporárias do agendamento
            session.pop('data', None)
            session.pop('hora', None)
            session.pop('espaco_id', None)
            session.pop('funcionarios_ids', None)
            session.pop('equipamentos_ids', None)

            flash("Agendamento realizado com sucesso!", "sucesso")
            return redirect(url_for('index'))

        except Exception as e:
            return f"<h2>Erro ao confirmar agendamento:</h2><pre>{e}</pre>"

    # Recarregar nomes para exibir na confirmação
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("SELECT nome FROM tbl_funcionario WHERE id_funcionario IN ({})".format(
            ",".join("?" * len(session['funcionarios_ids']))
        ), session['funcionarios_ids'])
        funcionarios = [row.nome for row in cursor.fetchall()]

        cursor.execute("SELECT nome FROM tbl_equipamento WHERE id_equipamento IN ({})".format(
            ",".join("?" * len(session['equipamentos_ids']))
        ), session['equipamentos_ids'])
        equipamentos = [row.nome for row in cursor.fetchall()]

        cursor.close()
        conn.close()
    except Exception as e:
        return f"<h2>Erro ao carregar dados de confirmação:</h2><pre>{e}</pre>"

    return render_template('confirmar_agendamento.html',
                           funcionarios=funcionarios,
                           equipamentos=equipamentos)

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)