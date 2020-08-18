# AppUnit

Python Application Framework.

![tests](https://github.com/antonrh/appunit/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/antonrh/appunit/branch/master/graph/badge.svg)](https://codecov.io/gh/antonrh/appunit)
[![Documentation Status](https://readthedocs.org/projects/appunit/badge/?version=latest)](https://appunit.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/appunit.svg)](https://pypi.org/project/appunit/)
[![license](https://img.shields.io/pypi/l/appunit)](https://github.com/antonrh/appunit/blob/master/LICENSE)

---

Documentation: https://appunit.readthedocs.io/

---

## Installing

Install using `pip`:

```bash
pip install appunit[full]
```

## Quick Example

*app.py*

```python
import appunit

app = appunit.AppUnit()


@app.get("/")
def index():
    return "Hello, AppUnit !"


if __name__ == "__main__":
    app.run()
```