
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from app import db
from app.models.avaliacao import Avaliacao
from app.models.tmt import TMT


tmt_bp = Blueprint(
    "tmt",
    __name__,
    url_prefix="/avaliacoes"
)


@tmt_bp.route(
    "/<int:avaliacao_id>/tmt",
    methods=["GET", "POST"]
)
@login_required
def formulario(avaliacao_id):

    avaliacao = db.get_or_404(Avaliacao, avaliacao_id)

    # Verifica se a avaliação pertence ao profissional.
    if avaliacao.profissional_id != current_user.id:
        abort(404)

    tmt = avaliacao.tmt

    if request.method == "POST":

        dados = {}

        try:
            # Tempos em segundos
            for campo in ["tempo_a", "tempo_b"]:

                valor = request.form.get(campo, "").strip()

                if not valor:
                    dados[campo] = None
                    continue

                # Aceita ponto ou vírgula decimal
                numero = float(valor.replace(",", "."))

                if not 0 < numero <= 36000:
                    raise ValueError()

                dados[campo] = numero

            # Quantidade de erros
            for campo in ["erros_a", "erros_b"]:

                valor = request.form.get(campo, "").strip()

                if not valor:
                    dados[campo] = None
                    continue

                numero = int(valor)

                if numero < 0:
                    raise ValueError()

                dados[campo] = numero

        except (ValueError, OverflowError):

            flash(
                "Informe tempos maiores que zero e "
                "quantidades de erros inteiras não negativas.",
                "erro"
            )

            return render_template(
                "avaliacoes/tmt.html",
                avaliacao=avaliacao,
                tmt=tmt
            ), 400

        # Cria um registro se ainda não existir
        if tmt is None:

            tmt = TMT(
                avaliacao_id=avaliacao.id
            )

            db.session.add(tmt)

        # Preenche ou atualiza os campos
        for campo, valor in dados.items():
            setattr(tmt, campo, valor)

        db.session.commit()

        flash(
            "Resultados do TMT salvos com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )

    return render_template(
        "avaliacoes/tmt.html",
        avaliacao=avaliacao,
        tmt=tmt
    )
