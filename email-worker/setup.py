from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = "Gym Owners worker service"
APP_ROOT = Path(__file__).parent
INSTALL_REQUIRES = [
    "gmsshared",
]

setup(
    name="email-worker",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=INSTALL_REQUIRES,
)
