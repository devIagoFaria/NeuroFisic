
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
from app.models.fluencia_verbal import FluenciaVerbal


fluencia_bp = Blueprint(
    "fluencia",
    __name__,
    url_prefix="/avaliacoes"
)


@fluencia_bp.route(
    "/<int:avaliacao_id>/fluencia-verbal",
    methods=["GET", "POST"]
)
@login_required
def formulario(avaliacao_id):

    avaliacao = db.get_or_404(
        Avaliacao,
        avaliacao_id
    )

    # Somente o profissional responsável
    if avaliacao.profissional_id != current_user.id:
        abort(404)

    fluencia = avaliacao.fluencia_verbal

    if request.method == "POST":

        tipo = request.form.get("tipo", "").strip()
        categoria = request.form.get("categoria", "").strip()

        campos_numericos = [
            "total_palavras",
            "palavras_validas",
            "repeticoes",
            "intrusoes",
            "intervalo_1",
            "intervalo_2",
            "intervalo_3",
            "intervalo_4"
        ]

        dados = {}

        try:

            if tipo not in ["Semântica", "Fonêmica"]:
                raise ValueError(
                    "Selecione o tipo de fluência."
                )

            if not categoria:
                raise ValueError(
                    "Informe a categoria ou letra utilizada."
                )

            for campo in campos_numericos:

                valor = request.form.get(
                    campo, ""
                ).strip()

                if not valor:
                    dados[campo] = None
                    continue

                numero = int(valor)

                if numero < 0:
                    raise ValueError(
                        "Os valores numéricos não podem ser negativos."
                    )

                dados[campo] = numero

            # Os intervalos são opcionais, mas, se
            # informados, precisam ser consistentes.
            intervalos = [
                dados["intervalo_1"],
                dados["intervalo_2"],
                dados["intervalo_3"],
                dados["intervalo_4"]
            ]

            if any(v is not None for v in intervalos):

                if any(v is None for v in intervalos):
                    raise ValueError(
                        "Preencha os quatro intervalos "
                        "ou deixe todos vazios."
                    )

                if dados["total_palavras"] is not None:

                    if sum(intervalos) != dados["total_palavras"]:
                        raise ValueError(
                            "A soma dos intervalos deve ser "
                            "igual ao total de palavras."
                        )

            total = dados["total_palavras"]
            validas = dados["palavras_validas"]
            repeticoes = dados["repeticoes"]
            intrusoes = dados["intrusoes"]

            if total is not None:

                for valor in [validas, repeticoes, intrusoes]:
                    if valor is not None and valor > total:
                        raise ValueError(
                            "Nenhuma contagem pode superar "
                            "o total de palavras."
                        )

                if all(
                    v is not None
                    for v in [validas, repeticoes, intrusoes]
                ):
                    if validas + repeticoes + intrusoes != total:
                        raise ValueError(
                            "O total deve corresponder à soma "
                            "das palavras válidas, repetições "
                            "e intrusões."
                        )

        except ValueError as erro:

            flash(str(erro), "erro")

            return render_template(
                "avaliacoes/fluencia_verbal.html",
                avaliacao=avaliacao,
                fluencia=fluencia
            ), 400

        # Criação ou edição
        if fluencia is None:

            fluencia = FluenciaVerbal(
                avaliacao_id=avaliacao.id
            )

            db.session.add(fluencia)

        fluencia.tipo = tipo
        fluencia.categoria = categoria

        for campo, valor in dados.items():
            setattr(fluencia, campo, valor)

        fluencia.observacao = request.form.get(
            "observacao", ""
        ).strip()

        db.session.commit()

        flash(
            "Resultados da Fluência Verbal salvos com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "avaliacoes.visualizar",
                avaliacao_id=avaliacao.id
            )
        )

    return render_template(
        "avaliacoes/fluencia_verbal.html",
        avaliacao=avaliacao,
        fluencia=fluencia
    )
