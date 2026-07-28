from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = "Gym Owners worker service"
APP_ROOT = Path(__file__).parent
AUTHOR = "Surendra Pepakayala"
AUTHOR_EMAIL = "surendra.pepakayala@gymlaunch.com"
PROJECT_URLS = {
    "Bug Tracker": "https://gymlaunch.atlassian.net/jira/software/c/projects/GMS/boards/4",
    "Source Code": "https://bitbucket.org/gls_itsystems/workspace/projects/gym_management_system",
}
INSTALL_REQUIRES = [
    "gmsshared",
]

setup(
    name="email-worker",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    version="0.1",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url="https://bitbucket.org/gls_itsystems/gms/src/main/worker-worker",
    project_urls=PROJECT_URLS,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=INSTALL_REQUIRES,
)
