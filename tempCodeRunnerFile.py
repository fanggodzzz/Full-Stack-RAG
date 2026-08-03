True:
        doc_num = document_queue.get()  # Wait for a document number from the queue
        if doc_num is None:  # Check for the sentinel value to exit
            break
        process_raw_data(doc_num)
        document_queue