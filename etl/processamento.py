import hashlib
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. Carregar variáveis de ambiente do ficheiro .env
load_dotenv(dotenv_path=".env")

database_url = os.getenv("DATABASE_URL")
cpf_salt = os.getenv("CPF_SALT", "chave_secreta_padrao")

if not database_url:
    raise ValueError("A variável DATABASE_URL não foi encontrada no ficheiro .env")

engine = create_engine(database_url)

# 2. Seleção de colunas úteis
colunas_uteis = [
    'ANO_ELEICAO', 'SG_UF', 'DS_CARGO', 'NM_CANDIDATO', 
    'NR_CPF_CANDIDATO', 'DS_COR_RACA', 'DS_GENERO', 
    'SG_PARTIDO', 'DS_SIT_TOT_TURNO'
]

# 3. Mapeamento de padrões de texto nulo do TSE
valores_nulos_tse = [
    '#NULO#', '#NE', '#NULO', '-1', '-3', '-4', '0', '0.0',
    'NÃO DIVULGADO', 'NÃO DIVULGÁVEL', 'NÃO INFORMADO', 
    'NÃO DECLAROU', 'NÃO DECLARADO', 'SEM INFORMAÇÃO', 
    'RECUSOU-SE A DECLARAR', 'NULL', 'null', 'NONE', 'None'
]

# 4. Padronização de siglas partidárias históricas (2014-2022)
mapeamento_partidos = {
    'PMDB': 'MDB',
    'PR': 'PL',
    'PPS': 'CIDADANIA',
    'PTN': 'PODEMOS',
    'PRB': 'REPUBLICANOS'
}

def anonimizar_cpf(cpf):
    if pd.isna(cpf) or str(cpf).strip() in ['', 'None']:
        return None
    # Garante os 11 dígitos preenchendo zeros à esquerda
    cpf_limpo = str(cpf).split('.')[0].strip().zfill(11)
    # Gera o hash SHA-256 juntamente com o Salt
    return hashlib.sha256((cpf_limpo + cpf_salt).encode('utf-8')).hexdigest()

def processar_ficheiro(caminho_arquivo):
    print(f"\n--- A processar ficheiro: {caminho_arquivo} ---")
    
    leitor = pd.read_csv(
        caminho_arquivo, 
        sep=';', 
        encoding='latin-1', 
        usecols=colunas_uteis,
        dtype={'NR_CPF_CANDIDATO': str},
        na_values=valores_nulos_tse,
        chunksize=100000
    )
    
    for i, chunk in enumerate(leitor):
        # Mascarar CPF e remover PII
        chunk['ID_CANDIDATO_ANONIMO'] = chunk['NR_CPF_CANDIDATO'].apply(anonimizar_cpf)
        chunk = chunk.drop(columns=['NR_CPF_CANDIDATO', 'NM_CANDIDATO'])
        
        # Padronizar nomes antigos de partidos
        chunk['SG_PARTIDO'] = chunk['SG_PARTIDO'].replace(mapeamento_partidos)
        
        # Eliminar qualquer linha com valores nulos/ausentes
        chunk = chunk.dropna()
        
        # Padronizar todos os nomes de colunas para minúsculas
        chunk.columns = chunk.columns.str.lower()
        
        # Inserir no PostgreSQL em lotes
        chunk.to_sql(
            'candidatos_historico', 
            engine, 
            if_exists='append', 
            index=False, 
            method='multi', 
            chunksize=5000
        )
        print(f"Lote {i + 1} limpo e inserido na base de dados.")

# 5. Execução para os 3 anos eleitorais
ficheiros = [
    "etl/bases/consulta_cand_2014_BRASIL.csv",
    "etl/bases/consulta_cand_2018_BRASIL.csv",
    "etl/bases/consulta_cand_2022_BRASIL.csv"
]

for ficheiro in ficheiros:
    if os.path.exists(ficheiro):
        processar_ficheiro(ficheiro)
    else:
        print(f"Aviso: O ficheiro '{ficheiro}' não foi encontrado em etl/bases/.")

print("\nProcessamento e carga concluídos com sucesso!")