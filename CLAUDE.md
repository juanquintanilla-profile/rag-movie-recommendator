# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) movie recommendation system focused on the **retrieval module**. The system takes user queries (starting with "El usuario busca...") and retrieves the most relevant movies from a database of 6,521 Spanish-language films using embeddings and vector similarity search.

The project is designed as a learning exercise to experiment with different retrieval approaches, embedding models, and preprocessing techniques, tracked using MLFlow.

## Core Architecture

### Data Flow
1. **Indexing Pipeline** (`retrieval/main.py:generate_index_pipeline`):
   - Loads movie data from `retrieval/data/movies_data.json`
   - Converts `Movie` objects to text using configurable function (`_text_to_embed_fn`)
   - Generates embeddings using HuggingFace models
   - Creates FAISS index for similarity search
   - Caches embeddings locally in `.cache/` directory

2. **Retrieval Pipeline** (`retrieval/main.py:retrieval_pipeline`):
   - Preprocesses query using configurable function (`_query_prepro_fn`)
   - Performs similarity search against FAISS index
   - Returns top-10 most similar movies

3. **Evaluation** (`retrieval/evaluation.py`):
   - Uses 300 query-movie pairs from `retrieval/data/eval_queries.json`
   - Main metric: MRR@10 (Mean Reciprocal Rank)
   - Additional metrics: `perc_top_10`, `secs_per_query`, `index_gen_minutes`

### Key Components

**Data Models** (`data_utils/schemas.py`):
- `Movie`: Pydantic model with fields: `movie_id`, `title_es`, `title_original`, `duration_mins`, `year`, `country`, `genre_tags`, `director_top_5`, `cast_top_5`, `synopsis`, etc.
- Genre tags and cast/crew fields are semicolon-separated strings

**Configuration** (`retrieval/config.py`):
- `RetrievalExpsConfig`: Central configuration class
- All attributes are automatically logged to MLFlow
- `index_config_unique_id`: Unique identifier for caching based on model + text function + normalization settings

**Caching System**:
- Embeddings cached in `retrieval/.cache/faiss_{index_config_unique_id}/`
- To force regeneration, either delete cache or **rename the `_text_to_embed_fn` function**
- Cache relies on function name matching - changing implementation without renaming will use stale cache

## Commands

### Environment Setup

**Linux/Mac**:
```bash
conda env create -f environment.yml
conda activate movies
```

**Windows**:
```bash
conda env create -f env_windows.yml
conda activate movies
```

### Data Download
Required before first run:
1. Movies data: Download to `retrieval/data/movies_data.json` from [Google Drive link](https://drive.google.com/file/d/1tcc_12DHMsVYPSLS_11Nhu83KMFrwMWQ/view?usp=sharing)
2. Evaluation data: Download to `retrieval/data/eval_queries.json` from [Google Drive link](https://drive.google.com/file/d/1yKNu1dCnfpC3C8YYGRL0ct29ZyDtw2Dw/view?usp=drive_link)

### MLFlow Server

Start tracking server (required before running experiments):
```bash
mlflow server --host 127.0.0.1 --port 8080
```
Access dashboard at: `http://localhost:8080/`

### Run Experiment

Execute a retrieval experiment:
```bash
python retrieval/main.py
```

This will:
1. Load configuration from `retrieval/config.py`
2. Generate embeddings (or load from cache)
3. Run evaluation on 300 test queries
4. Log metrics and parameters to MLFlow

## Experimentation Workflow

To run experiments, modify **only these three files**:

1. **`retrieval/config.py`**:
   - Change `model_name` (any HuggingFace model, e.g., `"all-MiniLM-L12-v2"`)
   - Change `normalize_embeddings` (bool)
   - Set `_text_to_embed_fn` to different text generation function
   - Set `_query_prepro_fn` to different query preprocessing function

2. **`retrieval/indexing_pipeline_utils.py`**:
   - Define new functions: `Movie -> str` for embedding generation
   - Example: `get_synopsys_txt(movie: Movie) -> str`
   - **Important**: Use a new function name to avoid cache issues

3. **`retrieval/retrieval_pipeline_utils.py`**:
   - Define new query preprocessing functions: `str -> str`
   - Example: `clean_query_txt(query: str) -> str`

## Important Notes

### Windows Path Restrictions
Due to FAISS library issues, the repository path **cannot contain "ñ" or accented characters**. Invalid example: `C:/Users/Desktop/04_Diseño_y_Estrategias_en_Producción_para_Soluciones_de_IA/`

### Embedding Generation Performance
- Without GPU, embedding generation can take 30-60+ minutes
- Cache system avoids regeneration for same configuration
- **Cache invalidation**: Rename the `_text_to_embed_fn` function when changing its implementation

### MLFlow Integration
- All `RetrievalExpsConfig` attributes are automatically logged as parameters
- Experiment name: "Embeddings Retrieval"
- Metrics logged: `mean_mrr10`, `perc_top_10`, `secs_per_query`, `index_gen_minutes`
- Rank distribution histogram saved as artifact

## Key Files Reference

- `retrieval/main.py:32` - Load embedder with model configuration
- `retrieval/main.py:44` - Index generation pipeline
- `retrieval/main.py:76` - Retrieval pipeline
- `retrieval/config.py:22` - Text-to-embed function configuration
- `retrieval/config.py:29` - Query preprocessing function configuration
- `retrieval/config.py:40` - Cache ID generation logic
- `retrieval/evaluation.py:122` - MRR calculation
- `data_utils/db_utils.py:45` - Movie data loading from JSON
