"""Gera uma base fictícia e reproduzível de chamados de Help Desk."""

from pathlib import Path

import numpy as np
import pandas as pd


# A semente fixa faz o mesmo script gerar os mesmos dados em toda execução.
SEMENTE = 42
TOTAL_CHAMADOS = 1200
DATA_INICIO = pd.Timestamp("2025-01-01 00:00:00")
DATA_CORTE = pd.Timestamp("2025-12-31 23:59:00")
PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_SAIDA = PASTA_PROJETO / "data" / "chamados_help_desk.csv"

departamentos = [
    "Financeiro", "Recursos Humanos", "Vendas", "Operações",
    "Marketing", "Jurídico", "Atendimento ao Cliente", "TI",
]
tecnicos = ["TEC-001", "TEC-002", "TEC-003", "TEC-004", "TEC-005", "TEC-006"]
prioridades = ["Crítica", "Alta", "Média", "Baixa"]

# Cada tipo de problema tem uma categoria e um peso de ocorrência.
# Pesos maiores tornam alguns problemas mais frequentes na amostra.
problemas = [
    ("Acesso e contas", "Senha bloqueada", 0.12),
    ("Acesso e contas", "Falha no login corporativo", 0.09),
    ("Acesso e contas", "Permissão insuficiente em pasta", 0.06),
    ("Hardware", "Notebook lento", 0.09),
    ("Hardware", "Teclado ou mouse com defeito", 0.05),
    ("Hardware", "Computador não liga", 0.05),
    ("Rede", "Wi-Fi instável", 0.10),
    ("Rede", "Sem acesso à internet", 0.08),
    ("Rede", "VPN não conecta", 0.06),
    ("Software", "Aplicativo corporativo fecha sozinho", 0.08),
    ("Software", "Erro ao instalar atualização", 0.05),
    ("Software", "Licença de software expirada", 0.04),
    ("Impressão", "Impressora não imprime", 0.05),
    ("E-mail", "E-mail não sincroniza", 0.04),
    ("Segurança", "Suspeita de e-mail de phishing", 0.03),
    ("Telefonia", "Telefone sem áudio", 0.01),
]

# Horas máximas para resposta/resolução conforme a prioridade.
sla_por_prioridade = {"Crítica": 4, "Alta": 8, "Média": 24, "Baixa": 72}


def gerar_base() -> pd.DataFrame:
    """Cria os chamados e devolve os dados em uma tabela do Pandas."""
    rng = np.random.default_rng(SEMENTE)
    pesos_problemas = [problema[2] for problema in problemas]
    registros = []

    for numero in range(1, TOTAL_CHAMADOS + 1):
        # Distribui as aberturas pelo ano e mantém datas próximas para a fila em andamento.
        # Chamados abertos só podem estar entre os 45 dias anteriores à data de corte.
        ultimo_dia_abertura = DATA_CORTE - pd.Timedelta(minutes=15)
        minutos_janela = int((ultimo_dia_abertura - DATA_INICIO).total_seconds() // 60)
        abertura = DATA_INICIO + pd.Timedelta(minutes=int(rng.integers(0, minutos_janela + 1)))
        esta_aberto = (
            abertura >= DATA_CORTE - pd.Timedelta(days=45)
            and rng.random() < 0.40
        )

        departamento = str(rng.choice(departamentos))
        tecnico = str(rng.choice(tecnicos, p=[0.22, 0.20, 0.18, 0.16, 0.14, 0.10]))
        prioridade = str(rng.choice(prioridades, p=[0.05, 0.20, 0.50, 0.25]))
        categoria, descricao, _ = problemas[int(rng.choice(len(problemas), p=pesos_problemas))]
        sla_horas = sla_por_prioridade[prioridade]

        if esta_aberto:
            encerramento = pd.NaT
            tempo_resolucao = np.nan
            status = str(rng.choice(["Aberto", "Em andamento"], p=[0.35, 0.65]))
            horas_decorridas = (DATA_CORTE - abertura).total_seconds() / 3600
            sla_cumprido = ""
            situacao_sla = "Atrasado" if horas_decorridas > sla_horas else "Dentro do prazo"
            satisfacao = np.nan
        else:
            # Simula se o atendimento foi concluído dentro do prazo.
            taxa_sla = {"Crítica": 0.72, "Alta": 0.80, "Média": 0.88, "Baixa": 0.93}[prioridade]
            previa_cumprimento = rng.random() < taxa_sla
            if previa_cumprimento:
                tempo_simulado = float(rng.uniform(0.25, sla_horas))
            else:
                tempo_simulado = float(rng.uniform(sla_horas * 1.05, sla_horas * 2.5))

            # Um chamado não pode ser encerrado depois da data de corte da análise.
            horas_ate_corte = (DATA_CORTE - abertura).total_seconds() / 3600
            tempo_resolucao = min(tempo_simulado, horas_ate_corte)
            cumpriu_sla = tempo_resolucao <= sla_horas

            encerramento = abertura + pd.Timedelta(hours=tempo_resolucao)
            status = "Fechado"
            sla_cumprido = "Sim" if cumpriu_sla else "Não"
            situacao_sla = "Cumprido" if cumpriu_sla else "Não cumprido"

            # Notas mais altas são mais prováveis quando o SLA é cumprido.
            if cumpriu_sla:
                satisfacao = int(rng.choice([1, 2, 3, 4, 5], p=[0.02, 0.04, 0.14, 0.35, 0.45]))
            else:
                satisfacao = int(rng.choice([1, 2, 3, 4, 5], p=[0.12, 0.22, 0.32, 0.24, 0.10]))

        registros.append({
            "id_chamado": f"HD-{numero:06d}",
            "data_abertura": abertura,
            "data_encerramento": encerramento,
            "departamento": departamento,
            "tecnico": tecnico,
            "categoria": categoria,
            "descricao_problema": descricao,
            "prioridade": prioridade,
            "status": status,
            "tempo_resolucao_horas": round(tempo_resolucao, 2) if pd.notna(tempo_resolucao) else np.nan,
            "sla_previsto_horas": sla_horas,
            "sla_cumprido": sla_cumprido,
            "situacao_sla_na_data_corte": situacao_sla,
            "satisfacao_usuario": satisfacao,
            "data_corte_analise": DATA_CORTE,
        })

    return pd.DataFrame(registros)


if __name__ == "__main__":
    dados = gerar_base()
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d %H:%M:%S")

    print(f"Base criada: {ARQUIVO_SAIDA}")
    print(f"Total de chamados: {len(dados)}")
    print(f"Chamados fechados: {(dados['status'] == 'Fechado').sum()}")
    print(f"Chamados ainda abertos: {(dados['status'] != 'Fechado').sum()}")
