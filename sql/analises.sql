-- 1. Problema técnico mais frequente
SELECT descricao_problema, COUNT(*) AS quantidade_chamados
FROM chamados
GROUP BY descricao_problema
ORDER BY quantidade_chamados DESC, descricao_problema
LIMIT 1;

-- 2. Departamento com mais chamados
SELECT departamento, COUNT(*) AS quantidade_chamados
FROM chamados
GROUP BY departamento
ORDER BY quantidade_chamados DESC, departamento
LIMIT 1;

-- 3. Técnico com mais chamados fechados (volume, não uma medida isolada de qualidade)
SELECT tecnico, COUNT(*) AS chamados_fechados
FROM chamados
WHERE status = 'Fechado'
GROUP BY tecnico
ORDER BY chamados_fechados DESC, tecnico
LIMIT 1;

-- 4. Tempo médio de resolução dos chamados fechados
SELECT ROUND(AVG(tempo_resolucao_horas), 2) AS media_resolucao_horas
FROM chamados
WHERE status = 'Fechado';

-- 5. Percentual de chamados fechados que não cumpriram o SLA
SELECT
    SUM(CASE WHEN sla_cumprido = 'Não' THEN 1 ELSE 0 END) AS fechados_fora_sla,
    COUNT(*) AS total_fechados,
    ROUND(100.0 * SUM(CASE WHEN sla_cumprido = 'Não' THEN 1 ELSE 0 END) / COUNT(*), 2)
        AS percentual_fora_sla
FROM chamados
WHERE status = 'Fechado';

-- 6. Volume de chamados abertos por mês
SELECT strftime('%Y-%m', data_abertura) AS mes, COUNT(*) AS quantidade_chamados
FROM chamados
GROUP BY mes
ORDER BY mes;

-- 7. Reincidência: mesmo problema no mesmo departamento em até 30 dias
WITH chamados_reincidentes AS (
    SELECT atual.id_chamado, atual.categoria
    FROM chamados AS atual
    WHERE EXISTS (
        SELECT 1
        FROM chamados AS anterior
        WHERE anterior.departamento = atual.departamento
          AND anterior.descricao_problema = atual.descricao_problema
          AND (
              anterior.data_abertura < atual.data_abertura
              OR (anterior.data_abertura = atual.data_abertura
                  AND anterior.id_chamado < atual.id_chamado)
          )
          AND julianday(atual.data_abertura) - julianday(anterior.data_abertura)
              BETWEEN 0 AND 30
    )
)
SELECT
    c.categoria,
    COUNT(DISTINCT r.id_chamado) AS chamados_reincidentes,
    COUNT(*) AS total_categoria,
    ROUND(100.0 * COUNT(DISTINCT r.id_chamado) / COUNT(*), 2) AS percentual_reincidente
FROM chamados AS c
LEFT JOIN chamados_reincidentes AS r ON r.id_chamado = c.id_chamado
GROUP BY c.categoria
ORDER BY percentual_reincidente DESC, chamados_reincidentes DESC;

-- 8. Satisfação média dos usuários com chamados fechados
SELECT
    ROUND(AVG(satisfacao_usuario), 2) AS satisfacao_media,
    COUNT(satisfacao_usuario) AS respostas_recebidas,
    COUNT(*) AS chamados_fechados
FROM chamados
WHERE status = 'Fechado';

-- 9. Problemas candidatos a prevenção: frequentes e presentes em vários departamentos
SELECT
    descricao_problema,
    categoria,
    COUNT(*) AS quantidade_chamados,
    COUNT(DISTINCT departamento) AS departamentos_afetados
FROM chamados
GROUP BY descricao_problema, categoria
HAVING COUNT(*) >= 20
ORDER BY quantidade_chamados DESC, departamentos_afetados DESC
LIMIT 10;

-- 10. Indicadores de carga e atendimento por técnico
SELECT
    tecnico,
    SUM(CASE WHEN status = 'Fechado' THEN 1 ELSE 0 END) AS chamados_fechados,
    SUM(CASE WHEN status <> 'Fechado' THEN 1 ELSE 0 END) AS chamados_abertos,
    ROUND(AVG(CASE WHEN status = 'Fechado' THEN tempo_resolucao_horas END), 2)
        AS media_resolucao_horas,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Fechado' AND sla_cumprido = 'Sim' THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN status = 'Fechado' THEN 1 ELSE 0 END), 0),
        2
    ) AS percentual_sla_cumprido
FROM chamados
GROUP BY tecnico
ORDER BY chamados_fechados DESC, tecnico;

-- 11. Chamados abertos atrasados, para localizar filas que precisam de atenção
SELECT departamento, COUNT(*) AS chamados_abertos_atrasados
FROM chamados
WHERE status <> 'Fechado'
  AND situacao_sla_na_data_corte = 'Atrasado'
GROUP BY departamento
ORDER BY chamados_abertos_atrasados DESC, departamento;
