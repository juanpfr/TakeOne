
# TakeOne 🎬

**TakeOne** é um sistema web desenvolvido em Flask para gerenciamento de reservas de estúdios de criação (foto e vídeo), com autenticação de usuários e conexão a banco de dados SQL Server.

## 🚀 Tecnologias Utilizadas

- Python 3.x  
- Flask  
- SQL Server (via pyodbc)  
- Jinja2 (Templates)  
- dotenv (Variáveis de ambiente)

## ⚙️ Como Executar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/juanpfr/TakeOne.git
cd TakeOne
```

### 2. Crie e ative um ambiente virtual (opcional mas recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente  
Crie um arquivo `.env` na raiz com as seguintes chaves (exemplo):

```env
SECRET_KEY=sua_chave_secreta
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=TakeOneDB
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

### 5. Execute a aplicação
```bash
python app.py
```
Acesse via [http://localhost:5000](http://localhost:5000)

## 📁 Estrutura do Projeto
```bash
TakeOne/
├── app.py               # Arquivo principal da aplicação Flask
├── .env                 # Configurações de ambiente (não versionado)
├── requirements.txt     # Dependências do projeto
├── templates/           # Templates HTML Jinja2 (não listado aqui)
├── static/              # Arquivos estáticos (CSS, JS, imagens)
├── docs/                # Arquivos de documentação do projeto
```

## 👥 Autores

[@juanpfr](https://github.com/juanpfr)
[@br7trindade](https://github.com/br7trindade)
[@alissongaldino22](https://github.com/alissongaldino22)
[@isabellaoliiveiiraa](https://github.com/isabellaoliiveiiraa)

© 2025 - Projeto acadêmico para fins de aprendizado.
