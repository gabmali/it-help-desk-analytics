# Especificação visual do relatório

## Configuração geral

- Formato da página: widescreen 16:9.
- Fundo claro, texto em azul-marinho e cores de destaque consistentes: azul para volume, verde para meta cumprida, âmbar para atenção e vermelho para atraso.
- Filtros no topo de cada página: data de abertura, departamento, técnico e prioridade.
- Exibir no cabeçalho: `IT Help Desk Analytics` e a data de corte dos dados.
- Usar unidades explícitas: chamados, horas, percentual e nota de 1 a 5.

## Página 1 — Visão geral

1. Faixa superior com título e segmentadores.
2. Linha de cartões: Total Chamados, Chamados Abertos, Chamados Fechados, Tempo Medio Resolucao (h), SLA Cumprido (%) e Satisfacao Media.
3. Faixa central: linha de chamados abertos por mês e barras horizontais de volume por departamento.
4. Faixa inferior: barras de chamados por categoria e colunas de volume por prioridade.

O eixo mensal usa a data de abertura. A linha mostra volume de solicitações registradas, não quantidade de chamados encerrados.

## Página 2 — SLA e qualidade

1. Segmentadores iguais aos da página de visão geral.
2. Cartões: SLA Cumprido (%), SLA Fora (%), Chamados Abertos Atrasados e Satisfacao Media.
3. Gráfico de barras com SLA cumprido por prioridade.
4. Tabela por técnico com chamados fechados, chamados abertos, tempo médio e percentual de SLA.
5. Tabela de chamados abertos atrasados por departamento, técnico, prioridade e data de abertura.
6. Barras de categorias com maior reincidência podem ser adicionadas quando a regra for preparada como tabela ou coluna auxiliar no modelo.

## Interações e leitura

- Os segmentadores filtram todos os visuais das duas páginas.
- Selecionar uma categoria ou departamento deve realçar os valores relacionados nos outros gráficos.
- Mostrar a quantidade de respostas junto à satisfação média.
- Em visuais de técnico, exibir volume e SLA em conjunto; não ordenar apenas pela quantidade de chamados fechados e chamar isso de eficiência.
- Indicadores de SLA de chamados fechados usam fechados como denominador. A fila aberta atrasada é um indicador de estoque na data de corte.
