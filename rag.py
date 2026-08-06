import json
from os import getenv
import time
from shared import import_chunks
import Models.bm25_model as bm
import Models.vector_model as vec
import Models.hybrid as hybrid
from ollama import chat
from query_retrieval import normalize_text_tokens, load_models

TOP_N = 20  # Default to top 20 results if not set in .env
BM25_WEIGHT = 0.25  # Default weight for BM25 in hybrid retrieval
SYSTEM_PROMPT = """
You are a closed-book question answering system.

You MUST answer using ONLY the information contained
in the CONTEXT provided by the application.

Rules:
1. Do not use outside knowledge.
2. Do not rely on your pretrained knowledge.
3. Do not infer facts that are not supported by the context.
4. If the context does not contain enough information,
   respond exactly:
   I don't know.
5. Every factual claim must be supported by a citation
   to one of the provided chunks.
"""

bm25_model = None
w2v_model = None
w2v_doc_vectors = None
chunks = []


def init():
    global chunks, bm25_model, w2v_model, w2v_doc_vectors

    chunks = import_chunks()
    bm25_model = bm.load_bm25_model()
    w2v_model, w2v_doc_vectors = vec.load_vector_model()

    return

def query_llm(query, context):
    start = time.time()
    response = chat(
        model="llama3.2:latest",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
                QUESTION:
                {query}

                CONTEXT:
                {context}

                """
            }
        ],
        options={
            "num_predict": 300
        }
    )
    elapsed = time.time() - start
    try:
        # best-effort size info
        resp_text = response.get("message", {}).get("content") or str(response)
        resp_len = len(resp_text)
    except Exception:
        resp_len = 0
    print(f"LLM call took {elapsed:.2f}s, response length {resp_len} chars")
    return response

def query_models(tokens):
    global bm25_model, w2v_model, w2v_doc_vectors, vectorizer, tfidf_matrix
    bm25_model, w2v_model, w2v_doc_vectors, vectorizer, tfidf_matrix = load_models()

    bm_scores = bm_top_indices = []
    w2v_scores = w2v_top_indices = []

    print("Querying BM25 model...")
    bm_scores, bm_top_indices = bm.query_bm25(bm25_model, tokens, top_n=20)

    print("Querying Word2Vec model...")
    w2v_scores, w2v_top_indices = vec.query_vector(w2v_model, w2v_doc_vectors, tokens, top_n=20, vectorizer=vectorizer, tfidf_matrix=tfidf_matrix)

    print("Combining BM25 and Word2Vec scores for hybrid retrieval...")
    _, hybrid_top_indices = hybrid.combine_scores(bm_scores, w2v_scores, bm25_weight=BM25_WEIGHT, top_n=20)

    return bm_top_indices, w2v_top_indices, hybrid_top_indices

def get_chunks(top_indices):
    # build a context string from top indices but limit size per chunk
    context_parts = []
    max_chars_per_chunk = 1000
    # send fewer chunks to reduce token count and latency
    num = min(3, len(top_indices))
    for i in range(num):
        idx = top_indices[i]
        title = chunks[idx].get("title", "")
        text = chunks[idx].get("chunk_text", "")
        # print(idx)
        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk] + "..."
        context_parts.append(f"{title}\n{text}")

    # join with a clear separator to help models and keep token count lower
    context = "\n\n---\n\n".join(context_parts)
    return context

def querying(user_query):
    global bm25_model, w2v_model, w2v_doc_vectors, vectorizer, tfidf_matrix, chunks
    tokens = normalize_text_tokens(user_query)
    bm25, w2v, hybrid = query_models(tokens)
    bm25_context = w2v_context = hybrid_context = ""
    chunks = import_chunks()  

    print("Retrieving context for BM25, Word2Vec, and Hybrid models...")
    bm25_context = get_chunks(bm25)
    w2v_context = get_chunks(w2v)
    hybrid_context = get_chunks(hybrid)

    bm25_response = w2v_response = hybrid_response = None

    print("Querying LLM with BM25, Word2Vec, and Hybrid contexts...")
    bm25_response = query_llm(user_query, bm25_context)
    w2v_response = query_llm(user_query, w2v_context)
    hybrid_response = query_llm(user_query, hybrid_context)

    return {
        "bm25": {
            "context": bm25_context,
            "response": bm25_response
        },
        "w2v": {
            "context": w2v_context,
            "response": w2v_response
        },
        "hybrid": {
            "context": hybrid_context,
            "response": hybrid_response
        }
    }

def main():
    querying()

if __name__ == "__main__":
    main()