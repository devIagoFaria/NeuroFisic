from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from flask import abort

from app import db
from app.models.avaliacao import Avaliacao
from app.models.paciente import Paciente


avaliacoes_bp = Blueprint(
    "avaliacoes",
    __name__,
    url_prefix="/avaliacoes"
)


@avaliacoes_bp.route("/")
@login_required
def listar():

    avaliacoes = db.session.scalars(
        db.select(Avaliacao)
        .where(Avaliacao.profissional_id == current_user.id)
        .order_by(Avaliacao.data.desc())
    ).all()

    return render_template(
        "avaliacoes/listar.html",
        avaliacoes=avaliacoes
    )


@avaliacoes_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():

    pacientes = db.session.scalars(
        db.select(Paciente)
        .order_by(Paciente.nome)
    ).all()

    if request.method == "POST":

        paciente_id = request.form.get("paciente_id")
        data = request.form.get("data")
        queixa_atual = request.form.get("queixa_atual")
        horas_sono_anterior = request.form.get("horas_sono_anterior")
        observacao = request.form.get("observacao")

        paciente = db.get_or_404(
            Paciente,
            int(paciente_id)
        )

        avaliacao = Avaliacao(
            data=datetime.strptime(
                data,
                "%Y-%m-%d"
            ).date(),

            queixa_atual=queixa_atual,

            horas_sono_anterior=(
                float(horas_sono_anterior)
                if horas_sono_anterior
                else None
            ),

            observacao=observacao,

            profissional_id=current_user.id,

            paciente_id=paciente.id
        )

        db.session.add(avaliacao)
        db.session.commit()

        flash(
            "Avaliação criada com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )
        
    paciente_selecionado_id = request.args.get(
        "paciente_id",
        type=int
    )

    return render_template(
        "avaliacoes/formulario.html",
        pacientes=pacientes,
        paciente_selecionado_id=paciente_selecionado_id
    )


@avaliacoes_bp.route("/<int:avaliacao_id>")
@login_required
def visualizar(avaliacao_id):

    avaliacao = db.session.scalar(
        db.select(Avaliacao)
        .options(
            joinedload(Avaliacao.paciente),
            joinedload(Avaliacao.profissional),
            joinedload(Avaliacao.ravlt),
            joinedload(Avaliacao.tmt),
            joinedload(Avaliacao.fluencia_verbal)
        )
        .where(
            Avaliacao.id == avaliacao_id,
            Avaliacao.profissional_id == current_user.id
        )
    )

    if avaliacao is None:
        abort(404)

    total_testes = sum([
        avaliacao.ravlt is not None,
        avaliacao.tmt is not None,
        avaliacao.fluencia_verbal is not None
    ])

    return render_template(
        "avaliacoes/visualizar.html",
        avaliacao=avaliacao,
        total_testes=total_testes
    )


@avaliacoes_bp.route(
    "/<int:avaliacao_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(avaliacao_id):

    avaliacao = db.get_or_404(
        Avaliacao,
        avaliacao_id
    )

    # Somente o profissional responsável pode editar.
    if avaliacao.profissional_id != current_user.id:
        abort(404)

    if request.method == "POST":

        data = request.form.get("data", "").strip()
        queixa_atual = request.form.get(
            "queixa_atual", ""
        ).strip()

        horas_sono_anterior = request.form.get(
            "horas_sono_anterior", ""
        ).strip()

        observacao = request.form.get(
            "observacao", ""
        ).strip()

        try:

            if not data:
                raise ValueError(
                    "Informe a data da avaliação."
                )

            data_convertida = datetime.strptime(
                data,
                "%Y-%m-%d"
            ).date()

            horas_convertidas = None

            if horas_sono_anterior:

                horas_convertidas = float(
                    horas_sono_anterior.replace(",", ".")
                )

                if not 0 <= horas_convertidas <= 24:
                    raise ValueError(
                        "As horas de sono devem estar "
                        "entre 0 e 24."
                    )

        except ValueError as erro:

            mensagem = str(erro)

            if "does not match format" in mensagem:
                mensagem = "Informe uma data válida."

            flash(mensagem, "erro")

            return render_template(
                "avaliacoes/formulario.html",
                avaliacao=avaliacao,
                pacientes=None
            ), 400

        # Atualiza somente os dados gerais.
        avaliacao.data = data_convertida
        avaliacao.queixa_atual = queixa_atual
        avaliacao.horas_sono_anterior = horas_convertidas
        avaliacao.observacao = observacao

        db.session.commit()

        flash(
            "Avaliação atualizada com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )

    return render_template(
        "avaliacoes/formulario.html",
        avaliacao=avaliacao,
        pacientes=None
    )


@avaliacoes_bp.route(
    "/<int:avaliacao_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(avaliacao_id):

    avaliacao = db.get_or_404(
        Avaliacao,
        avaliacao_id
    )

    # Verifica se pertence ao profissional logado
    if avaliacao.profissional_id != current_user.id:
        abort(404)

    # Confirmação enviada pelo formulário
    confirmacao = request.form.get("confirmacao")

    if confirmacao != "EXCLUIR":
        flash(
            "A exclusão não foi confirmada.",
            "erro"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )

    paciente_nome = avaliacao.paciente.nome

    # Exclui avaliação e resultados associados
    db.session.delete(avaliacao)
    db.session.commit()

    flash(
        f"Avaliação de {paciente_nome} excluída com sucesso.",
        "sucesso"
    )

    return redirect(
        url_for("avaliacoes.listar")
    )
