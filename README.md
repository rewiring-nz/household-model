# household-model

Estimates a household's emissions and cost savings from electrification


## Installation

```bash
pipenv install --dev
```

## Run

Run the live server with the following command:

```bash
cd src
pipenv run fastapi dev main.py
```

You can check out the auto-generated API docs at http://127.0.0.1:8000/docs.


## Contributing

```bash
# Run tests
pipenv run python -m pytest

# Lint (skip string normalisation)
pipenv run black -S .
```

## Refreshing `src/client` from `openapi.yml`

Since FastAPI expected pydantic models, we need to use an OpenAPI python generator that specifically produces pydantic models. We're using [python-pydantic-v1](https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/python-pydantic-v1.md).

```bash
brew install openapi-generator

# navigate to the root dir of this repo (make sure you're not in src/)

openapi-generator generate -i openapi.yml -g python-pydantic-v1 --additional-properties=generateSourceCodeOnly=true
mv openapi_client src/
```

