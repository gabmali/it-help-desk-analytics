"""Gera recomendações operacionais com base em regras simples e explícitas."""

from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_BASE = PASTA_PROJETO / "data" / "chamados_help_desk_tratados.csv"
ARQUIVO_SAIDA = PASTA_PROJETO / "data" / "recomendacoes_automaticas.md"


def carregar_dados() -> pd.DataFrame:
    """Carrega a base tratada e prepara informações para as regras de recomendação."""
    dados = pd.read_csv(
        ARQUIVO_BASE,
        encoding="utf-8-sig",
        parse_dates=["data_abertura", "data_encerramento", "data_corte_analise"],
    )
    dados["fechado"] = dados["status"].eq("Fechado")
    return dados


def calcular_reincidencia(dados: pd.DataFrame) -> pd.DataFrame:
    """Marca chamados repetidos no departamento em até 30 dias."""
    ordenados = dados.sort_values(["departamento", "descricao_problema", "data_abertura", "id_chamado"]).copy()
    diferenca_dias = (
        ordenados.groupby(["departamento", "descricao_problema"])["data_abertura"]
        .diff()
        .dt.total_seconds()
        .div(86400)
    )
    ordenados["reincidente_30_dias"] = diferenca_dias.between(0, 30)
    return (
        ordenados.groupby("categoria", as_index=False)
        .agg(
            total_chamados=("id_chamado", "count"),
            chamados_reincidentes=("reincidente_30_dias", "sum"),
        )
        .assign(
            reincidencia_pct=lambda tabela: 100 * tabela["chamados_reincidentes"] / tabela["total_chamados"]
        )
        .sort_values("reincidencia_pct", ascending=False)
    )


def gerar_recomendacoes(dados: pd.DataFrame) -> list[dict[str, str]]:
    """Avalia limiares simples e devolve evidências com ações sugeridas."""
    recomendacoes = []

    contagem_problema = dados["descricao_problema"].value_counts()
    problema_top = contagem_problema.index[0]
    quantidade_top = int(contagem_problema.iloc[0])
    recomendacoes.append({
        "prioridade": "Alta",
        "sinal": f"{problema_top}: {quantidade_top} chamados ({quantidade_top / len(dados) * 100:.1f}% da base).",
        "acao_sugerida": "Criar uma página de autosserviço e revisar o fluxo de solução para reduzir chamados repetidos.",
    })

    reincidencia = calcular_reincidencia(dados)
    categorias_altas = reincidencia.loc[reincidencia["reincidencia_pct"] >= 50]
    if not categorias_altas.empty:
        nomes = ", ".join(
            f"{linha.categoria} ({linha.reincidencia_pct:.1f}%)"
            for linha in categorias_altas.itertuples(index=False)
        )
        recomendacoes.append({
            "prioridade": "Alta",
            "sinal": f"Categorias com reincidência de pelo menos 50%: {nomes}.",
            "acao_sugerida": "Investigar causa raiz por departamento e registrar uma correção preventiva para cada problema recorrente.",
        })

    fechados = dados.loc[dados["fechado"]].copy()
    fechados["sla_ok"] = fechados["sla_cumprido"].eq("Sim")
    sla_global = 100 * fechados["sla_ok"].mean()
    por_tecnico = fechados.groupby("tecnico").agg(
        chamados_fechados=("id_chamado", "count"),
        sla_pct=("sla_ok", lambda serie: 100 * serie.mean()),
    )
    abaixo_meta = por_tecnico.loc[
        (por_tecnico["chamados_fechados"] >= 30)
        & (por_tecnico["sla_pct"] < sla_global - 5)
    ]
    if not abaixo_meta.empty:
        nomes = ", ".join(
            f"{tecnico} ({linha.sla_pct:.1f}%, {int(linha.chamados_fechados)} fechados)"
            for tecnico, linha in abaixo_meta.iterrows()
        )
        recomendacoes.append({
            "prioridade": "Média",
            "sinal": f"Técnicos mais de 5 pontos percentuais abaixo do SLA geral ({sla_global:.1f}%): {nomes}.",
            "acao_sugerida": "Revisar prioridades, complexidade e distribuição da fila antes de propor treinamento ou redistribuir carga.",
        })

    abertos_atrasados = dados.loc[
        (~dados["fechado"]) & dados["situacao_sla_na_data_corte"].eq("Atrasado")
    ]
    if not abertos_atrasados.empty:
        por_departamento = abertos_atrasados["departamento"].value_counts()
        destaques = ", ".join(f"{departamento}: {quantidade}" for departamento, quantidade in por_departamento.head(3).items())
        recomendacoes.append({
            "prioridade": "Alta",
            "sinal": f"{len(abertos_atrasados)} chamados abertos estão atrasados; maiores filas: {destaques}.",
            "acao_sugerida": "Fazer triagem diária da fila vencida, confirmar responsável e prazo de resolução e escalar os casos críticos.",
        })

    contagem_mensal_categoria = (
        dados.assign(mes=dados["data_abertura"].dt.to_period("M").astype(str))
        .groupby(["mes", "categoria"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    if len(contagem_mensal_categoria) >= 2:
        mes_atual, mes_anterior = contagem_mensal_categoria.index[-1], contagem_mensal_categoria.index[-2]
        atual = contagem_mensal_categoria.loc[mes_atual]
        anterior = contagem_mensal_categoria.loc[mes_anterior]
        subidas = atual[(anterior >= 10) & ((atual - anterior) >= 5) & (atual >= anterior * 1.25)]
        if not subidas.empty:
            detalhes = ", ".join(
                f"{categoria}: {int(anterior[categoria])} para {int(atual[categoria])}"
                for categoria in subidas.sort_values(ascending=False).index
            )
            recomendacoes.append({
                "prioridade": "Média",
                "sinal": f"Aumento de pelo menos 25% e 5 chamados de {mes_anterior} para {mes_atual}: {detalhes}.",
                "acao_sugerida": "Verificar mudanças recentes, incidentes concentrados e possíveis falhas após atualizações.",
            })

    satisfacao = fechados["satisfacao_usuario"].dropna()
    notas_baixas_pct = 100 * satisfacao.le(2).mean() if len(satisfacao) else 0
    if not satisfacao.empty and (satisfacao.mean() < 4 or notas_baixas_pct >= 10):
        recomendacoes.append({
            "prioridade": "Média",
            "sinal": f"Satisfação média de {satisfacao.mean():.2f}/5; {notas_baixas_pct:.1f}% das notas são 1 ou 2.",
            "acao_sugerida": "Revisar comentários e chamados com notas baixas para localizar etapas do atendimento que geram insatisfação.",
        })

    return recomendacoes


if __name__ == "__main__":
    chamados = carregar_dados()
    recomendacoes = gerar_recomendacoes(chamados)

    linhas = [
        "# Recomendações automáticas de suporte",
        "",
        "Resultados derivados da base fictícia de chamados, com data de corte em 31/12/2025.",
        "As regras indicam pontos para investigar; não provam causa raiz ou desempenho individual.",
        "",
    ]
    for numero, recomendacao in enumerate(recomendacoes, start=1):
        linhas.extend([
            f"## {numero}. Prioridade {recomendacao['prioridade']}",
            f"**Sinal:** {recomendacao['sinal']}",
            f"**Ação sugerida:** {recomendacao['acao_sugerida']}",
            "",
        ])

    ARQUIVO_SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Recomendações geradas: {len(recomendacoes)}")
    print(f"Arquivo: {ARQUIVO_SAIDA}")
