from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Profissional(UserMixin, db.Model):
    __tablename__ = "profissional"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)

    avaliacoes = db.relationship(
        "Avaliacao",
        back_populates="profissional"
    )

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return f"<Profissional {self.nome}>"