from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Cliente(db.Model, UserMixin):
    __tablename__ = 'tbl_cliente'

    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    sobrenome = db.Column(db.String(100))
    telefone = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(14))
    data_nascimento = db.Column(db.Date)
    data_cadastro = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ATIVO')

    def get_id(self):
        return str(self.id_cliente)


