import os
import threading
import json
from shared import import_chunks
import Models.bm25_model as bm
import Models.vector_model as vec
import Models.hybrid as hybrid

QUERY_RESULTS = "./Data/queries/"
QUERIES = "queries.jsonl"
BM25_WEIGHT = 0.25

# Format [{"query_id": "id", "tokens": ["token1", "token2", ...]}, ...]
queries = []
bm25_model = None
w2v_model = None
w2v_doc_vectors = None
chunks = import_chunks()

def load_queries():
    global queries
    queries.clear()
    path = os.path.join(QUERY_RESULTS, QUERIES)
    if not os.path.exists(path):
        print(f"Queries file {path} does not exist.")
        return []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                temp = json.loads(line)
                queries.append({
                    "query_id": temp["query_id"],
                    "tokens": temp["query"].split()
                })
            except Exception as e:
                print(f"Error parsing line: {line}. Error: {e}")
                continue

def load_models():
    global bm25_model, w2v_model, w2v_doc_vectors

    bm25_model = bm.load_bm25_model()
    w2v_model, w2v_doc_vectors = vec.load_vector_model()

    return 

def paragraph_pretier(text, max_length=80):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        if len(' '.join(current_line + [word])) <= max_length:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

def save_query_scores(folder, file_name, scores, top_indices):
    temp = {}
    for idx in top_indices:
        temp[idx] = float(scores[idx])
    path = os.path.join(folder, file_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(temp, f, ensure_ascii=False, indent=4)

def save_query_chunks(folder, file_name, top_indices):
    path = os.path.join(folder, file_name)
    with open(path, "w", encoding="utf-8") as f:
        for idx in top_indices:
            chunk_text = chunks[idx].get("chunk_text", "")
            f.write(f'Index: {idx} <<"chunk_id": {chunks[idx].get("chunk_id")}, "docno": {chunks[idx].get("docno")}>>\n\n')
            f.write(f"{paragraph_pretier(chunk_text)}\n")
            f.write("-" * 100 + "\n")

def query_processing(query_id, tokens):
    print(f"Processing query {query_id}...")
    result_folder = os.path.join(QUERY_RESULTS, query_id)
    os.makedirs(result_folder, exist_ok=True)

    bm_scores = bm_top_indices = []
    w2v_scores = w2v_top_indices = []

    bm_scores, bm_top_indices = bm.query_bm25(bm25_model, tokens, top_n=20)
    save_query_scores(result_folder, f"bm25_scores_{query_id}.json", bm_scores, bm_top_indices)
    save_query_chunks(result_folder, f"bm25_top_chunks_{query_id}.txt", bm_top_indices)

    print(f"BM25 - Finished processing query {query_id}. Results saved in {result_folder}.")

    w2v_scores, w2v_top_indices = vec.query_vector(w2v_model, w2v_doc_vectors, tokens, top_n=20)
    save_query_scores(result_folder, f"w2v_scores_{query_id}.json", w2v_scores, w2v_top_indices)
    save_query_chunks(result_folder, f"w2v_top_chunks_{query_id}.txt", w2v_top_indices)

    print(f"Word2Vec - Finished processing query {query_id}. Results saved in {result_folder}.")

    hybrid_scores, hybrid_top_indices = hybrid.combine_scores(bm_scores, w2v_scores, bm25_weight=BM25_WEIGHT, top_n=20)
    save_query_scores(result_folder, f"hybrid_scores_{query_id}.json", hybrid_scores, hybrid_top_indices)
    save_query_chunks(result_folder, f"hybrid_top_chunks_{query_id}.txt", hybrid_top_indices)

    print(f"Hybrid - Finished processing query {query_id}. Results saved in {result_folder}.")

def querying():
    load_models()
    load_queries()
    
    for query in queries:
        query_processing(query["query_id"], query["tokens"])

def main():
    querying()

if __name__ == "__main__":
    main()