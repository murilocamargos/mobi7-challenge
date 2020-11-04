import pytest
from mobi7 import create_app


@pytest.fixture
def app():
    app = create_app()
    return app
