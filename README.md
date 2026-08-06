# Full-Stack-RAG

A Python-based Retrieval-Augmented Generation (RAG) system for retrieving relevant information from software development documentation. The project implements a complete pipeline from web crawling and document preprocessing to BM25, Word2Vec, hybrid retrieval, and evaluation.

## GitHub Repository

**Public GitHub Repository:**
https://github.com/<your-username>/Full-Stack-RAG

> Replace `<your-username>` with your GitHub username before submission.

The repository contains the complete implementation, dataset artifacts, configuration, evaluation data, and instructions required to reproduce the experiments reported in the project report.

---

## Project Overview

Full-Stack-RAG is a retrieval and evaluation pipeline designed for software development documentation.

The system performs the following stages:

1. Crawls documentation websites.
2. Extracts and cleans relevant document content.
3. Removes unwanted HTML elements and duplicate documents.
4. Splits documents into smaller chunks.
5. Builds retrieval models using:
    - **BM25**
    - **Word2Vec**
    - **Hybrid BM25 + Word2Vec retrieval**

6. Processes a predefined set of queries.
7. Retrieves and ranks relevant documents/chunks.
8. Evaluates retrieval performance against the expected answer documents.
9. Saves the evaluation results used in the project report.

The complete pipeline can be executed using a single command.

---

## Repository Structure

```text
Full-Stack-RAG/
│
├── Data/
│   ├── documents/              # Crawled/raw documentation
│   ├── chunks/                 # Processed document chunks
│   ├── metadata/               # Document and chunk metadata
│   └── queries/                # Query and answer datasets
│       └── queries.jsonl
│
├── Document_processor/
│   ├── ...                     # HTML/Markdown/text preprocessing
│
├── Models/
│   ├── ...                     # BM25, Word2Vec, and hybrid retrieval
│   └── index/
│       ├── bm25.pkl
│       ├── word2vec.model
│       └── doc_vectors.pkl
│
├── Evaluation/
│   ├── evaluation_results.txt
│   └── question_status.txt
│
├── sources.txt                 # Seed URLs for the crawler
├── web_crawler.py              # Web crawling pipeline
├── data_processing.py          # Data preprocessing and chunking
├── main.py                     # Main reproducible pipeline
├── requirements.txt            # Pinned Python dependencies
└── README.md
```

---

## Dataset

The repository includes the dataset required to reproduce the experiments.

The `Data/` directory contains the processed documentation corpus, document/chunk metadata, queries, and expected answer information.

Because the dataset is included in the repository, users do **not** need to crawl the web again to reproduce the reported experiments.

### Rebuilding the Dataset

If the dataset needs to be regenerated, the crawler and preprocessing pipeline can be executed in the following order.

#### 1. Configure the seed URLs

The websites used for crawling are listed in:

```text
sources.txt
```

#### 2. Run the web crawler

```powershell
python web_crawler.py
```

The crawler collects the source documentation and stores the raw documents and associated metadata.

#### 3. Process the collected documents

```powershell
python data_processing.py
```

The processing pipeline cleans and normalizes the collected documents and generates the document chunks and corpus files used by the retrieval models.

> Note: Regenerating the dataset may produce different results if the source websites have changed since the original dataset was collected. The checked-in dataset should therefore be used when reproducing the results reported in the project report.

---

## Requirements

The project requires:

- Python **3.12**
- pip
- The dependencies listed in `requirements.txt`

All Python package versions are pinned in `requirements.txt` to reduce differences between environments.

---

## Installation

Clone the repository:

```powershell
git clone https://github.com/<your-username>/Full-Stack-RAG.git
cd Full-Stack-RAG
```

Create a Python virtual environment:

```powershell
py -3.12 -m venv rag-env
```

Activate the environment:

```powershell
rag-env\Scripts\activate
```

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

---

## Reproduce All Experimental Results

The complete experiment can be reproduced from the project root using a **single command**:

```powershell
python main.py
```

The command automatically performs the complete retrieval and evaluation pipeline.

### Pipeline Steps

`main.py` performs the following operations:

1. Loads the processed document chunks.
2. Trains the BM25 retrieval model.
3. Trains the Word2Vec model.
4. Generates document vectors for dense retrieval.
5. Loads the query set from:

```text
Data/queries/queries.jsonl
```

6. Runs every query through:
    - BM25 retrieval
    - Word2Vec retrieval
    - Hybrid retrieval

7. Generates ranked retrieval results.
8. Evaluates the retrieved documents against the expected answers.
9. Saves the evaluation results.

No interactive input is required.

---

## Generated Results

After running:

```powershell
python main.py
```

the following artifacts are generated or refreshed.

### Retrieval Models

```text
Models/index/bm25.pkl
Models/index/word2vec.model
Models/index/doc_vectors.pkl
```

These files contain the trained retrieval indexes and document vectors.

### Per-Query Results

Results for individual queries are stored under:

```text
Data/queries/<query_id>/
```

These files contain the rankings and retrieved chunks associated with each query.

### Evaluation Results

The overall evaluation output is stored in:

```text
Evaluation/evaluation_results.txt
```

This file contains the query-by-query evaluation results for the retrieval models.

The answerability status of the queries is stored in:

```text
Evaluation/question_status.txt
```

---

## Retrieval Models

### BM25

BM25 is used as the primary lexical retrieval model. It ranks documents according to the relevance of query terms while considering term frequency and document length.

### Word2Vec

Word2Vec is used to capture semantic relationships between words. Document vectors are generated from the trained word embeddings and compared with query representations to perform semantic retrieval.

### Hybrid Retrieval

The hybrid retrieval model combines the results of BM25 and Word2Vec retrieval to leverage both:

- **Lexical matching** from BM25
- **Semantic similarity** from Word2Vec

This allows the system to retrieve documents that may be relevant even when the query and document do not contain exactly the same terms.

---

## Evaluation Dataset

The query dataset is located at:

```text
Data/queries/queries.jsonl
```

Each query is associated with its expected answer document or URL, allowing the retrieval models to be evaluated against a known ground truth.

The evaluation includes both answerable and unanswerable queries.

The generated evaluation files allow the results reported in the project report to be independently inspected.

---

## Reproducibility

The project is designed to make the reported experiments reproducible.

### Fixed Random Seed

Word2Vec training uses a fixed random seed:

```text
42
```

This seed is configured in:

```text
Models/vector_model.py
```

### Pinned Dependencies

All required Python packages and their versions are specified in:

```text
requirements.txt
```

This helps ensure that the same software dependencies are used when reproducing the experiments.

### Fixed Dataset

The dataset used for the reported experiments is included in the repository under:

```text
Data/
```

Therefore, reproducing the reported experiments does not require downloading or crawling external websites.

### Recommended Environment

For the most consistent results, use:

```text
Python 3.12
```

and install the exact dependencies specified in:

```text
requirements.txt
```

---

## Reproducibility Checklist

The repository satisfies the following reproducibility requirements:

| Requirement                             | Included |
| --------------------------------------- | -------- |
| Public GitHub repository                | Yes      |
| Complete Python implementation          | Yes      |
| Dataset                                 | Yes      |
| Dataset construction scripts            | Yes      |
| Pinned dependencies                     | Yes      |
| Setup instructions                      | Yes      |
| Execution instructions                  | Yes      |
| Single command to reproduce experiments | Yes      |
| Fixed random seed                       | Yes      |
| Query/evaluation dataset                | Yes      |
| Saved evaluation artifacts              | Yes      |

---

## Quick Start

For users who only want to reproduce the reported results:

```powershell
git clone https://github.com/<your-username>/Full-Stack-RAG.git
cd Full-Stack-RAG
py -3.12 -m venv rag-env
rag-env\Scripts\activate
pip install -r requirements.txt
python main.py
```

The final evaluation results will be available in:

```text
Evaluation/evaluation_results.txt
```

and:

```text
Evaluation/question_status.txt
```

---

## Notes

- The crawler uses `sources.txt` as its seed URL list.
- The checked-in dataset should be used to reproduce the results reported in the project report.
- Re-crawling the websites may produce a different dataset because documentation pages can change over time.
- The main experimental pipeline does not require interactive input.
- If the dataset is regenerated, run `python main.py` afterward to rebuild the retrieval indexes and evaluation results.
- The repository should be cloned and executed using the same Python version and dependency versions specified above for the most consistent results.

---

## License

This project was developed for academic purposes as part of the CP423 project.
