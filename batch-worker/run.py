from src import scheduled_worker

if __name__ == "__main__":
    worker = scheduled_worker.Worker()
    worker.start()
