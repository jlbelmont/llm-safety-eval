from pathlib import Path
import json
import yaml
import jsonschema


def test_models_schema_validation():
    schema = json.loads(Path("configs/schema/models.schema.json").read_text())
    data = yaml.safe_load(Path("configs/models.yaml").read_text())
    jsonschema.validate(instance=data, schema=schema)


def test_providers_schema_validation():
    schema = json.loads(Path("configs/schema/providers.schema.json").read_text())
    data = yaml.safe_load(Path("configs/providers.yaml").read_text())
    jsonschema.validate(instance=data, schema=schema)
