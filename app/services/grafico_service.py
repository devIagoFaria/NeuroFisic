
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


class GraficoService:

    @staticmethod
    def _layout(fig, titulo_x=None, titulo_y=None):
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Arial, sans-serif",
                color="#344054",
                size=12
            ),
            margin=dict(l=45, r=25, t=35, b=55),
            height=380,
            xaxis_title=titulo_x,
            yaxis_title=titulo_y,
            hovermode="closest"
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#edf1f1",
            zeroline=False
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#edf1f1",
            zeroline=False
        )

        return fig

    @staticmethod
    def _html(fig, incluir_plotly=False):
        return pio.to_html(
            fig,
            full_html=False,
            include_plotlyjs=(
                True if incluir_plotly else False
            ),
            config={
                "responsive": True,
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": "neuropsico_grafico",
                    "scale": 2
                }
            }
        )

    @staticmethod
    def dispersao(resultado, incluir_plotly=False):

        pontos = resultado["pontos"]

        x = [p["x"] for p in pontos]
        y = [p["y"] for p in pontos]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(
                    size=11,
                    color="#176b68",
                    opacity=0.8,
                    line=dict(
                        width=1,
                        color="#ffffff"
                    )
                ),
                name="Avaliações",
                hovertemplate=(
                    "X: %{x}<br>"
                    "Y: %{y}<extra></extra>"
                )
            )
        )

        GraficoService._layout(
            fig,
            titulo_x=resultado["nome_x"],
            titulo_y=resultado["nome_y"]
        )

        return GraficoService._html(
            fig,
            incluir_plotly=incluir_plotly
        )

    @staticmethod
    def medias_ravlt(df, incluir_plotly=False):

        colunas = [
            "ravlt_a1",
            "ravlt_a2",
            "ravlt_a3",
            "ravlt_a4",
            "ravlt_a5"
        ]

        nomes = ["A1", "A2", "A3", "A4", "A5"]

        medias = []
        quantidades = []

        for coluna in colunas:
            serie = pd.to_numeric(
                df[coluna],
                errors="coerce"
            ).dropna()

            medias.append(
                float(serie.mean())
                if not serie.empty else None
            )

            quantidades.append(len(serie))

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=nomes,
                y=medias,
                marker_color="#176b68",
                customdata=quantidades,
                hovertemplate=(
                    "Tentativa: %{x}<br>"
                    "Média: %{y:.2f}<br>"
                    "N: %{customdata}"
                    "<extra></extra>"
                )
            )
        )

        GraficoService._layout(
            fig,
            titulo_x="Tentativa",
            titulo_y="Média de palavras recordadas"
        )

        return GraficoService._html(
            fig,
            incluir_plotly=incluir_plotly
        )

    @staticmethod
    def histograma_tmt(
        df,
        coluna="tmt_tempo_a",
        incluir_plotly=False
    ):

        colunas_permitidas = {
            "tmt_tempo_a": "TMT Parte A",
            "tmt_tempo_b": "TMT Parte B"
        }

        if coluna not in colunas_permitidas:
            raise ValueError(
                "Métrica TMT inválida."
            )

        serie = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).dropna()

        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=serie.tolist(),
                nbinsx=10,
                marker_color="#176b68",
                hovertemplate=(
                    "Tempo: %{x} s<br>"
                    "Frequência: %{y}"
                    "<extra></extra>"
                )
            )
        )

        GraficoService._layout(
            fig,
            titulo_x=(
                f"Tempo — {colunas_permitidas[coluna]} (s)"
            ),
            titulo_y="Quantidade de avaliações"
        )

        return GraficoService._html(
            fig,
            incluir_plotly=incluir_plotly
        )

    @staticmethod
    def evolucao_ravlt(df, incluir_plotly=True):

        colunas = [
            "ravlt_a1",
            "ravlt_a2",
            "ravlt_a3",
            "ravlt_a4",
            "ravlt_a5"
        ]

        tentativas = ["A1", "A2", "A3", "A4", "A5"]

        medias = []
        quantidades = []

        for coluna in colunas:

            serie = pd.to_numeric(
                df[coluna],
                errors="coerce"
            ).dropna()

            medias.append(
                float(serie.mean())
                if not serie.empty else None
            )

            quantidades.append(int(len(serie)))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=tentativas,
                y=medias,
                mode="lines+markers",
                line=dict(
                    color="#176b68",
                    width=3
                ),
                marker=dict(
                    size=9,
                    color="#176b68"
                ),
                customdata=quantidades,
                hovertemplate=(
                    "Tentativa: %{x}<br>"
                    "Média: %{y:.2f}<br>"
                    "N: %{customdata}"
                    "<extra></extra>"
                )
            )
        )

        GraficoService._layout(
            fig,
            titulo_x="Tentativa",
            titulo_y="Média de palavras recordadas"
        )

        return GraficoService._html(
            fig,
            incluir_plotly=incluir_plotly
        )
