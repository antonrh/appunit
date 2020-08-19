AppUnit provides Dependency Injection mechanism which allows the creation of dependent objects 
outside of a class and provides those objects to a class through different way using 
[Injector](https://github.com/alecthomas/injector) framework.

### Bindings

You can set and get application dependencies using `bind` and `lookup` methods.

```python
from appunit import AppUnit

app = AppUnit()
app.bind(str, to="Hello DI!")

print(app.lookup(str))
```

Output:

```
Hello DI!
```

### Scopes

You can also provide different scopes to your dependencies.

#### No Scope

```python
from appunit import AppUnit

app = AppUnit()
app.bind(str, to="Hello DI!")

print(app.lookup(str))
```

#### Singleton

Defining binding with singleton scope means the container creates a single instance 
of that binding, and all requests for that binding interface will return the same object, 
which is cached.

```python
from appunit import AppUnit, SingletonScope


class Component:
    def __init__(self, name: str):
        self.name = name


app = AppUnit()
app.bind(Component, to=Component("db"), scope=SingletonScope)

print(app.lookup(Component))
```

#### Request

Defining binding with request scope means the container creates a single instance 
of that binding for every request which is cached.

```python
from appunit import AppUnit, Request, RequestScope, inject


class Path(str):
    pass


@inject
def get_path(request: Request) -> Path:
    return Path(request.url.path)


app = AppUnit()
app.bind(Path, to=get_path, scope=RequestScope)


@app.get("/")
def index(path: Path):
    return f"path is `{path}`"


if __name__ == "__main__":
    app.run()
```

`inject` decorator declaring parameters to be injected.