import json
import os
from os import path
from shared import QUERY_RESULTS, import_chunks, import_meta_raw
from rag import querying
from query_retrieval import load_queries
from Models import bm25_model as bm
from Models import vector_model as vec
from Models import hybrid as hybrid
from query_retrieval import paragraph_pretier

QUERY_FOLDER = "./Data/queries/"
ANSWER_FILE = "answers.jsonl"
EVALUATION_FOLDER = "./Evaluation/"
chunks = import_chunks()
meta_raw = import_meta_raw()
answers = []
correct_docs = [-1]  # Initialize with -1 to indicate no correct document found
additional_docs = [-1]  # Initialize with -1 to indicate no additional correct document found
raw_queries = [] # Load queries from the queries.jsonl file
queries = []  # List to store queries loaded from the queries.jsonl file

def check(result, docno, additional_docno):
    # print(result)
    rank = 1
    ranks = []
    ranks_1 = []
    # print(docno, additional_docno)
    for chunk in result:
        chunk = int(chunk)  # Convert chunk to integer for indexing
        doc_meta = int(chunks[chunk]['docno'])
        # print(doc_meta, docno, additional_docno, f"{doc_meta} == {docno}: {doc_meta == docno}, {doc_meta} == {additional_docno}: {doc_meta == additional_docno}")
        if doc_meta == docno:
            ranks.append(rank)
        if doc_meta == additional_docno:
            ranks_1.append(rank)
        rank += 1

    return ranks, ranks_1

def get_docnos(result):
    docnos = []
    for chunk in result:
        chunk = int(chunk)  # Convert chunk to integer for indexing
        doc_meta = int(chunks[chunk]['docno'])
        if doc_meta not in docnos:
            docnos.append(doc_meta)
    return docnos

def load_answers():
    global answers
    if os.path.exists(os.path.join(QUERY_FOLDER, ANSWER_FILE)):
            with open(os.path.join(QUERY_FOLDER, ANSWER_FILE), "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        answers.append(json.loads(line))
    return answers

def load_raw_queries_and_queries():
    global raw_queries, queries
    raw_queries.clear()
    queries.clear()
    if os.path.exists(os.path.join(QUERY_FOLDER, "queries.jsonl")):
        with open(os.path.join(QUERY_FOLDER, "queries.jsonl"), "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    temp = json.loads(line)
                    raw_queries.append({
                        "query_id": temp["query_id"],
                        "tokens": temp["query"]
                    })
                except Exception as e:
                    print(f"Error parsing line: {line}. Error: {e}")
                continue
    queries = load_queries()  # Load queries from the queries.jsonl file
    return raw_queries, queries

def retrieval_evaluate():
    global answers, correct_docs, queries, additional_docs
    raw_queries, queries = load_raw_queries_and_queries()
    answer = load_answers()

    print("Starting retrieval evaluation...")

    for answer in answers:
        url = answer.get("answer_url")
        correct_docs.append(-1)  # Default to -1 if no correct document is found
        additional_docs.append(-1)  # Default to -1 if no additional correct document is found
        additional_url = answer.get("additional_url")
        for docno, meta in meta_raw.items():
            if meta.get("url") == url:
                correct_docs[-1] = int(docno)  # Update the last element with the correct docno
            elif additional_url and meta.get("url") == additional_url:
                additional_docs[-1] = int(docno)  # Update the last element with the additional correct docno

    # print(correct_docs)
    # print(additional_docs)

    with open(os.path.join(EVALUATION_FOLDER, "question_status.txt"), "w", encoding="utf-8") as status_file:
        for i in range(1, len(answers) + 1):
            if correct_docs[i] == -1:
                status_file.write(f"{i}: Unanswerable - No corresponding document found for the provided answer URL.\n")
            else:
                status_file.write(f"{i}: Answerable - Corresponding document found: docno {correct_docs[i]}\n")

    with open(os.path.join(EVALUATION_FOLDER, "retrieval_evaluation_results.txt"), "w", encoding="utf-8") as eval_file:
        for answer in answers:
            answer_id = answer.get("query_id")

            folder = os.path.join(QUERY_RESULTS, answer_id) + "/"
            answer_id = int(answer_id)  # Convert answer_id to integer for indexing

            # if answer_id != 12:
            #     continue

            if correct_docs[answer_id] == -1:
                eval_file.write(f"Query {answer_id} - {folder} - No corresponding document found for the provided answer URL.\n")
                eval_file.write("\n" + "-"*50 + "\n\n")
                continue  # Skip to the next answer if no corresponding document is found

            eval_file.write(f"Query {answer_id}\n\n")
            eval_file.write(f"Question: {raw_queries[answer_id - 1].get('tokens')}\n")
            eval_file.write(f"Correct Document: {correct_docs[answer_id]} {additional_docs[answer_id] if additional_docs[answer_id] != -1 else ''}\n\n")

            bm25_file = os.path.join(folder, f"bm25_scores_{answer_id}.json")
            w2v_file = os.path.join(folder, f"w2v_scores_{answer_id}.json")
            hybrid_file = os.path.join(folder, f"hybrid_scores_{answer_id}.json")

            bm25_result = json.load(open(bm25_file, "r", encoding="utf-8")) 
            w2v_result = json.load(open(w2v_file, "r", encoding="utf-8")) 
            hybrid_result = json.load(open(hybrid_file, "r", encoding="utf-8"))

            temp, temp_1 = check(bm25_result, correct_docs[answer_id], additional_docs[answer_id])
            if (temp or temp_1):
                eval_file.write(f"BM25: Correct document found for query {answer_id} at rank {temp} {temp_1}\n")
            else:
                eval_file.write(f"BM25: Correct document NOT found for query {answer_id}\n")

            temp, temp_1 = check(w2v_result, correct_docs[answer_id], additional_docs[answer_id])
            if (temp or temp_1):
                eval_file.write(f"W2V: Correct document found for query {answer_id} at rank {temp} {temp_1}\n")
            else:
                eval_file.write(f"W2V: Correct document NOT found for query {answer_id}\n")


            temp, temp_1 = check(hybrid_result, correct_docs[answer_id], additional_docs[answer_id])
            if (temp or temp_1):
                eval_file.write(f"Hybrid: Correct document found for query {answer_id} at rank {temp} {temp_1}\n")
            else:
                eval_file.write(f"Hybrid: Correct document NOT found for query {answer_id}\n")

            eval_file.write("\n")

            bm25_docnos = get_docnos(bm25_result)
            w2v_docnos = get_docnos(w2v_result)
            hybrid_docnos = get_docnos(hybrid_result)

            eval_file.write(f"BM25 Docs:\n")
            for docno in bm25_docnos:
                eval_file.write(f"Docno: {docno}, URL: {meta_raw[docno]['url']}\n")

            eval_file.write("\n")

            eval_file.write(f"W2V Docs:\n")
            for docno in w2v_docnos:
                eval_file.write(f"Docno: {docno}, URL: {meta_raw[docno]['url']}\n")

            eval_file.write("\n")

            eval_file.write(f"Hybrid Docs:\n")
            for docno in hybrid_docnos:
                eval_file.write(f"Docno: {docno}, URL: {meta_raw[docno]['url']}\n")

            eval_file.write("\n" + "-"*50 + "\n\n")

    print(f"Evaluation completed. Results are saved in {EVALUATION_FOLDER}/retrieval_evaluation_results.txt.")

def rag_evaluate():
    global answers, correct_docs, queries, additional_docs
    raw_queries, queries = load_raw_queries_and_queries()
    answers = load_answers()

    print("Starting RAG evaluation...")

    with open(os.path.join(EVALUATION_FOLDER, "rag_evaluation_results.txt"), "w", encoding="utf-8") as eval_file:

        for i in range(len(answers)):
            answer = answers[i]
            answer_id = answer.get("query_id")
            answer_id = int(answer_id)  # Convert answer_id to integer for indexing

            eval_file.write(f"Query {answer_id}\n\n")
            eval_file.write(f"Question: {raw_queries[answer_id - 1].get('tokens')}\n")
            eval_file.write(f"Reference Answer: {answer.get('reference_answer')}\n")

            response = querying(raw_queries[answer_id - 1].get('tokens'))
            # print(response['bm25']['response'], response['w2v']['response'], response['hybrid']['response']['content'])

            # BM25 Response
            eval_file.write(f"BM25 Response: \n {paragraph_pretier(response['bm25']['response']['message']['content'])}\n\n")

            # W2V Response
            eval_file.write(f"W2V Response: \n {paragraph_pretier(response['w2v']['response']['message']['content'])}\n\n")

            # Hybrid Response
            eval_file.write(f"Hybrid Response: \n {paragraph_pretier(response['hybrid']['response']['message']['content'])}\n\n")

            eval_file.write("\n" + "-"*50 + "\n\n")

            if (i == 1):
                break

    print(f"Evaluation completed. Results are saved in {EVALUATION_FOLDER}rag_evaluation_results.txt.")

    
if __name__ == "__main__":
    retrieval_evaluate()
    rag_evaluate()