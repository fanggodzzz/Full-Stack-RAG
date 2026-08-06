# Full-Stack-RAG

## Repository

Public GitHub repository: https://github.com/<your-username>/Full-Stack-RAG

Replace the placeholder above with the public repository that contains the complete, reproducible implementation for this project.

## Project Overview

Full-Stack-RAG is a Python-based retrieval and evaluation pipeline for a Spring documentation corpus. It crawls and processes source pages, builds BM25 and Word2Vec-based retrieval models, runs the full query set, and writes evaluation artifacts for the report.

## Repository Contents

- `Data/`: checked-in dataset artifacts, including raw documents, processed chunks, metadata, and the query/evaluation sets.
- `Document_processor/`: HTML, Markdown, and text preprocessing logic.
- `Models/`: BM25, Word2Vec, and hybrid retrieval implementations.
- `Evaluation/`: saved evaluation outputs used to generate the report tables.
- `requirements.txt`: pinned Python dependencies.
- `README.md`: setup and execution instructions.

## Dataset

The dataset is included in the repository under `Data/`, so the project can be run without re-crawling.

If you need to rebuild the dataset from scratch, use the crawler and processor pipeline:

1. List the seed URLs in `sources.txt`.
2. Run `python web_crawler.py` to crawl and save raw documents and metadata.
3. Run `python data_processing.py` to convert the raw files into processed chunks and corpus files.

The repository also includes the generated query set and answer files under `Data/queries/`.

## Reproducibility

The project is configured for reproducible runs with fixed model settings and pinned dependencies:

- Word2Vec training uses a fixed seed of `42` in `Models/vector_model.py`.
- The dependency versions are pinned in `requirements.txt`.
- The checked-in dataset removes the need for external downloads during grading or evaluation.

To keep results consistent, run the project with the same Python version and dependency set used to generate the saved artifacts.

## Setup

```powershell
py -3.12 -m venv rag-env
rag-env\Scripts\activate
pip install -r requirements.txt
```

## Reproduce All Results

Run the full pipeline from the project root with a single command:

```powershell
python main.py
```

This command:

1. Trains the BM25 and Word2Vec retrieval models.
2. Loads the query set from `Data/queries/queries.jsonl`.
3. Produces BM25, Word2Vec, and hybrid rankings for every query.
4. Writes evaluation summaries to `Evaluation/evaluation_results.txt` and `Evaluation/question_status.txt`.

## Generated Outputs

- `Models/index/bm25.pkl`: serialized BM25 model.
- `Models/index/word2vec.model`: trained Word2Vec model.
- `Models/index/doc_vectors.pkl`: document vectors used for dense retrieval.
- `Data/queries/<query_id>/`: per-query ranking files and retrieved chunks.
- `Evaluation/evaluation_results.txt`: query-by-query evaluation log.
- `Evaluation/question_status.txt`: answerable/unanswerable query summary.

## Notes

- The crawler uses `sources.txt` as its seed list.
- The main pipeline does not require interactive input.
- If you regenerate the dataset, rerun `python main.py` to refresh the model indexes and evaluation files.
