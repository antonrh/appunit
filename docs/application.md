AppUnit includes an application class `AppUnit` which is base class of `ASGI` or `CLI` application. 

```python
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request

from appunit.applications import AppUnit

app = AppUnit(debug=True)


@app.on_startup()
def startup():
    print("Starting application ...")


@app.middleware()
async def simple_middleware(request: Request, call_next: RequestResponseEndpoint):
    print("Hello middleware!")
    return await call_next(request)


@app.get("/")
def index():
    return {"success": True}


if __name__ == "__main__":
    app.run()
```

### Instantiating the application

::: appunit.applications.AppUnit
    :docstring: