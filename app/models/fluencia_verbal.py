from app import db


class FluenciaVerbal(db.Model):
    __tablename__ = "fluencia_verbal"

    id = db.Column(db.Integer, primary_key=True)

    avaliacao_id = db.Column(
        db.Integer,
        db.ForeignKey("avaliacao.id"),
        nullable=False,
        unique=True
    )

    total_palavras = db.Column(db.Integer)
    respostas_validas = db.Column(db.Integer)
    repeticoes = db.Column(db.Integer)

    palavras_0_15 = db.Column(db.Integer)
    palavras_16_30 = db.Column(db.Integer)
    palavras_31_45 = db.Column(db.Integer)
    palavras_46_60 = db.Column(db.Integer)

    avaliacao = db.relationship(
        "Avaliacao",
        back_populates="fluencia_verbal"
    )

    def __repr__(self):
        return f"<FluenciaVerbal {self.id}>"