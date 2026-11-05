
import pandas as pd
import numpy as np

from scipy.stats import pearsonr, spearmanr
from sqlalchemy.orm import joinedload

from app import db
from app.models.avaliacao import Avaliacao


class AnaliseService:

    METRICAS = {
        "RAVLT": {
            "ravlt_a1": "Tentativa A1",
            "ravlt_a2": "Tentativa A2",
            "ravlt_a3": "Tentativa A3",
            "ravlt_a4": "Tentativa A4",
            "ravlt_a5": "Tentativa A5",
            "ravlt_lista_b": "Lista B",
            "ravlt_a6": "Evocação A6",
            "ravlt_a7": "Evocação A7",
            "ravlt_reconhecimento": "Reconhecimento"
        },
        "TMT": {
            "tmt_tempo_a": "Tempo Parte A (s)",
            "tmt_erros_a": "Erros Parte A",
            "tmt_tempo_b": "Tempo Parte B (s)",
            "tmt_erros_b": "Erros Parte B"
        },
        "Fluência Verbal": {
            "fluencia_total": "Total de palavras",
            "fluencia_validas": "Respostas válidas",
            "fluencia_repeticoes": "Repetições",
            "fluencia_intervalo_1": "0–15 segundos",
            "fluencia_intervalo_2": "16–30 segundos",
            "fluencia_intervalo_3": "31–45 segundos",
            "fluencia_intervalo_4": "46–60 segundos"
        }
    }


    @staticmethod
    def preparar_dados(profissional_id):

        avaliacoes = db.session.scalars(
            db.select(Avaliacao)
            .options(
                joinedload(Avaliacao.paciente),
                joinedload(Avaliacao.ravlt),
                joinedload(Avaliacao.tmt),
                joinedload(Avaliacao.fluencia_verbal)
            )
            .where(
                Avaliacao.profissional_id == profissional_id
            )
            .order_by(
                Avaliacao.data,
                Avaliacao.id
            )
        ).all()

        registros = []

        for avaliacao in avaliacoes:

            ravlt = avaliacao.ravlt
            tmt = avaliacao.tmt
            fluencia = avaliacao.fluencia_verbal

            registro = {

                # Identificação
                "avaliacao_id": avaliacao.id,
                "paciente_id": avaliacao.paciente_id,
                "data_avaliacao": avaliacao.data,

                # Dados complementares
                "anos_estudo": (
                    avaliacao.paciente.anos_estudo
                    if avaliacao.paciente else None
                ),
                "horas_sono": avaliacao.horas_sono_anterior,

                # RAVLT
                "ravlt_a1": (
                    ravlt.quantidade_a1 if ravlt else None
                ),
                "ravlt_a2": (
                    ravlt.quantidade_a2 if ravlt else None
                ),
                "ravlt_a3": (
                    ravlt.quantidade_a3 if ravlt else None
                ),
                "ravlt_a4": (
                    ravlt.quantidade_a4 if ravlt else None
                ),
                "ravlt_a5": (
                    ravlt.quantidade_a5 if ravlt else None
                ),
                "ravlt_lista_b": (
                    ravlt.quantidade_lista_b if ravlt else None
                ),
                "ravlt_a6": (
                    ravlt.quantidade_a6 if ravlt else None
                ),
                "ravlt_a7": (
                    ravlt.quantidade_a7 if ravlt else None
                ),
                "ravlt_reconhecimento": (
                    ravlt.reconhecimento if ravlt else None
                ),

                # TMT
                "tmt_tempo_a": (
                    tmt.tempo_a if tmt else None
                ),
                "tmt_erros_a": (
                    tmt.erros_a if tmt else None
                ),
                "tmt_tempo_b": (
                    tmt.tempo_b if tmt else None
                ),
                "tmt_erros_b": (
                    tmt.erros_b if tmt else None
                ),

                # Fluência Verbal
                "fluencia_total": (
                    fluencia.total_palavras
                    if fluencia else None
                ),
                "fluencia_validas": (
                    fluencia.respostas_validas
                    if fluencia else None
                ),
                "fluencia_repeticoes": (
                    fluencia.repeticoes
                    if fluencia else None
                ),
                "fluencia_intervalo_1": (
                    fluencia.palavras_0_15
                    if fluencia else None
                ),
                "fluencia_intervalo_2": (
                    fluencia.palavras_16_30
                    if fluencia else None
                ),
                "fluencia_intervalo_3": (
                    fluencia.palavras_31_45
                    if fluencia else None
                ),
                "fluencia_intervalo_4": (
                    fluencia.palavras_46_60
                    if fluencia else None
                )
            }

            registros.append(registro)

        colunas = [

            # Identificação
            "avaliacao_id",
            "paciente_id",
            "data_avaliacao",

            # Dados complementares
            "anos_estudo",
            "horas_sono",

            # RAVLT
            "ravlt_a1",
            "ravlt_a2",
            "ravlt_a3",
            "ravlt_a4",
            "ravlt_a5",
            "ravlt_lista_b",
            "ravlt_a6",
            "ravlt_a7",
            "ravlt_reconhecimento",

            # TMT
            "tmt_tempo_a",
            "tmt_erros_a",
            "tmt_tempo_b",
            "tmt_erros_b",

            # Fluência Verbal
            "fluencia_total",
            "fluencia_validas",
            "fluencia_repeticoes",
            "fluencia_intervalo_1",
            "fluencia_intervalo_2",
            "fluencia_intervalo_3",
            "fluencia_intervalo_4"
        ]

        return pd.DataFrame(
            registros,
            columns=colunas
        )


    @staticmethod
    def calcular_estatisticas_descritivas(df):

        resultados = {}

        for teste, metricas in AnaliseService.METRICAS.items():

            estatisticas_teste = []

            for coluna, nome in metricas.items():

                # Converte valores para numéricos.
                # Valores ausentes ou inválidos viram NaN.
                serie = pd.to_numeric(
                    df[coluna],
                    errors="coerce"
                ).dropna()

                quantidade = int(serie.count())

                if quantidade == 0:
                    estatisticas = {
                        "metrica": nome,
                        "coluna": coluna,
                        "n": 0,
                        "media": None,
                        "mediana": None,
                        "minimo": None,
                        "maximo": None,
                        "desvio_padrao": None,
                        "variancia": None
                    }

                else:
                    estatisticas = {
                        "metrica": nome,
                        "coluna": coluna,
                        "n": quantidade,

                        "media": round(
                            float(serie.mean()), 2
                        ),

                        "mediana": round(
                            float(serie.median()), 2
                        ),

                        "minimo": float(serie.min()),

                        "maximo": float(serie.max()),

                        # Estatísticas amostrais
                        "desvio_padrao": (
                            round(float(serie.std(ddof=1)), 2)
                            if quantidade >= 2 else None
                        ),

                        "variancia": (
                            round(float(serie.var(ddof=1)), 2)
                            if quantidade >= 2 else None
                        )
                    }

                estatisticas_teste.append(estatisticas)

            resultados[teste] = estatisticas_teste

        return resultados


    @staticmethod
    def calcular_correlacao(
        df,
        variavel_x,
        variavel_y,
        metodo="spearman",
        fluencia_tipo=None,
        fluencia_categoria=None
    ):
        # 1. Validar as métricas permitidas
        metricas = {
            coluna: nome
            for grupo in AnaliseService.METRICAS.values()
            for coluna, nome in grupo.items()
        }

        if variavel_x not in metricas or variavel_y not in metricas:
            raise ValueError("Selecione métricas válidas.")

        if variavel_x == variavel_y:
            raise ValueError(
                "Selecione duas métricas diferentes."
            )

        if metodo not in ("pearson", "spearman"):
            raise ValueError("Método de correlação inválido.")

        # 2. Filtrar o protocolo de Fluência Verbal
        dados = df.copy()

        envolve_fluencia = (
            variavel_x.startswith("fluencia_")
            or variavel_y.startswith("fluencia_")
        )

        if envolve_fluencia:
            if not fluencia_tipo or not fluencia_categoria:
                raise ValueError(
                    "Para analisar Fluência Verbal, informe "
                    "o tipo e a categoria ou letra do protocolo."
                )

            dados = dados[
                (dados["fluencia_tipo"] == fluencia_tipo)
                & (
                    dados["fluencia_categoria"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.casefold()
                    == fluencia_categoria.strip().casefold()
                )
            ]

        # 3. Manter apenas pares com valores válidos
        pares = dados[
            ["paciente_id", variavel_x, variavel_y]
        ].copy()

        for coluna in (variavel_x, variavel_y):
            pares[coluna] = pd.to_numeric(
                pares[coluna],
                errors="coerce"
            )

        pares = pares.replace(
            [np.inf, -np.inf],
            np.nan
        ).dropna()

        # 4. Evitar tratar avaliações repetidas
        # do mesmo paciente como independentes
        if pares["paciente_id"].duplicated().any():
            raise ValueError(
                "Existem avaliações repetidas de um mesmo "
                "paciente entre os pares válidos. "
                "Esta versão exige uma observação por "
                "paciente. Utilize uma seleção com uma "
                "avaliação por paciente antes de analisar."
            )

        n = len(pares)

        if n < 3:
            raise ValueError(
                "São necessários pelo menos três pares "
                "válidos para esta análise."
            )

        x = pares[variavel_x]
        y = pares[variavel_y]

        if x.nunique() < 2 or y.nunique() < 2:
            raise ValueError(
                "Não é possível calcular a correlação "
                "quando uma das métricas é constante."
            )

        # 5. Calcular a correlação
        if metodo == "pearson":
            resultado = pearsonr(x, y)
        else:
            resultado = spearmanr(x, y)

        coeficiente = float(resultado.statistic)
        valor_p = float(resultado.pvalue)

        if not np.isfinite(coeficiente):
            raise ValueError(
                "Não foi possível calcular a correlação."
            )

        # 6. Classificação descritiva convencional
        absoluto = abs(coeficiente)

        if absoluto < 0.20:
            intensidade = "muito fraca"
        elif absoluto < 0.40:
            intensidade = "fraca"
        elif absoluto < 0.60:
            intensidade = "moderada"
        elif absoluto < 0.80:
            intensidade = "forte"
        else:
            intensidade = "muito forte"

        if coeficiente > 0:
            direcao = "positiva"
        elif coeficiente < 0:
            direcao = "negativa"
        else:
            direcao = "nula"

        return {
            "variavel_x": variavel_x,
            "variavel_y": variavel_y,
            "nome_x": metricas[variavel_x],
            "nome_y": metricas[variavel_y],
            "metodo": metodo,
            "n": n,
            "coeficiente": coeficiente,
            "valor_p": (
                valor_p if np.isfinite(valor_p) else None
            ),
            "intensidade": intensidade,
            "direcao": direcao,
            "fluencia_tipo": fluencia_tipo,
            "fluencia_categoria": fluencia_categoria,
            "pontos": [
                {
                    "x": float(linha[variavel_x]),
                    "y": float(linha[variavel_y])
                }
                for _, linha in pares.iterrows()
            ]
        }


    @staticmethod
    def calcular_indicadores(df):

        total_avaliacoes = len(df)

        total_pacientes = (
            int(df["paciente_id"].nunique())
            if not df.empty else 0
        )

        grupos = {
            "RAVLT": [
                "ravlt_a1",
                "ravlt_a2",
                "ravlt_a3",
                "ravlt_a4",
                "ravlt_a5",
                "ravlt_lista_b",
                "ravlt_a6",
                "ravlt_a7",
                "ravlt_reconhecimento"
            ],

            "TMT": [
                "tmt_tempo_a",
                "tmt_erros_a",
                "tmt_tempo_b",
                "tmt_erros_b"
            ],

            "Fluência Verbal": [
                "fluencia_total",
                "fluencia_validas",
                "fluencia_repeticoes",
                "fluencia_intervalo_1",
                "fluencia_intervalo_2",
                "fluencia_intervalo_3",
                "fluencia_intervalo_4"
            ]
        }

        quantidade_testes = {}

        for nome, colunas in grupos.items():

            quantidade_testes[nome] = int(
                df[colunas].notna().any(axis=1).sum()
            )

        total_com_tres_testes = int(
            (
                df[grupos["RAVLT"]].notna().any(axis=1)
                &
                df[grupos["TMT"]].notna().any(axis=1)
                &
                df[grupos["Fluência Verbal"]].notna().any(axis=1)
            ).sum()
        )

        percentual_com_tres_testes = (
            round(
                total_com_tres_testes / total_avaliacoes * 100,
                1
            )
            if total_avaliacoes > 0 else 0
        )

        return {
            "total_avaliacoes": total_avaliacoes,
            "total_pacientes": total_pacientes,
            "quantidade_testes": quantidade_testes,
            "total_com_tres_testes": total_com_tres_testes,
            "percentual_com_tres_testes": percentual_com_tres_testes
        }
