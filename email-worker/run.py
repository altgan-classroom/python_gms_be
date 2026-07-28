from src import worker_service

if __name__ == "__main__":
    worker = worker_service.Worker()
    worker.start()
