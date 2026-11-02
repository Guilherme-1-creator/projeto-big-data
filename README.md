# Representatividade Política no Brasil — Big Data

## Sobre o projeto

Este projeto tem como objetivo analisar a representatividade étnico-racial e de gênero nas eleições gerais brasileiras, utilizando dados públicos disponibilizados pelo Tribunal Superior Eleitoral (TSE).

A análise considera as eleições gerais de 2014, 2018 e 2022, buscando identificar diferenças na participação política entre grupos raciais e de gênero, além de observar sua presença entre os candidatos eleitos.

O projeto está alinhado principalmente à **ODS 18 — Igualdade Étnico-Racial**, com contribuição complementar à **ODS 5 — Igualdade de Gênero**.

## Objetivos

- Analisar a distribuição de candidaturas por raça/cor e gênero.
- Identificar a quantidade e a proporção de candidatos eleitos.
- Comparar as taxas de sucesso eleitoral entre diferentes grupos.
- Investigar a relação entre raça/cor e gênero por meio de indicadores interseccionais.
- Observar a evolução da representatividade política ao longo das eleições gerais.
- Permitir análises por região, estado e cargo político.

## Fonte dos dados

Os dados utilizados são provenientes do **Tribunal Superior Eleitoral (TSE)**, por meio dos arquivos de consulta de candidaturas (`consulta_cand`).

São considerados os seguintes anos eleitorais:

- 2014
- 2018
- 2022

O projeto utiliza exclusivamente dados de eleições gerais, permitindo comparar os resultados de diferentes disputas eleitorais ao longo do período analisado.

Os arquivos CSV são armazenados em `etl/bases/` e processados antes de serem inseridos no banco de dados PostgreSQL.

Fonte: https://dadosabertos.tse.jus.br/

## Tecnologias utilizadas

- **Python:** processamento e análise dos dados.
- **Pandas:** leitura, limpeza e transformação dos arquivos CSV.
- **SQLAlchemy:** conexão e integração com o banco de dados.
- **PostgreSQL:** armazenamento dos dados tratados.
- **Aiven:** serviço de banco de dados em nuvem.
- **Terraform:** infraestrutura como código para criação do banco na Aiven.
- **Streamlit:** desenvolvimento do dashboard interativo.
- **Plotly:** construção dos gráficos.
- **Git e GitHub:** versionamento do projeto.

## Arquitetura do projeto

O funcionamento está organizado em quatro etapas principais:

1. **Extração:** leitura dos arquivos CSV disponibilizados pelo TSE.
2. **Transformação:** seleção de colunas, tratamento de valores ausentes, padronização de partidos e anonimização dos CPFs.
3. **Carga:** inserção dos dados tratados na tabela `candidatos_historico`, no PostgreSQL hospedado na Aiven.
4. **Visualização:** consulta aos dados armazenados e apresentação dos indicadores no dashboard desenvolvido com Streamlit.

```text
Dados abertos do TSE
        |
        v
Arquivos CSV (consulta_cand)
        |
        v
ETL - Python e Pandas
        |
        v
Tratamento e anonimização
        |
        v
PostgreSQL na Aiven
        |
        v
Dashboard - Streamlit
        |
        v
Gráficos e indicadores
```

O Terraform é utilizado para provisionar a infraestrutura do banco de dados na Aiven.

## Estrutura do repositório

```text
projeto-big-data/
│
├── dashboard/
│   └── app.py
│
├── etl/
│   ├── bases/
│   │   ├── consulta_cand_2014_BRASIL.csv
│   │   ├── consulta_cand_2018_BRASIL.csv
│   │   └── consulta_cand_2022_BRASIL.csv
│   │
│   └── processamento.py
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── .env
├── .gitignore
└── requirements.txt
```

## Tratamento dos dados e regras de negócio

O processamento dos dados segue as seguintes regras:

**1. Seleção de informações**

São utilizadas informações dos arquivos do TSE, como:

- Ano da eleição;
- Unidade da Federação;
- Cargo político;
- CPF do candidato;
- Raça/cor;
- Gênero;
- Partido;
- Situação do candidato no turno.

O nome do candidato e o CPF original não são mantidos na tabela final.

**2. Anonimização**

O CPF é tratado e convertido em um identificador anônimo por meio do algoritmo SHA-256, combinado com um salt configurado em variável de ambiente.

**3. Tratamento de valores ausentes**

Durante o ETL, são removidos os registros que apresentam valores nulos nos campos considerados pelo processamento.

Essa decisão busca evitar que informações incompletas interfiram no cálculo dos indicadores e nas comparações entre os grupos analisados.

Como consequência, os resultados representam os registros que possuem informações completas nos campos considerados pelo processamento. Essa escolha também pode excluir candidaturas válidas que apresentem algum campo não preenchido.

**4. Padronização partidária**

Algumas siglas históricas são convertidas para suas denominações posteriores, como PMDB para MDB, PR para PL e PRB para REPUBLICANOS.

**5. Classificação dos resultados**

São classificados como eleitos os candidatos cuja situação no turno corresponde a:

- ELEITO;
- ELEITO POR QP;
- ELEITO POR MÉDIA.

As demais situações são agrupadas como não eleitas no dashboard.

**6. Análise interseccional**

Os dados de raça/cor e gênero são cruzados para permitir a comparação da taxa de sucesso eleitoral entre diferentes grupos.

## Indicadores do dashboard

O dashboard apresenta quatro indicadores principais:

| Indicador | Descrição |
|---|---|
| Total de candidaturas | Quantidade de registros de candidatos após a aplicação dos filtros. |
| Total de eleitos | Quantidade de candidatos classificados como eleitos. |
| Taxa geral de eleição | Percentual de candidatos eleitos em relação ao total de candidaturas. |
| Percentual de eleitos negros | Participação de candidatos pretos e pardos entre os eleitos. |

Além dos indicadores, o dashboard possui quatro áreas de análise:

### 1. Étnico-Racial (ODS 18)

Apresenta a distribuição de candidaturas e resultados por raça/cor, com alternância entre volume absoluto e proporção percentual. Também apresenta taxas de conversão eleitoral por grupo racial.

### 2. Interseccionalidade (ODS 18 + ODS 5)

Cruza raça/cor e gênero por meio de uma matriz visual (heatmap), permitindo observar a taxa de sucesso eleitoral dos diferentes grupos.

### 3. Evolução Histórica

Apresenta a evolução da quantidade de candidatos eleitos por raça/cor ao longo das eleições analisadas.

### 4. Drill-Down e Alternador de Métricas

Permite detalhar os resultados por região ou estado (UF), alternando entre o total absoluto de eleitos e a média de eleitos.

## Filtros interativos

O dashboard disponibiliza filtros dinâmicos para:

- Ano eleitoral;
- Região;
- Estado (UF);
- Sexo/gênero;
- Raça/cor;
- Cargo político.

Os filtros podem ser combinados para permitir diferentes recortes da análise.

## Os 5 Vs do Big Data

**Volume:** os arquivos de candidaturas do TSE são processados em lotes de até 100 mil registros, reduzindo a necessidade de carregar todos os dados simultaneamente na memória.

**Variedade:** o projeto trabalha principalmente com dados estruturados em arquivos CSV, contendo informações eleitorais organizadas em colunas.

**Velocidade:** o processamento ocorre em lote, por meio de scripts Python executados conforme a necessidade de atualização dos dados.

**Veracidade:** são aplicados procedimentos de limpeza, identificação de valores ausentes, padronização de informações e tratamento de inconsistências presentes nos arquivos.

**Valor:** os dados são transformados em indicadores que ajudam a compreender a participação de diferentes grupos raciais e de gênero na política brasileira, contribuindo para discussões relacionadas à igualdade e à representatividade.

## Classificação dos dados

Os dados utilizados são predominantemente estruturados, pois estão organizados em arquivos CSV com campos definidos.

Entre os principais campos utilizados estão:

| Campo | Descrição |
|---|---|
| `ano_eleicao` | Ano da eleição. |
| `sg_uf` | Sigla da unidade federativa. |
| `ds_cargo` | Cargo político disputado. |
| `ds_cor_raca` | Autodeclaração de raça/cor. |
| `ds_genero` | Informação de gênero do candidato. |
| `sg_partido` | Sigla do partido político. |
| `ds_sit_tot_turno` | Situação do candidato no turno. |
| `id_candidato_anonimo` | Identificador gerado a partir do CPF anonimizado. |

## LGPD e segurança dos dados

O projeto utiliza dados públicos disponibilizados pelo TSE e adota medidas para reduzir a exposição de informações pessoais.

Entre as medidas implementadas:

- Remoção do nome do candidato durante o processamento.
- Anonimização do CPF por meio de hash SHA-256 com salt.
- Utilização de variáveis de ambiente para armazenar informações de conexão.
- Exclusão de arquivos de configuração sensíveis do versionamento por meio do `.gitignore`.

As informações de raça/cor e gênero são utilizadas conforme os registros disponibilizados pelo TSE, sem inferência de características dos candidatos.

## Como executar o projeto

### 1. Pré-requisitos

- Python 3.10 ou superior.
- PostgreSQL disponível e acessível.
- Conta e serviço PostgreSQL configurados na Aiven.
- Terraform instalado, caso seja necessário provisionar a infraestrutura.

### 2. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd projeto-big-data
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=sua_url_de_conexao_postgresql
CPF_SALT=uma_chave_aleatoria_e_segura
```

Substitua os valores pelos dados correspondentes ao seu ambiente.


### 5. Executar o processamento dos dados

Com os arquivos CSV dentro de `etl/bases/`, execute na raiz do projeto:

```bash
python etl/processamento.py
```

O script realiza o tratamento dos arquivos e insere os registros na tabela `candidatos_historico` do PostgreSQL.

### 6. Executar o dashboard

Na raiz do projeto, execute:

```bash
streamlit run dashboard/app.py
```

O Streamlit disponibilizará o dashboard no navegador.

## Infraestrutura com Terraform

A pasta `terraform/` contém os arquivos utilizados para provisionar o banco PostgreSQL na Aiven:

- `main.tf`: configuração do provedor Aiven e criação do serviço PostgreSQL.
- `variables.tf`: declaração da variável de autenticação da API.
- `outputs.tf`: disponibilização da URI de conexão do banco como saída sensível.

A variável `aiven_api_token` deve ser fornecida de forma segura durante a execução do Terraform.

## Considerações finais

O projeto transforma dados públicos eleitorais em informações que permitem analisar a representatividade étnico-racial e de gênero nas eleições gerais brasileiras.

Por meio do processamento em Python, armazenamento em PostgreSQL e visualização interativa em Streamlit, busca-se facilitar a identificação de diferenças na participação política e contribuir para a discussão sobre representatividade no Brasil.
