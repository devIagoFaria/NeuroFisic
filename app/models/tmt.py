from app import db


class TMT(db.Model):
    __tablename__ = "tmt"

    id = db.Column(db.Integer, primary_key=True)

    avaliacao_id = db.Column(
        db.Integer,
        db.ForeignKey("avaliacao.id"),
        nullable=False,
        unique=True
    )

    tempo_a = db.Column(db.Float)
    erros_a = db.Column(db.Integer)

    tempo_b = db.Column(db.Float)
    erros_b = db.Column(db.Integer)

    avaliacao = db.relationship(
        "Avaliacao",
        back_populates="tmt"
    )

    def __repr__(self):
        return f"<TMT {self.id}>"