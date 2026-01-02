from __future__ import annotations

from langchain_core.documents import Document

from data_utils import Movie
from retrieval import config


def create_docs_to_embedd(movies: list[Movie], config: config.RetrievalExpsConfig) -> list[Document]:
    """
    Convierte una lista de objetos `Movie` a una lista the objetos `Document`(usada por Langchain).
    En esta función se decide que parte de los datos será usado como embeddings y que parte como metadata.
    """
    movies_as_docs = []
    for movie in movies:
        content = config.text_to_embed_fn(movie)
        metadata = movie.model_dump()
        doc = Document(page_content=content, metadata=metadata)
        movies_as_docs.append(doc)

    return movies_as_docs


## Posibles funciones para usar como `text_to_embed_fn` en `RetrievalExpsConfig` ##


def get_synopsys_txt(movie: Movie) -> str:
    return movie.synopsis


def get_enriched_txt(movie: Movie) -> str:
    """
    Crea un texto enriquecido con múltiples metadatos de la película.
    Incluye: título, género, director, país, elenco y sinopsis.
    """
    # Limpiamos los campos que pueden tener separadores
    genres = movie.genre_tags.replace(";", ", ") if movie.genre_tags else ""
    cast = movie.cast_top_5.replace(";", ", ") if movie.cast_top_5 else ""

    enriched_text = f"""Título: {movie.title_es}
Géneros: {genres}
Director: {movie.director_top_5}
País: {movie.country}
Elenco: {cast}
Sinopsis: {movie.synopsis}"""

    return enriched_text

# def ...
