# Requires the shared base image. Build via ./build.sh first.
FROM gms-base

COPY ./email-worker/ /app/email-worker
RUN pip install --no-deps -e /app/email-worker

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

CMD ["python", "email-worker/run.py"]
