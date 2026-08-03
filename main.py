import web_crawler as crawler
import data_processing as processor
# import bm25_model as bm
# import vector_model as vec
import threading

def prepare_data():
    crawler_thread = threading.Thread(target=crawler.main)
    processor_thread = threading.Thread(target=processor.main)
    crawler_thread.start()
    processor_thread.start()

    crawler_thread.join()
    processor_thread.join()
    
# def train_data():
#     chunks = []
#     bm_thread = threading.Thread(target=bm.build_bm25)
#     vec_thread = threading.Thread(target=vec.train_word2vec)

#     bm_thread.start()
#     vec_thread.start()

#     bm_thread.join()
#     vec_thread.join()

def main():
    prepare_data()
    # train_data()

if __name__ == "__main__":
    main()