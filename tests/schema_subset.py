"""A minimal JSON Schema validator for the keyword subset the published
schemas use (operator ruling D8, docs/ops/plan-2026-09-13-agent-discovery.md
§3: a stdlib validator in tests, no new dependency).

Supported: `type` (a name or a list), `properties`, `required`, `items`,
`pattern`, `enum`, `const`, `allOf`, `anyOf`, and boolean
`additionalProperties`. Annotation keywords (`$schema`, `$id`, `title`,
`description`) are ignored. Any other keyword raises SchemaError, so the
subset cannot grow silently: a schema that reaches for `$ref` or `oneOf`
has to extend this file on purpose.

Not a test module (no `test_` prefix); imported by tests/test_agent_discovery.py.
"""

import re

_ANNOTATIONS = {"$schema", "$id", "title", "description"}
_KEYWORDS = {"type", "properties", "required", "items", "pattern", "enum",
             "const", "allOf", "anyOf", "additionalProperties"}
_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: (isinstance(v, (int, float))
                         and not isinstance(v, bool)),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class SchemaError(Exception):
    """The schema uses a keyword this subset does not implement."""


class ValidationError(Exception):
    """The instance does not satisfy the schema; the message names the path."""


def validate(instance, schema, path="$"):
    unknown = set(schema) - _KEYWORDS - _ANNOTATIONS
    if unknown:
        raise SchemaError(f"{path}: unsupported keyword(s) {sorted(unknown)}")
    if "type" in schema:
        names = schema["type"]
        names = [names] if isinstance(names, str) else list(names)
        for name in names:
            if name not in _TYPES:
                raise SchemaError(f"{path}: unknown type {name!r}")
        if not any(_TYPES[name](instance) for name in names):
            raise ValidationError(
                f"{path}: expected {names}, got {type(instance).__name__}")
    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(f"{path}: {instance!r} not in enum")
    if "pattern" in schema and isinstance(instance, str) \
            and not re.search(schema["pattern"], instance):
        raise ValidationError(
            f"{path}: {instance!r} does not match {schema['pattern']!r}")
    if isinstance(instance, dict):
        for key in schema.get("required", ()):
            if key not in instance:
                raise ValidationError(f"{path}: missing required {key!r}")
        properties = schema.get("properties", {})
        for key, sub in properties.items():
            if key in instance:
                validate(instance[key], sub, f"{path}.{key}")
        extra = schema.get("additionalProperties", True)
        if not isinstance(extra, bool):
            raise SchemaError(f"{path}: additionalProperties must be boolean")
        if extra is False:
            for key in instance:
                if key not in properties:
                    raise ValidationError(f"{path}: unexpected {key!r}")
    if isinstance(instance, list) and "items" in schema:
        for i, element in enumerate(instance):
            validate(element, schema["items"], f"{path}[{i}]")
    for sub in schema.get("allOf", ()):
        validate(instance, sub, path)
    if "anyOf" in schema:
        errors = []
        for sub in schema["anyOf"]:
            try:
                validate(instance, sub, path)
                break
            except ValidationError as exc:
                errors.append(str(exc))
        else:
            raise ValidationError(f"{path}: no anyOf branch matched: {errors}")
