import pandas as pd
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user


from app.services.analise_service import AnaliseService
from app.services.grafico_service import GraficoService
from app.services.agrupamento_service import AgrupamentoService

analises_bp = Blueprint(
    "analises",
    __name__,
    url_prefix="/analises"
)



@analises_bp.route("/")
@login_required
def index():

    # 1. Preparar os dados
    df = AnaliseService.preparar_dados(
        current_user.id
    )

    # 2. Indicadores gerais
    indicadores = (
        AnaliseService.calcular_indicadores(df)
    )

    # 3. Estatísticas descritivas
    estatisticas = (
        AnaliseService.calcular_estatisticas_descritivas(
            df
        )
    )

    # 4. Verificar disponibilidade do RAVLT
    colunas_ravlt = [
        "ravlt_a1",
        "ravlt_a2",
        "ravlt_a3",
        "ravlt_a4",
        "ravlt_a5"
    ]

    possui_ravlt = bool(
        df[colunas_ravlt].notna().any().any()
    )

    # 5. Gerar gráfico
    grafico_ravlt = None

    if possui_ravlt:
        grafico_ravlt = (
            GraficoService.evolucao_ravlt(
                df,
                incluir_plotly=True
            )
        )

    # 6. Últimas avaliações
    ultimas_avaliacoes = (
        df.sort_values(
            ["data_avaliacao", "avaliacao_id"],
            ascending=[False, False]
        )
        .head(5)
        .copy()
    )

    ultimas_avaliacoes["data_avaliacao"] = (
        pd.to_datetime(
            ultimas_avaliacoes["data_avaliacao"]
        ).dt.strftime("%d/%m/%Y")
    )

    registros_recentes = (
        ultimas_avaliacoes[
            ["avaliacao_id", "data_avaliacao"]
        ].to_dict(orient="records")
    )

    return render_template(
        "analises/index.html",
        indicadores=indicadores,
        estatisticas=estatisticas,
        grafico_ravlt=grafico_ravlt,
        registros_recentes=registros_recentes
    )


@analises_bp.route("/correlacoes", methods=["GET", "POST"])
@login_required
def correlacoes():

    df = AnaliseService.preparar_dados(
        current_user.id
    )

    # Montar catálogo para os campos de seleção
    grupos_metricas = AnaliseService.METRICAS

    variavel_x = "ravlt_a5"
    variavel_y = "tmt_tempo_b"
    metodo = "spearman"
    fluencia_tipo = ""
    fluencia_categoria = ""

    resultado = None
    grafico_dispersao = None

    if request.method == "POST":

        variavel_x = request.form.get(
            "variavel_x", ""
        )

        variavel_y = request.form.get(
            "variavel_y", ""
        )

        metodo = request.form.get(
            "metodo", "spearman"
        )

        fluencia_tipo = request.form.get(
            "fluencia_tipo", ""
        ).strip()

        fluencia_categoria = request.form.get(
            "fluencia_categoria", ""
        ).strip()

        try:

            resultado = (
                AnaliseService.calcular_correlacao(
                    df=df,
                    variavel_x=variavel_x,
                    variavel_y=variavel_y,
                    metodo=metodo,
                    fluencia_tipo=fluencia_tipo,
                    fluencia_categoria=fluencia_categoria
                )
            )
            
            grafico_dispersao = GraficoService.dispersao(
                resultado,
                incluir_plotly=True
            )

        except ValueError as erro:
            flash(str(erro), "erro")

    return render_template(
        "analises/correlacoes.html",
        grupos_metricas=grupos_metricas,
        variavel_x=variavel_x,
        variavel_y=variavel_y,
        metodo=metodo,
        fluencia_tipo=fluencia_tipo,
        fluencia_categoria=fluencia_categoria,
        resultado=resultado,
        grafico_dispersao=grafico_dispersao,
        total_avaliacoes=len(df)
    )


@analises_bp.route("/graficos")
@login_required
def graficos():

    df = AnaliseService.preparar_dados(
        current_user.id
    )

    colunas_ravlt = [
        "ravlt_a1",
        "ravlt_a2",
        "ravlt_a3",
        "ravlt_a4",
        "ravlt_a5"
    ]

    total_ravlt = int(
        df[colunas_ravlt].notna().any(axis=1).sum()
    )

    total_tmt_a = int(
        df["tmt_tempo_a"].notna().sum()
    )

    total_tmt_b = int(
        df["tmt_tempo_b"].notna().sum()
    )

    # Primeiro gráfico inclui a biblioteca Plotly
    grafico_ravlt = GraficoService.medias_ravlt(
        df,
        incluir_plotly=(total_ravlt > 0)
    )

    grafico_tmt_a = GraficoService.histograma_tmt(
        df,
        coluna="tmt_tempo_a",
        incluir_plotly=(
            total_ravlt == 0 and total_tmt_a > 0
        )
    )

    grafico_tmt_b = GraficoService.histograma_tmt(
        df,
        coluna="tmt_tempo_b",
        incluir_plotly=(
            total_ravlt == 0
            and total_tmt_a == 0
            and total_tmt_b > 0
        )
    )

    return render_template(
        "analises/graficos.html",
        grafico_ravlt=grafico_ravlt,
        grafico_tmt_a=grafico_tmt_a,
        grafico_tmt_b=grafico_tmt_b,
        total_ravlt=total_ravlt,
        total_tmt_a=total_tmt_a,
        total_tmt_b=total_tmt_b
    )



@analises_bp.route(
    "/agrupamentos",
    methods=["GET", "POST"]
)
@login_required
def agrupamentos():

    df = AnaliseService.preparar_dados(
        current_user.id
    )

    metricas_disponiveis = (
        AgrupamentoService.METRICAS_PERMITIDAS
    )

    metricas_selecionadas = [
        "ravlt_a5",
        "tmt_tempo_b"
    ]

    quantidade_grupos = 3
    resultado = None

    if request.method == "POST":

        metricas_selecionadas = (
            request.form.getlist("metricas")
        )

        quantidade_grupos = request.form.get(
            "quantidade_grupos",
            "3"
        )

        try:

            resultado = AgrupamentoService.executar(
                df=df,
                metricas=metricas_selecionadas,
                quantidade_grupos=quantidade_grupos
            )

        except ValueError as erro:
            flash(str(erro), "erro")

    return render_template(
        "analises/agrupamentos.html",
        metricas_disponiveis=metricas_disponiveis,
        metricas_selecionadas=metricas_selecionadas,
        quantidade_grupos=quantidade_grupos,
        resultado=resultado,
        total_avaliacoes=len(df)
    )
