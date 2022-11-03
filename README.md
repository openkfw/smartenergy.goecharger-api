# goechargerv2

![workflow](https://github.com/openkfw/goechargerv2/actions/workflows/python-ci.yml/badge.svg)
![workflow](https://github.com/openkfw/goechargerv2/actions/workflows/python-publish.yml/badge.svg)
![PyPI version](https://badge.fury.io/py/goechargerv2.svg)

A python API to access the Go eCharger wallbox. Official Go-eCharger [API documentation](https://github.com/goecharger/go-eCharger-API-v2).

## Installing the library locally

```bash
python3 -m pip install -e .
```

> __This is needed for the first time when working with the library/examples/tests.__

## Example usage

```bash
GOE_API_URL="https://REPLACE_ME.api.v3.go-e.io" GOE_API_TOKEN="REPLACE_ME" python3 examples/simple.py
```

or

```python
from goechargerv2.goecharger import GoeChargerApi

charger = GoeChargerApi('provide_api_url', 'provide_api_token')
# or you can define additional optional parameters
# charger = GoeChargerApi('provide_api_url', 'provide_api_token', timeout=10, wait=True)
 
print(charger.request_status())
```

## Development

### Linting

```bash
pylint tests/*.py src/**/*.py
```

### Unit testing

```bash
python3 -m unittest -v tests/*.py
```
