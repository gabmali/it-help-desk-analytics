-- Tabela principal: uma linha representa um chamado de TI.
CREATE TABLE IF NOT EXISTS chamados (
    id_chamado TEXT PRIMARY KEY,
    data_abertura TEXT NOT NULL,
    data_encerramento TEXT,
    departamento TEXT NOT NULL,
    tecnico TEXT NOT NULL,
    categoria TEXT NOT NULL,
    descricao_problema TEXT NOT NULL,
    prioridade TEXT NOT NULL CHECK (prioridade IN ('Crítica', 'Alta', 'Média', 'Baixa')),
    status TEXT NOT NULL CHECK (status IN ('Aberto', 'Em andamento', 'Fechado')),
    tempo_resolucao_horas REAL,
    sla_previsto_horas INTEGER NOT NULL CHECK (sla_previsto_horas > 0),
    sla_cumprido TEXT CHECK (sla_cumprido IN ('Sim', 'Não')),
    situacao_sla_na_data_corte TEXT NOT NULL CHECK (
        situacao_sla_na_data_corte IN ('Cumprido', 'Não cumprido', 'Atrasado', 'Dentro do prazo')
    ),
    satisfacao_usuario INTEGER CHECK (satisfacao_usuario BETWEEN 1 AND 5),
    data_corte_analise TEXT NOT NULL,
    CHECK (data_encerramento IS NULL OR data_encerramento >= data_abertura),
    CHECK (
        (status = 'Fechado'
            AND data_encerramento IS NOT NULL
            AND tempo_resolucao_horas IS NOT NULL
            AND sla_cumprido IN ('Sim', 'Não'))
        OR
        (status IN ('Aberto', 'Em andamento')
            AND data_encerramento IS NULL
            AND tempo_resolucao_horas IS NULL
            AND sla_cumprido IS NULL
            AND satisfacao_usuario IS NULL)
    )
);

-- Índices ajudam consultas que filtram por data, departamento ou técnico.
CREATE INDEX IF NOT EXISTS idx_chamados_data_abertura ON chamados (data_abertura);
CREATE INDEX IF NOT EXISTS idx_chamados_departamento ON chamados (departamento);
CREATE INDEX IF NOT EXISTS idx_chamados_tecnico ON chamados (tecnico);
