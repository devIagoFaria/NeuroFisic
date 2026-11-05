from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.profissional import Profissional
from app.models.paciente import Paciente
from app.models.avaliacao import Avaliacao
from app.services.analise_service import AnaliseService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        profissional = db.session.scalar(
            db.select(Profissional).where(
                Profissional.email == email
            )
        )

        if profissional and profissional.verificar_senha(senha):
            login_user(profissional)

            return redirect(url_for("auth.dashboard"))

        flash("E-mail ou senha inválidos.", "erro")

    return render_template("login.html")


@auth_bp.route("/dashboard")
@login_required
def dashboard():

    # Pacientes distintos com avaliações do profissional
    pacientes_com_avaliacao = db.session.scalar(
        db.select(
            db.func.count(
                db.func.distinct(Avaliacao.paciente_id)
            )
        ).where(
            Avaliacao.profissional_id == current_user.id
        )
    ) or 0

    # Total de avaliações do profissional
    total_avaliacoes = db.session.scalar(
        db.select(db.func.count(Avaliacao.id))
        .where(
            Avaliacao.profissional_id == current_user.id
        )
    ) or 0

    # Últimas cinco avaliações
    avaliacoes_recentes = db.session.scalars(
        db.select(Avaliacao)
        .where(
            Avaliacao.profissional_id == current_user.id
        )
        .order_by(
            Avaliacao.data.desc(),
            Avaliacao.id.desc()
        )
        .limit(5)
    ).all()


    df = AnaliseService.preparar_dados(current_user.id)

    indicadores = AnaliseService.calcular_indicadores(df)

    total_analises = indicadores["total_com_tres_testes"]

    return render_template(
        "dashboard.html",
        total_pacientes=pacientes_com_avaliacao,
        total_avaliacoes=total_avaliacoes,
        avaliacoes_recentes=avaliacoes_recentes
    )


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for("auth.login"))