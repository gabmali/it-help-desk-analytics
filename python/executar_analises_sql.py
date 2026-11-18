"""Executa as consultas do arquivo analises.sql e mostra os resultados."""

from pathlib import Path
import sqlite3


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_BANCO = PASTA_PROJETO / "data" / "help_desk.db"
ARQUIVO_CONSULTAS = PASTA_PROJETO / "sql" / "analises.sql"

texto_sql = ARQUIVO_CONSULTAS.read_text(encoding="utf-8")
consultas = [bloco.strip() for bloco in texto_sql.split(";") if bloco.strip()]

with sqlite3.connect(ARQUIVO_BANCO) as conexao:
    for numero, consulta in enumerate(consultas, start=1):
        cursor = conexao.execute(consulta)
        nomes_colunas = [coluna[0] for coluna in cursor.description]
        resultados = cursor.fetchall()

        print(f"\nConsulta {numero}")
        print(" | ".join(nomes_colunas))
        for linha in resultados:
            print(" | ".join(str(valor) for valor in linha))
