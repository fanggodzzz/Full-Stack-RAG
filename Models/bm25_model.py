from rank_bm25 import BM25Okapi
import pickle

MODELS = "./Models"

def build_bm25(chunks):

    corpus = [
        chunk["tokens"]
        for chunk in chunks
    ]

    bm25 = BM25Okapi(corpus)

    with open("data/index/bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)