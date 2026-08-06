# Full-Stack-RAG

A Python-based Retrieval-Augmented Generation (RAG) system for retrieving relevant information from software development documentation. The project implements a complete pipeline from web crawling and document preprocessing to BM25, Word2Vec, hybrid retrieval, and evaluation.

## GitHub Repository

**Public GitHub Repository:**
https://github.com/<your-username>/Full-Stack-RAG

Replace `<your-username>` with your GitHub username before submission.

The repository contains the complete implementation, dataset, retrieval models, evaluation data, web interface, configuration, and instructions required to reproduce the experiments reported in the project report.

---

# Project Overview

Full-Stack-RAG is a retrieval and evaluation pipeline designed for software development documentation.

The system performs the following stages:

1. Crawls documentation websites.
2. Extracts and cleans relevant document content.
3. Removes unwanted HTML elements and duplicate documents.
4. Splits documents into smaller chunks.
5. Builds retrieval models using:

   * **BM25**
   * **Word2Vec**
   * **Hybrid BM25 + Word2Vec retrieval**
6. Processes a predefined set of queries.
7. Retrieves and ranks relevant documents/chunks.
8. Generates responses using the retrieved context.
9. Evaluates retrieval performance against expected answer documents.
10. Provides a functional web interface for submitting queries and viewing generated responses.

The complete experimental pipeline can be executed using a single command.

---

# Repository Structure

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
│       ├── bm25.pkl            # BM25 index
│       ├── word2vec.model      # Word2Vec model
│       └── doc_vectors.pkl     # Document vectors
│
├── Evaluation/
│   ├── evaluation_results.txt
│   └── question_status.txt
│
├── UI/
│   ├── index.html              # Web interface
│   ├── ...                     # UI assets
│
├── sources.txt                 # Seed URLs for the crawler
├── web_crawler.py              # Web crawling pipeline
├── data_processing.py          # Data preprocessing and chunking
├── system.py                   # Flask web application
├── main.py                     # Main reproducible experiment pipeline
├── rag.py                      # RAG/retrieval pipeline
├── requirements.txt            # Pinned Python dependencies
└── README.md
```

---

# Dataset

The repository includes the dataset required to reproduce the experiments.

The `Data/` directory contains the processed documentation corpus, document/chunk metadata, queries, and expected answer information.

Because the dataset is included in the repository, users do **not** need to crawl the web again to reproduce the reported experiments.

## Rebuilding the Dataset

If the dataset needs to be regenerated, the crawler and preprocessing pipeline can be executed in the following order.

### 1. Configure the seed URLs

The websites used for crawling are listed in:

```text
sources.txt
```

### 2. Run the web crawler

```powershell
python web_crawler.py
```

The crawler collects the source documentation and stores the raw documents and associated metadata.

### 3. Process the collected documents

```powershell
python data_processing.py
```

The processing pipeline cleans and normalizes the collected documents and generates the document chunks and corpus files used by the retrieval models.

> **Note:** Regenerating the dataset may produce different results if the source websites have changed since the original dataset was collected. The checked-in dataset should therefore be used when reproducing the results reported in the project report.

---

# Requirements

The project requires:

* Python **3.12**
* pip
* Ollama
* An Ollama model compatible with the RAG pipeline
* The dependencies listed in `requirements.txt`

All Python package versions are pinned in `requirements.txt` to reduce differences between environments.

---

# Installation

## 1. Clone the Repository

```powershell
git clone https://github.com/<your-username>/Full-Stack-RAG.git
cd Full-Stack-RAG
```

## 2. Create a Python Virtual Environment

```powershell
py -3.12 -m venv rag-env
```

Activate the environment:

```powershell
rag-env\Scripts\activate
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# Ollama Setup

The system uses Ollama to generate responses from the retrieved documentation context.

Install Ollama and make sure the Ollama service is running before starting the RAG application.

For example, if the project is configured to use `llama3.2`, make sure the model is available locally:

```powershell
ollama pull llama3.2
```

You can check installed models with:

```powershell
ollama list
```

You can check currently running models with:

```powershell
ollama ps
```

The Ollama model configuration is defined in the RAG implementation.

---

# Reproduce All Experimental Results

The complete experiment can be reproduced from the project root using a **single command**:

```powershell
python main.py
```

The command automatically performs the complete retrieval and evaluation pipeline.

## Pipeline Steps

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

   * BM25 retrieval
   * Word2Vec retrieval
   * Hybrid retrieval
7. Generates ranked retrieval results.
8. Evaluates the retrieved documents against the expected answers.
9. Saves the evaluation results.

No interactive input is required.

---

# Web User Interface

The project also includes a **functional web-based user interface** built with Flask.

The web application allows users to submit natural-language questions through the browser and receive answers generated by the RAG system.

The Flask application is implemented in:

```text
system.py
```

The interface is located in:

```text
UI/
```

## Starting the Web UI

Make sure the virtual environment is activated:

```powershell
rag-env\Scripts\activate
```

Make sure Ollama is running and the required model is available.

Then start the Flask application:

```powershell
python system.py
```

The application initializes the RAG system and starts the Flask development server.

You should see output similar to:

```text
 * Running on http://127.0.0.1:5000
```

Open the displayed address in a web browser:

```text
http://127.0.0.1:5000
```

The browser will display the RAG user interface.

---

# Web UI Query Flow

The web interface communicates with the Flask backend through the `/api/query` endpoint.

The general flow is:

```text
User
  │
  │ Enter question
  ▼
Web UI (UI/index.html)
  │
  │ POST /api/query
  ▼
Flask Application (system.py)
  │
  ▼
RAG Pipeline (rag.py)
  │
  ├── BM25 Retrieval
  ├── Word2Vec Retrieval
  └── Hybrid Retrieval
  │
  ▼
Retrieved Documentation Context
  │
  ▼
Ollama Language Model
  │
  ▼
Generated Response
  │
  ▼
Flask API
  │
  ▼
Web UI
```

## API Endpoint

The Flask application provides the following endpoint:

```text
POST /api/query
```

The request body should contain a JSON object with a `query` field:

```json
{
    "query": "How does Spring Boot auto-configuration work?"
}
```

The server returns a JSON response similar to:

```json
{
    "status": "received",
    "query": "How does Spring Boot auto-configuration work?",
    "reply": "Generated response from the RAG system..."
}
```

An empty query is rejected with HTTP status `400`.

---

# Retrieval Models

## BM25

BM25 is used as the primary lexical retrieval model. It ranks documents according to the relevance of query terms while considering term frequency and document length.

## Word2Vec

Word2Vec is used to capture semantic relationships between words. Document vectors are generated from the trained word embeddings and compared with query representations to perform semantic retrieval.

## Hybrid Retrieval

The hybrid retrieval model combines the results of BM25 and Word2Vec retrieval to leverage both:

* **Lexical matching** from BM25
* **Semantic similarity** from Word2Vec

This allows the system to retrieve documents that may be relevant even when the query and document do not contain exactly the same terms.

---

# Generated Results

After running:

```powershell
python main.py
```

the following artifacts are generated or refreshed.

## Retrieval Models

```text
Models/index/bm25.pkl
Models/index/word2vec.model
Models/index/doc_vectors.pkl
```

These files contain the trained retrieval indexes and document vectors.

## Per-Query Results

Results for individual queries are stored under:

```text
Data/queries/<query_id>/
```

These files contain the rankings and retrieved chunks associated with each query.

## Evaluation Results

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

# Evaluation Dataset

The query dataset is located at:

```text
Data/queries/queries.jsonl
```

Each query is associated with its expected answer document or URL, allowing the retrieval models to be evaluated against a known ground truth.

The evaluation includes both answerable and unanswerable queries.

The generated evaluation files allow the results reported in the project report to be independently inspected.

---

# Reproducibility

The project is designed to make the reported experiments reproducible.

## Fixed Random Seed

Word2Vec training uses a fixed random seed:

```text
42
```

This seed is configured in:

```text
Models/vector_model.py
```

Using a fixed seed reduces variation in Word2Vec training between runs.

## Pinned Dependencies

All required Python packages and their versions are specified in:

```text
requirements.txt
```

This helps ensure that the same software dependencies are used when reproducing the experiments.

## Fixed Dataset

The dataset used for the reported experiments is included in the repository under:

```text
Data/
```

Therefore, reproducing the reported experiments does not require downloading or crawling external websites.

## Pre-trained Retrieval Indexes

The generated retrieval indexes are stored under:

```text
Models/index/
```

These include:

```text
bm25.pkl
word2vec.model
doc_vectors.pkl
```

The indexes can be committed to the repository using Git LFS when necessary due to their file size.

This allows the repository to retain the model artifacts used during experimentation.

## Recommended Environment

For the most consistent results, use:

```text
Python 3.12
```

and install the exact dependencies specified in:

```text
requirements.txt
```

---

# Reproducibility Checklist

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
| Retrieval model indexes                 | Yes      |
| Saved evaluation artifacts              | Yes      |
| Functional web UI                       | Yes      |

---

# Quick Start

## Reproduce the Experiments

From the project root:

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

## Run the Web Application

After installing the dependencies and configuring Ollama:

```powershell
rag-env\Scripts\activate
python system.py
```

Then open:

```text
http://127.0.0.1:5000
```

in a web browser.

---

# Notes

* The crawler uses `sources.txt` as its seed URL list.
* The checked-in dataset should be used to reproduce the results reported in the project report.
* Re-crawling the websites may produce a different dataset because documentation pages can change over time.
* The main experimental pipeline does not require interactive input.
* The web interface requires the Flask application and Ollama to be running.
* The web interface sends user queries to the `/api/query` endpoint.
* If the dataset is regenerated, run `python main.py` afterward to rebuild the retrieval indexes and evaluation results.
* For the most consistent results, use Python 3.12 and the dependency versions specified in `requirements.txt`.
* The generated model indexes may be stored using Git LFS if they exceed the standard GitHub file size limit.

---

# License

This project was developed for academic purposes as part of the CP423 project.
