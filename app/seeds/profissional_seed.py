from app import db
from app.models.profissional import Profissional


def criar_profissional_padrao():

    email = "admin@neuropsico.com"

    profissional_existente = db.session.scalar(
        db.select(Profissional).where(
            Profissional.email == email
        )
    )

    if profissional_existente:
        return

    profissional = Profissional(
        nome="Administrador",
        email=email
    )

    profissional.definir_senha("123456")

    db.session.add(profissional)
    db.session.commit()

    print("Usuário administrador padrão criado.")
    