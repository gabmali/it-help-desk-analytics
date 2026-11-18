"""Calcula indicadores principais para acompanhar a operação de Help Desk."""

from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_BASE = PASTA_PROJETO / "data" / "chamados_help_desk_tratados.csv"
PASTA_DADOS = PASTA_PROJETO / "data"


def carregar_dados() -> pd.DataFrame:
    """Lê a base tratada e prepara colunas auxiliares para os cálculos."""
    dados = pd.read_csv(
        ARQUIVO_BASE,
        encoding="utf-8-sig",
        parse_dates=["data_abertura", "data_encerramento", "data_corte_analise"],
    )
    dados["eh_fechado"] = dados["status"].eq("Fechado")
    dados["eh_aberto"] = ~dados["eh_fechado"]
    dados["sla_ok"] = dados["sla_cumprido"].eq("Sim")
    dados["sla_fora"] = dados["sla_cumprido"].eq("Não")
    dados["mes"] = dados["data_abertura"].dt.to_period("M").astype(str)
    return dados


def calcular_resumo(dados: pd.DataFrame) -> pd.DataFrame:
    """Calcula os KPIs gerais e registra a regra usada em cada um."""
    fechados = dados.loc[dados["eh_fechado"]]
    fechados_com_nota = fechados["satisfacao_usuario"].dropna()
    total_fechados = int(dados["eh_fechado"].sum())
    sla_cumpridos = int(dados["sla_ok"].sum())
    sla_fora = int(dados["sla_fora"].sum())

    indicadores = [
        ("total_chamados", len(dados), "chamados", "Todos os registros da base"),
        ("chamados_fechados", total_fechados, "chamados", "Status igual a Fechado"),
        ("chamados_abertos", int(dados["eh_aberto"].sum()), "chamados", "Status diferente de Fechado"),
        ("percentual_abertos", 100 * dados["eh_aberto"].mean(), "%", "Abertos dividido pelo total"),
        (
            "tempo_medio_resolucao_horas",
            fechados["tempo_resolucao_horas"].mean(),
            "horas",
            "Média apenas dos chamados fechados",
        ),
        (
            "tempo_mediano_resolucao_horas",
            fechados["tempo_resolucao_horas"].median(),
            "horas",
            "Mediana apenas dos chamados fechados",
        ),
        (
            "sla_cumprido_percentual",
            100 * sla_cumpridos / total_fechados if total_fechados else 0,
            "%",
            "Fechados dentro do SLA dividido por todos os fechados",
        ),
        (
            "sla_fora_percentual",
            100 * sla_fora / total_fechados if total_fechados else 0,
            "%",
            "Fechados fora do SLA dividido por todos os fechados",
        ),
        (
            "chamados_abertos_atrasados",
            int((dados["eh_aberto"] & dados["situacao_sla_na_data_corte"].eq("Atrasado")).sum()),
            "chamados",
            "Abertos classificados como Atrasado na data de corte",
        ),
        (
            "satisfacao_media",
            fechados_com_nota.mean(),
            "nota de 1 a 5",
            "Média das avaliações preenchidas em chamados fechados",
        ),
        (
            "respostas_satisfacao",
            len(fechados_com_nota),
            "respostas",
            "Quantidade de chamados fechados com avaliação preenchida",
        ),
    ]
    resumo = pd.DataFrame(indicadores, columns=["indicador", "valor", "unidade", "regra"])
    resumo["valor"] = resumo["valor"].astype(float).round(2)
    return resumo


def calcular_por_grupo(dados: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Calcula volume, resolução média e cumprimento do SLA por grupo."""
    resumo = (
        dados.groupby(coluna, as_index=False)
        .agg(
            total_chamados=("id_chamado", "count"),
            chamados_fechados=("eh_fechado", "sum"),
            chamados_abertos=("eh_aberto", "sum"),
            tempo_medio_resolucao_horas=("tempo_resolucao_horas", "mean"),
            chamados_sla_cumprido=("sla_ok", "sum"),
        )
    )
    denominador = resumo["chamados_fechados"].where(resumo["chamados_fechados"].ne(0))
    resumo["sla_cumprido_percentual"] = 100 * resumo["chamados_sla_cumprido"] / denominador
    resumo["tempo_medio_resolucao_horas"] = resumo["tempo_medio_resolucao_horas"].round(2)
    resumo["sla_cumprido_percentual"] = resumo["sla_cumprido_percentual"].round(2)
    return resumo


if __name__ == "__main__":
    chamados = carregar_dados()
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)

    resumo = calcular_resumo(chamados)
    mensal = calcular_por_grupo(chamados, "mes")
    por_tecnico = calcular_por_grupo(chamados, "tecnico")
    por_prioridade = calcular_por_grupo(chamados, "prioridade")
    por_departamento = calcular_por_grupo(chamados, "departamento")

    resumo.to_csv(PASTA_DADOS / "kpis_resumo.csv", index=False, encoding="utf-8-sig")
    mensal.to_csv(PASTA_DADOS / "kpis_mensais.csv", index=False, encoding="utf-8-sig")
    por_tecnico.to_csv(PASTA_DADOS / "kpis_por_tecnico.csv", index=False, encoding="utf-8-sig")
    por_prioridade.to_csv(PASTA_DADOS / "kpis_por_prioridade.csv", index=False, encoding="utf-8-sig")
    por_departamento.to_csv(PASTA_DADOS / "kpis_por_departamento.csv", index=False, encoding="utf-8-sig")

    print("Indicadores gerais:")
    print(resumo.to_string(index=False))
    print("\nIndicadores calculados por mês, técnico, prioridade e departamento.")
