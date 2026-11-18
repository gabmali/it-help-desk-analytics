"""Faz a análise exploratória e salva gráficos para o portfólio."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_BASE = PASTA_PROJETO / "data" / "chamados_help_desk_tratados.csv"
PASTA_IMAGENS = PASTA_PROJETO / "images"
PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)

# Define um estilo comum para manter os gráficos com a mesma aparência.
sns.set_theme(style="whitegrid", palette="deep")

# Lê o arquivo tratado e converte as datas para trabalhar com meses.
chamados = pd.read_csv(
    ARQUIVO_BASE,
    encoding="utf-8-sig",
    parse_dates=["data_abertura", "data_encerramento", "data_corte_analise"],
)
fechados = chamados.loc[chamados["status"] == "Fechado"].copy()

# Prepara tabelas resumidas para os gráficos.
mensal = (
    chamados.assign(mes=chamados["data_abertura"].dt.to_period("M").astype(str))
    .groupby("mes")
    .size()
    .rename("quantidade_chamados")
    .reset_index()
)
por_categoria = chamados["categoria"].value_counts().sort_values()
por_departamento = chamados["departamento"].value_counts().sort_values()
satisfacao_contagem = (
    fechados["satisfacao_usuario"].astype("Int64").astype(str)
    .value_counts()
    .reindex(["1", "2", "3", "4", "5"], fill_value=0)
    .rename_axis("nota")
    .reset_index(name="quantidade_respostas")
)

print("Volume por mês:")
print(mensal.to_string(index=False))
print(f"\nMédia de chamados por mês: {mensal['quantidade_chamados'].mean():.1f}")
print("\nChamados por categoria:")
print(por_categoria.sort_values(ascending=False).to_string())
print("\nChamados por departamento:")
print(por_departamento.sort_values(ascending=False).to_string())
print("\nTempo de resolução em horas, chamados fechados:")
print(fechados["tempo_resolucao_horas"].describe().round(2).to_string())
print(f"\nSatisfação média: {fechados['satisfacao_usuario'].mean():.2f} de 5")

# Gráfico 1: evolução do volume mensal.
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=mensal, x="mes", y="quantidade_chamados", marker="o", ax=ax)
ax.set_title("Chamados abertos por mês")
ax.set_xlabel("Mês")
ax.set_ylabel("Quantidade de chamados")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout()
fig.savefig(PASTA_IMAGENS / "eda_volume_mensal.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Gráfico 2: volume por categoria, em barras horizontais.
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=por_categoria.values, y=por_categoria.index, ax=ax, color=sns.color_palette()[0])
ax.set_title("Chamados por categoria")
ax.set_xlabel("Quantidade de chamados")
ax.set_ylabel("Categoria")
fig.tight_layout()
fig.savefig(PASTA_IMAGENS / "eda_categoria.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Gráfico 3: quantidade de chamados por departamento.
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=por_departamento.values, y=por_departamento.index, ax=ax, color=sns.color_palette()[1])
ax.set_title("Chamados por departamento")
ax.set_xlabel("Quantidade de chamados")
ax.set_ylabel("Departamento")
fig.tight_layout()
fig.savefig(PASTA_IMAGENS / "eda_departamento.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Gráfico 4: distribuição do tempo de resolução por prioridade.
ordem_prioridade = ["Crítica", "Alta", "Média", "Baixa"]
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(
    data=fechados,
    x="prioridade",
    y="tempo_resolucao_horas",
    order=ordem_prioridade,
    ax=ax,
)
ax.set_title("Tempo de resolução por prioridade")
ax.set_xlabel("Prioridade")
ax.set_ylabel("Horas até a resolução")
fig.tight_layout()
fig.savefig(PASTA_IMAGENS / "eda_tempo_resolucao_prioridade.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Gráfico 5: distribuição das avaliações de satisfação.
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=satisfacao_contagem, x="nota", y="quantidade_respostas", ax=ax)
ax.set_title("Distribuição da satisfação dos usuários")
ax.set_xlabel("Nota de satisfação (1 a 5)")
ax.set_ylabel("Quantidade de respostas")
fig.tight_layout()
fig.savefig(PASTA_IMAGENS / "eda_satisfacao.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print(f"\nGráficos salvos em: {PASTA_IMAGENS}")
