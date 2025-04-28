# Music Recommendation API

Este projeto implementa uma API de recomendação de músicas usando FastAPI, oferecendo diferentes estratégias de recomendação:

*   Baseada em Conteúdo (similaridade de características)
*   Baseada em Gênero/Artista
*   Filtro Colaborativo (simulado)
*   Híbrida (combinação de conteúdo e colaborativo)
*   Baseada em Popularidade (filtrada por ano/gênero)

Também inclui uma interface web simples (UI) construída com Jinja2 para interagir com a API.

## Pré-requisitos

*   Python 3.8+
*   pip

## Configuração

1.  **Clone o repositório ou baixe os arquivos.**

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd colavorete_filtering
    ```

3.  **Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    ```

4.  **Ative o ambiente virtual:**
    *   No Windows (PowerShell):
        ```powershell
        .\venv\Scripts\Activate
        ```
    *   No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

5.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Executando a API

Com o ambiente virtual ativado, execute o seguinte comando para iniciar o servidor FastAPI com Uvicorn:

```bash
uvicorn modelo:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.

## Acessando a Interface Web (UI)

Abra seu navegador e acesse `http://127.0.0.1:8000`. Você poderá navegar pelas diferentes páginas da UI para testar as recomendações.

## Endpoints da API

Além da UI, os seguintes endpoints REST estão disponíveis:

*   `GET /recommendations/content-based/{song_title}`
*   `POST /recommendations/genre-artist`
*   `GET /recommendations/collaborative/{user_id}`
*   `POST /recommendations/hybrid`
*   `GET /recommendations/popular`

Consulte o código em `modelo.py` para detalhes sobre os parâmetros e corpos de requisição.

## Análise Exploratória de Dados (EDA)

O script `eda.py` realiza uma análise básica dos dados do arquivo `top50MusicFrom2010-2019.csv` e salva alguns gráficos (histogramas, correlação, popularidade por ano) como arquivos `.png`.

Para executar a EDA:

```bash
python eda.py
```

## Dados

O arquivo `top50MusicFrom2010-2019.csv` contém os dados das músicas utilizados para as recomendações.
