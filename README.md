# household-model

Estimates a household's emissions and cost savings from electrification.


## Installation

```bash
pipenv install --dev
```

## Run

```bash
cd src

# for development
pipenv run fastapi dev main.py

# for production
pipenv run fastapi run
```

You can check out the auto-generated API docs at http://127.0.0.1:8000/docs.


## Contributing

```bash
# Run tests
pipenv run python -m pytest

# Lint (skip string normalisation)
pipenv run black -S . --exclude src/openapi_client
```

## Generating the API client from `openapi.yml`

First, [install the OpenAPI generator](https://openapi-generator.tech/docs/installation/).

```bash
# Linux/MacOS
brew install openapi-generator
```

### For python (e.g. use within this model)

Since FastAPI expected pydantic models, we need to use an OpenAPI python generator that specifically produces pydantic models. We're using [python-pydantic-v1](https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/python-pydantic-v1.md).

```bash
# navigate to the root dir of this repo (make sure you're not in src/)

# generate client
openapi-generator generate -i openapi.yml -g python-pydantic-v1 --additional-properties=generateSourceCodeOnly=true

# move into src/ folder, overwriting any existing version
mkdir -p src/openapi_client && cp -r ./openapi_client/* ./src/openapi_client && rm -R ./openapi_client/
```

Unfortunately, there's no Pydantic v2-compatible openapi generator, so we're using the latest Pydantic v1 version, pinned in our Pipfile.

### For TypeScript

To use the client in TypeScript (e.g. for a frontend like the [household-calculator-app](https://github.com/rewiring-nz/household-calculator-app)), generate a TypeScript api using something like the [typescript-axios generator](https://openapi-generator.tech/docs/generators/typescript-axios).

```bash
# Replace the value after -o (for "output") with the location where you want the client to go.
# E.g. the src/shared/api/ folder of your frontend project
openapi-generator-cli generate -i openapi.yml -g typescript-axios -o ~/code/household-calculator-app/src/shared/api/
```