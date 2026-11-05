from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.models.paciente import Paciente


pacientes_bp = Blueprint(
    "pacientes",
    __name__,
    url_prefix="/pacientes"
)


@pacientes_bp.route("/")
@login_required
def listar():

    pacientes = db.session.scalars(
        db.select(Paciente).order_by(Paciente.nome)
    ).all()

    return render_template(
        "pacientes/listar.html",
        pacientes=pacientes
    )


@pacientes_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():

    if request.method == "POST":

        nome = request.form.get("nome")
        data_nascimento = request.form.get("data_nascimento")
        sexo = request.form.get("sexo")
        estado_civil = request.form.get("estado_civil")
        anos_estudo = request.form.get("anos_estudo")
        profissao = request.form.get("profissao")
        ocupacao_atual = request.form.get("ocupacao_atual")

        paciente = Paciente(
            nome=nome,
            data_nascimento=datetime.strptime(
                data_nascimento,
                "%Y-%m-%d"
            ).date(),
            sexo=sexo,
            estado_civil=estado_civil,
            anos_estudo=int(anos_estudo) if anos_estudo else None,
            profissao=profissao,
            ocupacao_atual=ocupacao_atual
        )

        db.session.add(paciente)
        db.session.commit()

        flash("Paciente cadastrado com sucesso.", "sucesso")

        return redirect(url_for("pacientes.listar"))

    return render_template("pacientes/formulario.html", paciente=None)


@pacientes_bp.route("/<int:paciente_id>")
@login_required
def visualizar(paciente_id):

    paciente = db.get_or_404(Paciente, paciente_id)

    return render_template(
        "pacientes/visualizar.html",
        paciente=paciente
    )
    
@pacientes_bp.route("/<int:paciente_id>/editar", methods=["GET", "POST"])
@login_required
def editar(paciente_id):

    paciente = db.get_or_404(Paciente, paciente_id)

    if request.method == "POST":

        paciente.nome = request.form.get("nome")

        data_nascimento = request.form.get("data_nascimento")

        paciente.data_nascimento = datetime.strptime(
            data_nascimento,
            "%Y-%m-%d"
        ).date()

        paciente.sexo = request.form.get("sexo")
        paciente.estado_civil = request.form.get("estado_civil")

        anos_estudo = request.form.get("anos_estudo")

        paciente.anos_estudo = (
            int(anos_estudo)
            if anos_estudo
            else None
        )

        paciente.profissao = request.form.get("profissao")
        paciente.ocupacao_atual = request.form.get("ocupacao_atual")

        db.session.commit()

        flash(
            "Paciente atualizado com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "pacientes.visualizar",
                paciente_id=paciente.id
            )
        )

    return render_template(
        "pacientes/formulario.html",
        paciente=paciente
    )
    
@pacientes_bp.route("/<int:paciente_id>/excluir", methods=["POST"])
@login_required
def excluir(paciente_id):

    paciente = db.get_or_404(Paciente, paciente_id)

    # Não permite excluir paciente que possui avaliações
    if paciente.avaliacoes:
        flash(
            "Não é possível excluir este paciente porque ele possui avaliações registradas.",
            "erro"
        )

        return redirect(
            url_for(
                "pacientes.visualizar",
                paciente_id=paciente.id
            )
        )

    nome_paciente = paciente.nome

    db.session.delete(paciente)
    db.session.commit()

    flash(
        f"Paciente {nome_paciente} excluído com sucesso.",
        "sucesso"
    )

    return redirect(
        url_for("pacientes.listar")
    )