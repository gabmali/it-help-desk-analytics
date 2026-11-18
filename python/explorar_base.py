"""Explora a estrutura e os principais valores da base de chamados."""

from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_BASE = PASTA_PROJETO / "data" / "chamados_help_desk.csv"

# Lê o CSV. O arquivo foi salvo em UTF-8 com BOM para facilitar a abertura no Excel.
chamados = pd.read_csv(
    ARQUIVO_BASE,
    encoding="utf-8-sig",
    parse_dates=["data_abertura", "data_encerramento", "data_corte_analise"],
)

print("\n1. Tamanho da base")
print(f"Linhas: {chamados.shape[0]:,}")
print(f"Colunas: {chamados.shape[1]}")

print("\n2. Primeiras cinco linhas")
print(chamados.head().to_string(index=False))

print("\n3. Tipos de dados")
print(chamados.dtypes.to_string())

print("\n4. Valores ausentes por coluna")
ausentes = chamados.isna().sum().sort_values(ascending=False)
print(ausentes.to_string())

print("\n5. Quantidade de IDs duplicados")
print(chamados["id_chamado"].duplicated().sum())

print("\n6. Intervalo de datas de abertura")
print(f"De {chamados['data_abertura'].min()} até {chamados['data_abertura'].max()}")

print("\n7. Chamados por status")
print(chamados["status"].value_counts().to_string())

print("\n8. Chamados por prioridade")
print(chamados["prioridade"].value_counts().to_string())

print("\n9. Dez departamentos com mais chamados")
print(chamados["departamento"].value_counts().head(10).to_string())

print("\n10. Chamados por categoria")
print(chamados["categoria"].value_counts().to_string())

print("\n11. Dez descrições mais frequentes")
print(chamados["descricao_problema"].value_counts().head(10).to_string())

# Para médias de resolução e satisfação, usamos apenas chamados fechados.
fechados = chamados.loc[chamados["status"] == "Fechado"].copy()
print("\n12. Tempo de resolução dos chamados fechados (horas)")
print(fechados["tempo_resolucao_horas"].describe().round(2).to_string())

print("\n13. Satisfação dos chamados fechados")
print(fechados["satisfacao_usuario"].value_counts().sort_index().to_string())
print(f"Média de satisfação: {fechados['satisfacao_usuario'].mean():.2f}")

print("\n14. Cumprimento do SLA nos chamados fechados")
print(fechados["sla_cumprido"].value_counts().to_string())
percentual_sla = fechados["sla_cumprido"].eq("Sim").mean() * 100
print(f"Percentual cumprido: {percentual_sla:.1f}%")
