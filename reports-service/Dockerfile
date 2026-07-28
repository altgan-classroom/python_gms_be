# Requires the shared base image. Build via ./build.sh first.
# (Note: the old members-service bundle was dropped — reports no longer imports it.)
FROM gms-base

COPY ./reports-service/ /app/reports-service
RUN pip install --no-deps -e /app/reports-service

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

EXPOSE 5008
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/reports-service/gunicorn.conf.py", "reports-service.src:create_app()"]
