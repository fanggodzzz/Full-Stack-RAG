from rank_bm25 import BM25Okapi
from shared import import_chunks, load_corpus
import pickle
import os

INDEX_DIR = os.path.join(os.path.dirname(__file__), "./index")
MODEL_NAME = "bm25.pkl"
TEMP_DIR = os.path.join(os.path.dirname(__file__), "../Temp/index/")

def build_bm25_model():
    print("Training BM25 model...")

    corpus = load_corpus()
    # print(corpus[0])

    bm25 = BM25Okapi(corpus)

    path = os.path.join(INDEX_DIR, MODEL_NAME)
    os.makedirs(INDEX_DIR, exist_ok=True)
    with open(f"{INDEX_DIR}/{MODEL_NAME}", "wb") as f:
        pickle.dump(bm25, f)

    print(f"BM25 model saved to {path}")

def load_bm25_model():
    # with open(f"{TEMP_DIR}/{MODEL_NAME}", "rb") as f:
    
    with open(f"{INDEX_DIR}/{MODEL_NAME}", "rb") as f:
        bm25 = pickle.load(f)
    return bm25


def query_bm25(bm25, query_tokens, top_n=10):
    # return full scores list and top indices
    scores = bm25.get_scores(query_tokens)
    # scores is numpy array-like 
    try:
        scores_list = list(scores)
    except Exception:
        import numpy as _np
        scores_list = _np.array(scores).tolist()

    top_indices = sorted(range(len(scores_list)), key=lambda i: scores_list[i], reverse=True)[:top_n]
    return scores_list, top_indices
