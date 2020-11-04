import sys, os
from mobi7.funcs import consolidate_results
from mobi7 import create_app

app = create_app()

if __name__ == "__main__":
    if '--consolidate' in sys.argv:
        consolidate_results('./data')
    else:
        app.run(
            host=os.environ.get("BACKEND_HOST", "127.0.0.1"),
            port=5000,
            debug=True,
        )