from app import db


class Paciente(db.Model):
    __tablename__ = "paciente"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(30))
    estado_civil = db.Column(db.String(50))
    anos_estudo = db.Column(db.Integer)
    profissao = db.Column(db.String(100))
    ocupacao_atual = db.Column(db.String(100))

    avaliacoes = db.relationship(
        "Avaliacao",
        back_populates="paciente"
    )

    def __repr__(self):
        return f"<Paciente {self.nome}>"