# Shared base image for ALL GMS services.
# Installs Python 3.11 + every gmsshared dependency ONCE (the heavy/slow part:
# cryptography, pandas, lxml, reportlab, xhtml2pdf, ...). Each service image is
# then `FROM gms-base` and only installs its own thin package — so service builds
# are near-instant and the expensive dependency layer is shared on disk.
#
# Build this FIRST, before `docker compose build`:
#   ./build.sh            (or)   docker build -t gms-base -f gms-base.Dockerfile .
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="."

# build-essential is only needed to compile the few sdist-only wheels
# (xhtml2pdf / svglib / reportlab). mysql-connector-python is pure Python, so
# the old default-libmysqlclient-dev + pkg-config packages were unnecessary.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./gmsshared/ /app/gmsshared
RUN pip install -e /app/gmsshared
