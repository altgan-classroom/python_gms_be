# Requires the shared base image. Build via ./build.sh first.
FROM gms-base

COPY ./batch-worker/ /app/batch-worker
RUN pip install --no-deps -e /app/batch-worker

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

CMD ["python", "batch-worker/run.py"]
