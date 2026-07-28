# Requires the shared base image. Build via ./build.sh first.
FROM gms-base

COPY ./members-service/ /app/members-service
RUN pip install --no-deps -e /app/members-service

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

EXPOSE 5005
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/members-service/gunicorn.conf.py", "members-service.src:create_app()"]
