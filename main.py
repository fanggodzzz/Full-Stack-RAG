import web_crawler as crawler
import data_processing as processor
import threading

def prepare_data():
    crawler_thread = threading.Thread(target=crawler.main)
    processor_thread = threading.Thread(target=processor.main)
    crawler_thread.start()
    processor_thread.start()

    crawler_thread.join()
    processor_thread.join()
    
def main():
    prepare_data()
    
if __name__ == "__main__":
    main()