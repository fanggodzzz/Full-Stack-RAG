from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
import os
from shared import load_corpus

INDEX_DIR = os.path.join(os.path.dirname(__file__), "./index")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "../Temp/index/")
WORD2VEC_PATH = os.path.join(INDEX_DIR, "word2vec.model")
DOCVEC_PATH = os.path.join(INDEX_DIR, "doc_vectors.pkl")

text_hashes = set()  # Set to store hashes of processed texts
# meta_raw = {}  # Dictionary to store metadata for each document

def tfidf_vectorize(corpus):
    texts = [" ".join(tokens) for tokens in corpus]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    return vectorizer, tfidf_matrix

def combine_vectors_with_tfidf(doc_vectors, tokens, token_id, vectorizer, tfidf_matrix):
    total_weight = 0.0
    for i in range(len(tokens)):
        if tokens[i] not in vectorizer.vocabulary_:
            continue

        token_index = vectorizer.vocabulary_[tokens[i]]

        tfidf_weight = float(tfidf_matrix[token_id, token_index])
        doc_vectors[i] *= tfidf_weight

        total_weight += tfidf_weight

    combined_vector = np.sum(doc_vectors, axis=0)

    if total_weight > 0:
        combined_vector /= total_weight

    return combined_vector

def build_vector_model(vector_size=300):
    print("Training Word2Vec model...")

    sentences = load_corpus()

    model = Word2Vec(
        vector_size=vector_size,
        window=10,
        min_count=1,
        workers=10,
        sg=1,
        negative=10,
        epochs=20,
        seed=42,
    )

    model.build_vocab(sentences)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.epochs)

    os.makedirs(INDEX_DIR, exist_ok=True)
    model.save(WORD2VEC_PATH)

    print(f"Word2Vec model saved to {WORD2VEC_PATH}")

    # model, _ = load_vector_model()  # Load the model to ensure it's saved and can be loaded correctly
    # print(f"Loaded Word2Vec model from {WORD2VEC_PATH}")

    vectorizer, tfidf_matrix = tfidf_vectorize(sentences)  # Initialize TF-IDF vectorizer and matrix    
    print("Built document vectors using TF-IDF weighted averaging")

    # build document vectors by averaging token vectors
    doc_vectors = []

    for i in range(len(sentences)):
        print(f"Processing document {i + 1}/{len(sentences)}", end="\r")
        tokens = sentences[i]
        vecs = [model.wv[t].copy() if t in model.wv else np.zeros(vector_size, dtype=float)for t in tokens]        
        if len(vecs) == 0:
            doc_vectors.append(np.zeros(vector_size, dtype=float))
        else:
            doc_vectors.append(combine_vectors_with_tfidf(vecs, tokens, i, vectorizer, tfidf_matrix))

    with open(DOCVEC_PATH, "wb") as f:
        pickle.dump(doc_vectors, f)

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


def query_vector(model, doc_vectors, query_tokens, vectorizer, tfidf_matrix, top_n=10):
    # compute query vector as mean of tokens present in model
    import numpy as _np

    # Use tfidf from both corpus and query to compute the query vector
    tfidf_matrix = vectorizer.transform([" ".join(query_tokens)])  
    
    token_vecs = [model.wv[t].copy() if t in model.wv else np.zeros(model.vector_size, dtype=float) for t in query_tokens]
    if len(token_vecs) == 0:
        query_vec = _np.zeros(model.vector_size, dtype=float)
    else:
        query_vec = combine_vectors_with_tfidf(token_vecs, query_tokens, 0, vectorizer, tfidf_matrix)

    scores = [_cosine(query_vec, dv) for dv in doc_vectors]
    # return full scores array and top indices
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    return scores, top_indices
