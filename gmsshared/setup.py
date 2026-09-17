"""Installation script for authentication / authorization service."""
from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = "GMS shared library"
APP_ROOT = Path(__file__).parent
INSTALL_REQUIRES = [
    "boto3",
    "celery",
    "redis",
    # FastAPI stack (added during the Flask->FastAPI migration; coexists with Flask
    # while services are converted one at a time)
    "fastapi",
    "uvicorn[standard]",
    "python-multipart",
    # cryptography >=47 ships Rust wheels that SIGILL on some Apple-Silicon Docker
    # setups; 44.0.1 is the newest that runs cleanly and satisfies PyJWT + xhtml2pdf.
    "cryptography==44.0.1",
    "Flask",
    "Flask-Bcrypt",
    "Flask-Cors",
    "Flask-Migrate",
    "flask-openapi3[swagger,redoc,rapidoc,rapipdf,scalar,elements]",
    "Flask-Pydantic==0.12.0",
    "Flask-SQLAlchemy",
    "gunicorn",
    "Jinja2",
    "markupsafe",
    "mysql-connector-python",
    "Pydantic[email]==2.5.3",
    "PyJWT==2.9.0",
    "python-dateutil",
    "python-dotenv",
    "requests",
    "urllib3",
    "werkzeug",
    "pandas",
    "xhtml2pdf==0.2.11",  # pinned: newer pyHanko needs cryptography>=48 (which SIGILLs)
    "python-bidi==0.4.2",
    "pytz==2024.1",
]

setup(
    name="gmsshared",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    version="1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=INSTALL_REQUIRES
)
