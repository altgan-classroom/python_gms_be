# Requires the shared base image. Build via ./build.sh (or `docker build -t gms-base -f gms-base.Dockerfile .`) first.
FROM gms-base

COPY ./auth-admin-service/ /app/auth-admin-service
RUN pip install --no-deps -e /app/auth-admin-service

ENV FLASK_DEBUG="false" \
    FLASK_SKIP_DOTENV="true"

EXPOSE 5004
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/auth-admin-service/gunicorn.conf.py", "auth-admin-service.src:create_app()"]
