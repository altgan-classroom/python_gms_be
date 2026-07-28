# Requires the shared base image. Build via ./build.sh first.
FROM gms-base

COPY ./scheduler/ /app/scheduler
RUN pip install --no-deps -e /app/scheduler

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

CMD ["python", "scheduler/run.py"]
