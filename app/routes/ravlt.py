
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, abort
)
from flask_login import login_required, current_user

from app import db
from app.models.avaliacao import Avaliacao
from app.models.ravlt import RAVLT


ravlt_bp = Blueprint(
    "ravlt",
    __name__,
    url_prefix="/avaliacoes"
)


def buscar_avaliacao(avaliacao_id):
    avaliacao = db.get_or_404(Avaliacao, avaliacao_id)

    # Apenas o profissional responsável pode acessar.
    if avaliacao.profissional_id != current_user.id:
        abort(404)

    return avaliacao


@ravlt_bp.route(
    "/<int:avaliacao_id>/ravlt",
    methods=["GET", "POST"]
)
@login_required
def formulario(avaliacao_id):

    avaliacao = buscar_avaliacao(avaliacao_id)

    ravlt = avaliacao.ravlt

    if request.method == "POST":

        campos = [
            "quantidade_a1",
            "quantidade_a2",
            "quantidade_a3",
            "quantidade_a4",
            "quantidade_a5",
            "quantidade_lista_b",
            "quantidade_a6",
            "quantidade_a7",
            "reconhecimento"
        ]

        dados = {}

        try:
            for campo in campos:
                valor = request.form.get(campo, "").strip()

                if not valor:
                    dados[campo] = None
                    continue

                numero = int(valor)

                if numero < 0:
                    raise ValueError()

                dados[campo] = numero

        except ValueError:
            flash(
                "Informe números inteiros maiores ou iguais a zero.",
                "erro"
            )

            return render_template(
                "avaliacoes/ravlt.html",
                avaliacao=avaliacao,
                ravlt=ravlt
            ), 400

        if ravlt is None:
            ravlt = RAVLT(avaliacao_id=avaliacao.id)
            db.session.add(ravlt)

        for campo, valor in dados.items():
            setattr(ravlt, campo, valor)

        ravlt.observacao = (
            request.form.get("observacao", "").strip()
        )

        db.session.commit()

        flash(
            "Resultados do RAVLT salvos com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )

    return render_template(
        "avaliacoes/ravlt.html",
        avaliacao=avaliacao,
        ravlt=ravlt
    )