from app import db


class RAVLT(db.Model):
    __tablename__ = "ravlt"

    id = db.Column(db.Integer, primary_key=True)

    avaliacao_id = db.Column(
        db.Integer,
        db.ForeignKey("avaliacao.id"),
        nullable=False,
        unique=True
    )

    observacao = db.Column(db.Text)

    quantidade_a1 = db.Column(db.Integer)
    quantidade_a2 = db.Column(db.Integer)
    quantidade_a3 = db.Column(db.Integer)
    quantidade_a4 = db.Column(db.Integer)
    quantidade_a5 = db.Column(db.Integer)

    quantidade_lista_b = db.Column(db.Integer)

    quantidade_a6 = db.Column(db.Integer)
    quantidade_a7 = db.Column(db.Integer)

    reconhecimento = db.Column(db.Integer)

    avaliacao = db.relationship(
        "Avaliacao",
        back_populates="ravlt"
    )

    def __repr__(self):
        return f"<RAVLT {self.id}>"