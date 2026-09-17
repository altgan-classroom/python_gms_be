from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = "GMS members service"
APP_ROOT = Path(__file__).parent
INSTALL_REQUIRES = ["pyotp==2.9.0", "gmsshared", "pandas"]

setup(
    name="members-service",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    version="1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=INSTALL_REQUIRES,
)
