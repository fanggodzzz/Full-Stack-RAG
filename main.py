from Models import bm25_model as bm
from Models import vector_model as vec
import threading
from shared import import_chunks
from query_retrieval import querying

chunks = []

def prepare_data():
    import web_crawler as crawler
    import data_processing as processor

    crawler_thread = threading.Thread(target=crawler.main)
    processor_thread = threading.Thread(target=processor.main)
    crawler_thread.start()
    processor_thread.start()

    crawler_thread.join()
    processor_thread.join()
    
def train_data():
    chunks = import_chunks()
    bm_thread = threading.Thread(target=bm.build_bm25_model, args=(chunks,))
    vec_thread = threading.Thread(target=vec.build_vector_model, args=(chunks,))

    bm_thread.start()
    vec_thread.start()

    bm_thread.join()
    vec_thread.join()

def get_query_response():
    querying()

def main():
    # prepare_data()
    # train_data()
    get_query_response()

if __name__ == "__main__":
    main()