
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from app.services.analise_service import AnaliseService


class AgrupamentoService:

    # Nesta primeira versão, apenas RAVLT e TMT.
    METRICAS_PERMITIDAS = {
        coluna: nome
        for grupo, metricas in AnaliseService.METRICAS.items()
        if grupo in ("RAVLT", "TMT")
        for coluna, nome in metricas.items()
    }

    @staticmethod
    def executar(df, metricas, quantidade_grupos=3):

        # 1. Validar métricas
        if not isinstance(metricas, (list, tuple)):
            raise ValueError("Selecione as métricas.")

        if len(metricas) < 2:
            raise ValueError(
                "Selecione pelo menos duas métricas."
            )

        if len(metricas) != len(set(metricas)):
            raise ValueError(
                "Não selecione métricas repetidas."
            )

        for metrica in metricas:
            if metrica not in AgrupamentoService.METRICAS_PERMITIDAS:
                raise ValueError(
                    "Uma das métricas selecionadas é inválida."
                )

        # 2. Validar número de grupos
        try:
            quantidade_grupos = int(quantidade_grupos)
        except (TypeError, ValueError):
            raise ValueError(
                "Informe uma quantidade válida de grupos."
            )

        if quantidade_grupos < 2 or quantidade_grupos > 6:
            raise ValueError(
                "A quantidade de grupos deve estar entre 2 e 6."
            )

        # 3. Preparar os dados
        colunas = [
            "avaliacao_id",
            "paciente_id",
            "data_avaliacao"
        ] + list(metricas)

        dados = df[colunas].copy()

        for metrica in metricas:
            dados[metrica] = pd.to_numeric(
                dados[metrica],
                errors="coerce"
            )

        dados = dados.replace(
            [np.inf, -np.inf],
            np.nan
        )

        # Exige resultados em todas as métricas escolhidas
        dados = dados.dropna(
            subset=metricas
        )

        # 4. Selecionar uma avaliação por paciente
        dados = dados.sort_values(
            ["data_avaliacao", "avaliacao_id"],
            ascending=[False, False]
        )

        dados = dados.drop_duplicates(
            subset=["paciente_id"],
            keep="first"
        )

        dados = dados.sort_values(
            "avaliacao_id"
        ).reset_index(drop=True)

        n = len(dados)

        # Precisamos de mais registros que grupos
        # para avaliar o resultado com silhouette.
        if n <= quantidade_grupos:
            raise ValueError(
                "É necessário ter mais pacientes "
                "com dados completos do que grupos."
            )

        # 5. Remover variáveis constantes
        constantes = [
            metrica
            for metrica in metricas
            if dados[metrica].nunique() < 2
        ]

        if constantes:
            raise ValueError(
                "As seguintes métricas não apresentam "
                "variação suficiente: "
                + ", ".join(constantes)
            )

        # 6. Padronização
        matriz_original = dados[metricas].to_numpy(
            dtype=float
        )

        scaler = StandardScaler()

        matriz_padronizada = scaler.fit_transform(
            matriz_original
        )

        # 7. Executar K-Means
        modelo = KMeans(
            n_clusters=quantidade_grupos,
            random_state=42,
            n_init=10
        )

        grupos = modelo.fit_predict(
            matriz_padronizada
        )

        grupos_distintos = len(set(grupos))

        if grupos_distintos < quantidade_grupos or grupos_distintos >= n:
            raise ValueError(
                "Não foi possível formar a quantidade "
                "solicitada de grupos distintos. "
                "Experimente reduzir o número de grupos."
            )

        dados["grupo"] = grupos + 1

        # 8. Avaliar separação dos grupos
        silhueta = float(
            silhouette_score(
                matriz_padronizada,
                grupos
            )
        )

        # 9. Resumir os grupos
        resumo = []

        for numero_grupo in sorted(
            dados["grupo"].unique()
        ):

            registros_grupo = dados[
                dados["grupo"] == numero_grupo
            ]

            medias = {
                metrica: round(
                    float(registros_grupo[metrica].mean()),
                    2
                )
                for metrica in metricas
            }

            resumo.append({
                "grupo": int(numero_grupo),
                "quantidade": len(registros_grupo),
                "medias": medias
            })

        # 10. Preparar registros para visualização
        registros = []

        for _, linha in dados.iterrows():

            valores = {
                metrica: float(linha[metrica])
                for metrica in metricas
            }

            registros.append({
                "avaliacao_id": int(linha["avaliacao_id"]),
                "grupo": int(linha["grupo"]),
                "valores": valores
            })

        return {
            "quantidade_registros": n,
            "quantidade_grupos": quantidade_grupos,
            "metricas": list(metricas),
            "nomes_metricas": {
                metrica: AgrupamentoService.METRICAS_PERMITIDAS[metrica]
                for metrica in metricas
            },
            "silhueta": round(silhueta, 3),
            "resumo": resumo,
            "registros": registros
        }
