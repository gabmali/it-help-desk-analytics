"""Carrega a base de chamados tratada em um banco de dados SQLite."""

from pathlib import Path
import sqlite3

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_CSV = PASTA_PROJETO / "data" / "chamados_help_desk_tratados.csv"
ARQUIVO_SCHEMA = PASTA_PROJETO / "sql" / "schema.sql"
ARQUIVO_BANCO = PASTA_PROJETO / "data" / "help_desk.db"


def converter_data(valor):
    """Converte uma data do Pandas para texto ISO, formato usado no SQLite."""
    if pd.isna(valor):
        return None
    return pd.Timestamp(valor).strftime("%Y-%m-%d %H:%M:%S")


def criar_registros(dados: pd.DataFrame) -> list[tuple]:
    """Converte cada linha da tabela em uma tupla pronta para inserção SQL."""
    registros = []
    for _, linha in dados.iterrows():
        satisfacao = None if pd.isna(linha["satisfacao_usuario"]) else int(linha["satisfacao_usuario"])
        tempo = None if pd.isna(linha["tempo_resolucao_horas"]) else float(linha["tempo_resolucao_horas"])
        sla_cumprido = None if pd.isna(linha["sla_cumprido"]) else str(linha["sla_cumprido"])

        registros.append((
            str(linha["id_chamado"]),
            converter_data(linha["data_abertura"]),
            converter_data(linha["data_encerramento"]),
            str(linha["departamento"]),
            str(linha["tecnico"]),
            str(linha["categoria"]),
            str(linha["descricao_problema"]),
            str(linha["prioridade"]),
            str(linha["status"]),
            tempo,
            int(linha["sla_previsto_horas"]),
            sla_cumprido,
            str(linha["situacao_sla_na_data_corte"]),
            satisfacao,
            converter_data(linha["data_corte_analise"]),
        ))
    return registros


def carregar_banco() -> int:
    """Cria a tabela e substitui os registros pela versão atual do CSV tratado."""
    dados = pd.read_csv(
        ARQUIVO_CSV,
        encoding="utf-8-sig",
        parse_dates=["data_abertura", "data_encerramento", "data_corte_analise"],
    )
    registros = criar_registros(dados)
    comandos_sql = ARQUIVO_SCHEMA.read_text(encoding="utf-8")
    instrucao_insert = """
        INSERT INTO chamados (
            id_chamado, data_abertura, data_encerramento, departamento, tecnico,
            categoria, descricao_problema, prioridade, status, tempo_resolucao_horas,
            sla_previsto_horas, sla_cumprido, situacao_sla_na_data_corte,
            satisfacao_usuario, data_corte_analise
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    conexao = sqlite3.connect(ARQUIVO_BANCO)
    try:
        with conexao:
            conexao.executescript(comandos_sql)
            # A tabela é recarregada para não duplicar chamados ao executar novamente.
            conexao.execute("DELETE FROM chamados")
            conexao.executemany(instrucao_insert, registros)
            total = conexao.execute("SELECT COUNT(*) FROM chamados").fetchone()[0]
    finally:
        conexao.close()

    return total


if __name__ == "__main__":
    total_carregado = carregar_banco()
    print(f"Banco SQLite criado/atualizado em: {ARQUIVO_BANCO}")
    print(f"Chamados carregados: {total_carregado}")
