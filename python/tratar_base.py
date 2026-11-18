"""Limpa tipos e textos e valida regras de consistência dos chamados."""

from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_ENTRADA = PASTA_PROJETO / "data" / "chamados_help_desk.csv"
ARQUIVO_SAIDA = PASTA_PROJETO / "data" / "chamados_help_desk_tratados.csv"

colunas_texto = [
    "id_chamado", "departamento", "tecnico", "categoria", "descricao_problema",
    "prioridade", "status", "sla_cumprido", "situacao_sla_na_data_corte",
]
colunas_data = ["data_abertura", "data_encerramento", "data_corte_analise"]
colunas_numericas = ["tempo_resolucao_horas", "sla_previsto_horas", "satisfacao_usuario"]


def carregar_e_tratar() -> tuple[pd.DataFrame, int, int]:
    """Lê o arquivo original, normaliza campos e aplica verificações de qualidade."""
    dados = pd.read_csv(ARQUIVO_ENTRADA, encoding="utf-8-sig")
    total_original = len(dados)

    # Remove espaços extras e transforma texto vazio em valor ausente.
    for coluna in colunas_texto:
        dados[coluna] = (
            dados[coluna]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .replace("", pd.NA)
        )

    # Converte textos de data para datas e números armazenados como texto para números.
    for coluna in colunas_data:
        dados[coluna] = pd.to_datetime(dados[coluna], errors="raise")
    for coluna in colunas_numericas:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="raise")

    # Um ID identifica um chamado. Se houver repetição, conserva a primeira ocorrência.
    duplicados_removidos = int(dados["id_chamado"].duplicated().sum())
    dados = dados.drop_duplicates(subset="id_chamado", keep="first").copy()

    # Campos essenciais não podem ficar vazios.
    campos_obrigatorios = [
        "id_chamado", "data_abertura", "departamento", "tecnico", "categoria",
        "descricao_problema", "prioridade", "status", "sla_previsto_horas",
    ]
    faltantes = dados[campos_obrigatorios].isna().sum()
    faltantes = faltantes[faltantes > 0]
    if not faltantes.empty:
        raise ValueError(f"Há campos obrigatórios vazios:\n{faltantes.to_string()}")

    # Regras que devem ser verdadeiras para a combinação de status e datas.
    status_validos = {"Aberto", "Em andamento", "Fechado"}
    if not dados["status"].isin(status_validos).all():
        raise ValueError("Foi encontrado um status fora da lista esperada.")

    fechado = dados["status"].eq("Fechado")
    aberto = ~fechado
    if (dados.loc[fechado, "data_encerramento"].isna()).any():
        raise ValueError("Há chamados fechados sem data de encerramento.")
    if (dados.loc[aberto, "data_encerramento"].notna()).any():
        raise ValueError("Há chamados abertos com data de encerramento.")
    if (dados.loc[fechado, "data_encerramento"] < dados.loc[fechado, "data_abertura"]).any():
        raise ValueError("Há encerramento anterior à abertura.")

    # Chamados abertos ainda não têm duração final nem avaliação de satisfação/SLA.
    if dados.loc[aberto, "tempo_resolucao_horas"].notna().any():
        raise ValueError("Há chamados abertos com tempo final de resolução.")
    if dados.loc[aberto, "satisfacao_usuario"].notna().any():
        raise ValueError("Há chamados abertos com nota de satisfação.")
    if dados.loc[aberto, "sla_cumprido"].notna().any():
        raise ValueError("Há chamados abertos marcados como SLA cumprido/não cumprido.")

    if (dados["sla_previsto_horas"] <= 0).any():
        raise ValueError("O prazo de SLA deve ser maior que zero.")
    if (dados.loc[fechado, "tempo_resolucao_horas"] < 0).any():
        raise ValueError("Há tempo de resolução negativo.")
    notas_preenchidas = dados["satisfacao_usuario"].dropna()
    if not notas_preenchidas.between(1, 5).all():
        raise ValueError("A satisfação deve ser uma nota entre 1 e 5.")

    return dados, total_original, duplicados_removidos


if __name__ == "__main__":
    chamados, total_original, duplicados_removidos = carregar_e_tratar()
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    chamados.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d %H:%M:%S")

    print(f"Arquivo tratado salvo em: {ARQUIVO_SAIDA}")
    print(f"Linhas na origem: {total_original}")
    print(f"IDs duplicados removidos: {duplicados_removidos}")
    print(f"Linhas após o tratamento: {len(chamados)}")
    print("Valores ausentes por coluna:")
    print(chamados.isna().sum().to_string())
