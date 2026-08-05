from gensim.models import Word2Vec
import numpy as np
import pickle
import os
from shared import load_corpus

INDEX_DIR = os.path.join(os.path.dirname(__file__), "./index")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "../Temp/index/")
WORD2VEC_PATH = os.path.join(INDEX_DIR, "word2vec.model")
DOCVEC_PATH = os.path.join(INDEX_DIR, "doc_vectors.pkl")


def build_vector_model(chunks, vector_size=100):
    print("Training Word2Vec model...")

    sentences = load_corpus()

    if not sentences:
        raise ValueError("No tokenized text available to train the vector model.")

    model = Word2Vec(
        vector_size=vector_size,
        window=5,
        min_count=1,
        workers=4,
        sg=1,
    )
    model.build_vocab(sentences)
    model.train(sentences, total_examples=len(sentences), epochs=model.epochs)

    os.makedirs(INDEX_DIR, exist_ok=True)
    model.save(WORD2VEC_PATH)

    # build document vectors by averaging token vectors
    doc_vectors = []
    for tokens in sentences:
        vecs = [model.wv[t] for t in tokens if t in model.wv]
        if len(vecs) == 0:
            doc_vectors.append(np.zeros(vector_size, dtype=float))
        else:
            doc_vectors.append(np.mean(vecs, axis=0))

    with open(DOCVEC_PATH, "wb") as f:
        pickle.dump(doc_vectors, f)

    print(f"Word2Vec model saved to {WORD2VEC_PATH}")
    print(f"Document vectors saved to {DOCVEC_PATH}")

    return model, doc_vectors


def load_vector_model():
    # model = Word2Vec.load(os.path.join(TEMP_DIR, "word2vec.model"))
    # with open(f"{TEMP_DIR}/doc_vectors.pkl", "rb") as f:

    model = Word2Vec.load(WORD2VEC_PATH)
    with open(DOCVEC_PATH, "rb") as f:
        doc_vectors = pickle.load(f)
    return model, doc_vectors


def _cosine(a, b):
    if np.all(a == 0) or np.all(b == 0):
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def query_vector(model, doc_vectors, query_tokens, top_n=10):
    # compute query vector as mean of tokens present in model
    import numpy as _np

    token_vecs = [model.wv[t] for t in query_tokens if t in model.wv]
    if len(token_vecs) == 0:
        query_vec = _np.zeros(model.vector_size, dtype=float)
    else:
        query_vec = _np.mean(token_vecs, axis=0)

    scores = [_cosine(query_vec, dv) for dv in doc_vectors]
    # return full scores array and top indices
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    return scores, top_indices
