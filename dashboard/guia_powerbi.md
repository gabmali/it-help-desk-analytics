# Dashboard no Power BI

## Importar os dados

1. No Power BI Desktop, escolha **Obter dados > Texto/CSV**.
2. Selecione `data/chamados_help_desk_tratados.csv`.
3. Carregue a tabela e renomeie-a para `Chamados`.
4. Confira os tipos de data, número decimal, número inteiro e texto.
5. Crie a coluna `Data Abertura Dia`, a tabela `Calendario` e as medidas no arquivo `medidas_dax.dax`.
6. Relacione `Calendario[Date]` com `Chamados[Data Abertura Dia]` em relação um para muitos, com filtro do calendário para os chamados.
7. Use `Calendario[AnoMes]` (formato `yyyy-MM`) no eixo para manter a ordem cronológica e classifique `Calendario[Mes]` por `Calendario[MesNumero]`. Marque `Calendario` como tabela de datas.
8. Formate `SLA Cumprido (%)` e `SLA Fora (%)` como porcentagem; `Tempo Medio Resolucao (h)` como número decimal; e satisfação com duas casas decimais.

## Página sugerida: Visão geral

- Cartões: Total Chamados, Chamados Abertos, Chamados Fechados, Tempo Medio Resolucao (h), SLA Cumprido (%) e Satisfacao Media.
- Linha: Total Chamados por Calendario[AnoMes].
- Barras: Total Chamados por departamento e por categoria.
- Colunas: Total Chamados por prioridade.
- Barras horizontais: Chamados Fechados por técnico.
- Segmentadores: Calendario[Date], departamento, tecnico e prioridade.

## Página sugerida: SLA e qualidade

- Cartões: SLA Cumprido (%), SLA Fora (%) e Chamados Abertos Atrasados.
- Barras: SLA Cumprido (%) por prioridade e por técnico.
- Colunas: Satisfacao Media por categoria.
- Tabela: chamados em aberto atrasados por departamento, técnico e prioridade.

## Definições dos indicadores

- O tempo médio usa somente chamados fechados; campos vazios de chamados abertos não entram no cálculo.
- SLA Cumprido (%) e SLA Fora (%) usam chamados fechados como denominador.
- Chamados Abertos Atrasados usa o campo `situacao_sla_na_data_corte`; representa o estado em 31/12/2025.
- Satisfacao Media ignora notas vazias. Exiba Notas de Satisfacao junto à média para mostrar o tamanho da amostra.
- O volume de chamados fechados por técnico mede quantidade, não ajusta pela complexidade ou carga horária.
- Os dados e resultados são simulados. A taxa de SLA e a satisfação servem para demonstrar análises, não para avaliar uma empresa real.
