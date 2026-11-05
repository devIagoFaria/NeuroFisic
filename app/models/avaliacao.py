from app import db


class Avaliacao(db.Model):
    __tablename__ = "avaliacao"

    id = db.Column(db.Integer, primary_key=True)

    data = db.Column(db.Date, nullable=False)
    queixa_atual = db.Column(db.Text)
    horas_sono_anterior = db.Column(db.Float)
    observacao = db.Column(db.Text)

    profissional_id = db.Column(
        db.Integer,
        db.ForeignKey("profissional.id"),
        nullable=False
    )

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("paciente.id"),
        nullable=False
    )

    profissional = db.relationship(
        "Profissional",
        back_populates="avaliacoes"
    )

    paciente = db.relationship(
        "Paciente",
        back_populates="avaliacoes"
    )

    ravlt = db.relationship(
        "RAVLT",
        back_populates="avaliacao",
        uselist=False,
        cascade="all, delete-orphan"
    )

    tmt = db.relationship(
        "TMT",
        back_populates="avaliacao",
        uselist=False,
        cascade="all, delete-orphan"
    )

    fluencia_verbal = db.relationship(
        "FluenciaVerbal",
        back_populates="avaliacao",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Avaliacao {self.id}>"