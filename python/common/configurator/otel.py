from os import environ, getcwd
from os.path import abspath, dirname, pathsep


def config_otel():
    # Set Python path
    python_path = environ.get("PYTHONPATH")

    python_path = python_path.split(pathsep) if python_path else []

    cwd_path = getcwd()

    if cwd_path not in python_path:
        python_path.insert(0, cwd_path)

    filedir_path = dirname(abspath(__file__))
    python_path = [path for path in python_path if path != filedir_path]
    python_path.insert(0, filedir_path)
    environ["PYTHONPATH"] = pathsep.join(python_path)

    # Import to auto initialize
    import opentelemetry.instrumentation.auto_instrumentation.sitecustomize
