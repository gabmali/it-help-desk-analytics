# Dicionário de dados

## Base de chamados

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `id_chamado` | Texto | Identificador único, por exemplo `HD-000001`. |
| `data_abertura` | Data e hora | Momento em que o chamado foi registrado. |
| `data_encerramento` | Data e hora, nulo para abertos | Momento em que o atendimento terminou. |
| `departamento` | Texto | Departamento que solicitou suporte. |
| `tecnico` | Texto | Identificação fictícia do técnico responsável. |
| `categoria` | Texto | Grupo amplo do problema, como Rede ou Hardware. |
| `descricao_problema` | Texto | Tipo específico do problema. |
| `prioridade` | Texto | Crítica, Alta, Média ou Baixa. |
| `status` | Texto | Aberto, Em andamento ou Fechado. |
| `tempo_resolucao_horas` | Decimal, nulo para abertos | Tempo entre abertura e encerramento. |
| `sla_previsto_horas` | Inteiro | Prazo do SLA definido pela prioridade. |
| `sla_cumprido` | Sim/Não, nulo para abertos | Resultado do SLA para um chamado fechado. |
| `situacao_sla_na_data_corte` | Texto | Cumprido, Não cumprido, Atrasado ou Dentro do prazo. |
| `satisfacao_usuario` | Inteiro de 1 a 5, nulo para abertos | Avaliação fictícia após o fechamento. |
| `data_corte_analise` | Data e hora | Referência usada para avaliar chamados ainda abertos. |

## Regras da simulação

- Período das aberturas: 01/01/2025 a 31/12/2025.
- Data de corte: 31/12/2025 às 23:59.
- Semente aleatória: 42; a geração é reproduzível.
- Prazos simulados: Crítica 4h, Alta 8h, Média 24h e Baixa 72h.
- Chamados que permanecem abertos são selecionados entre os 45 dias anteriores à data de corte para representar uma fila ativa recente.
- Chamados em aberto não têm encerramento, tempo de resolução, resultado final do SLA ou nota de satisfação.
- A satisfação foi simulada com tendência a notas mais altas quando o SLA foi cumprido.
- Os dados são totalmente fictícios e não devem ser interpretados como referência de mercado.
