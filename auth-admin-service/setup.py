"""Installation script for authentication / authorization service."""

from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = "GMS auth service"
APP_ROOT = Path(__file__).parent
INSTALL_REQUIRES = [
    "gmsshared",
]

setup(
    name="auth-admin-service",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    version="1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=INSTALL_REQUIRES,
)
