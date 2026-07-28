# Requires the shared base image. Build via ./build.sh first.
FROM gms-base

COPY ./plans-classes-service/ /app/plans-classes-service
RUN pip install --no-deps -e /app/plans-classes-service

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

EXPOSE 5006
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/plans-classes-service/gunicorn.conf.py", "plans-classes-service.src:create_app()"]
