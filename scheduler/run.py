from src.scheduler import scheduler_service

if __name__ == "__main__":
    worker = scheduler_service.Beat()
    worker.run()
