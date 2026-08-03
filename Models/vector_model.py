from gensim.models import Word2Vec

MODELS = "./Models"
MODEL_NAME = "word2vec.model"

def train_word2vec(chunks):

    sentences = [
        chunk["tokens"]
        for chunk in chunks
    ]

    model = Word2Vec(
        sentences=sentences,
        vector_size=100,
        window=5,
        min_count=2,
        workers=4,
        sg=1
    )

    model.save("models/word2vec.model")

    return model