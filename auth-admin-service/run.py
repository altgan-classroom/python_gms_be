"""Flask CLI/Application entry point."""

from src import create_app
from gmsshared import db

app = create_app()


@app.shell_context_processor
def shell():
    return {
        "db": db,
    }
