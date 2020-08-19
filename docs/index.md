# AppUnit Micro-Framework

![tests](https://github.com/antonrh/appunit/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/antonrh/appunit/branch/master/graph/badge.svg)](https://codecov.io/gh/antonrh/appunit)
[![Documentation Status](https://readthedocs.org/projects/appunit/badge/?version=latest)](https://appunit.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/appunit.svg)](https://pypi.org/project/appunit/)
[![license](https://img.shields.io/pypi/l/appunit)](https://github.com/antonrh/appunit/blob/master/LICENSE)

---

AppUnit is Python 3.6+ Micro-Framework, built on top of famous libraries:

* [Starlette](https://github.com/encode/starlette/) - Lightweight ASGI framework/toolkit
* [Click](https://github.com/pallets/click) - Command line interface toolkit
* [Injector](https://github.com/alecthomas/injector) - Dependency injection framework
* [Pydantic](https://github.com/samuelcolvin/pydantic/) - Data validation and settings management

---

## Installing

Install using `pip`:

```bash
pip install appunit
```

To run application with [Uvicorn](https://github.com/encode/uvicorn) server use:

```bash
pip install appunit[full]
```

## Quick Example

*app.py*

```python
from appunit.applications import AppUnit

app = AppUnit()


@app.get("/")
def index():
    return "Hello, AppUnit!"


if __name__ == "__main__":
    app.run()
```

Output:

```
INFO: Started server process [35049]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```
