from flask import Flask, render_template
import pyodbc
from dotenv import load_dotenv

load_dotenv()

# Criando instância da aplicação flask
app = Flask(__name__)

# String de conexão com o SQL SERVER
conn_str = ()

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Iniciar o servidor Flask em modo debug
if __name__ == '__main__':
    app.run(debug=True)