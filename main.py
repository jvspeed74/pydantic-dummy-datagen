import json
from enum import Enum
from random import choice
from types import UnionType
from typing import Any, Type, Union, get_origin, get_args, TypeVar

from annotated_types import Interval
from faker import Faker
from pydantic import BaseModel, RootModel, StringConstraints
from typing_extensions import ParamSpec

fake = Faker()

TModel = TypeVar('TModel', bound=BaseModel)


def generate_dummy_data(model: Type[TModel]) -> str:
    """Generate a dummy JSON string from a Pydantic v2 model, handling nested structures, lists, dicts, and constraints."""

    def extract_metadata(metadata: list[Any]) -> dict:
        """Extracts constraint metadata from Pydantic v2 FieldInfo metadata list."""
        extracted: dict = {}
        for item in metadata:
            if isinstance(item, StringConstraints):
                extracted.update(item.__dict__)
            elif isinstance(item, Interval):
                for attr in ['gt', 'ge', 'lt', 'le']:
                    if hasattr(item, attr):
                        extracted[attr] = getattr(item, attr)

        extracted = {k: v for k, v in extracted.items() if v is not None}
        return extracted

    def generate_value(field_type: Any, metadata: dict) -> Any:
        """Generate a dummy value based on the field type, applying constraints where possible."""

        origin: ParamSpec | Type[UnionType] | type | None = get_origin(field_type)
        args: tuple[Any, ...] = get_args(field_type)

        # Handle Optional[X] (Union[X, None])
        if origin is Union and type(None) in args:
            non_none_type = next(t for t in args if t is not type(None))
            return choice([None, generate_value(non_none_type, metadata)])

        # Handle Root Models
        if isinstance(field_type, type) and issubclass(field_type, RootModel):
            root_type: object = field_type.__annotations__.get('root', Any)
            return generate_value(root_type, metadata)

        # Handle nested Pydantic models
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return generate_dummy_instance(field_type)

        # Handle Enums
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            return choice(list(field_type)).value

        # Handle Lists
        if origin is list:
            sub_type: object = args[0] if args else Any
            return [generate_value(sub_type, metadata) for _ in range(3)]

        # Handle Dicts
        if origin is dict:
            key_type, value_type = args if args else (str, Any)
            return {fake.word(): generate_value(value_type, metadata) for _ in range(2)}

        # Handle Tuples
        if origin is tuple:
            return tuple(generate_value(t, metadata) for t in args)

        # Handle primitive types with explicit check for bool first
        if field_type is bool or (isinstance(field_type, type) and issubclass(field_type, bool)):
            return fake.boolean()

        # Handle constrained types
        if isinstance(field_type, type):
            if issubclass(field_type, int):
                min_val = metadata.get("ge", metadata.get("gt", 1) + 1)
                max_val = metadata.get("le", metadata.get("lt", 1000) - 1)
                return fake.random_int(min=min_val, max=max_val)
            elif issubclass(field_type, float):
                min_val = metadata.get("ge", metadata.get("gt", 1.0) + 0.1)
                max_val = metadata.get("le", metadata.get("lt", 1000.0) - 0.1)
                return round(fake.pyfloat(min_value=min_val, max_value=max_val), 2)
            elif issubclass(field_type, str):
                min_length = metadata.get("min_length", 5)
                max_length = metadata.get("max_length", 15)

                if min_length == max_length:
                    return fake.pystr(min_chars=min_length, max_chars=min_length)

                return fake.text(max_nb_chars=max_length)[:max(min_length, max_length)]

        # Default fallback
        if field_type is str:
            return fake.sentence(nb_words=4)
        elif field_type is int:
            return fake.random_int(min=1, max=1000)
        elif field_type is float:
            return round(fake.pyfloat(), 2)
        elif field_type is list:
            return [fake.word() for _ in range(3)]
        # Handle Any type
        elif field_type is Any:
            return choice([fake.word(), fake.random_int(min=1, max=1000), fake.pyfloat(), fake.sentence(nb_words=4)])

        return None

    def generate_dummy_instance(model: Type[TModel]) -> Any:
        """Generate a dummy instance of a Pydantic v2 model."""

        # Handle Root Models in Pydantic v2
        if issubclass(model, RootModel):
            root_type: object = model.__annotations__.get('root', Any)
            return generate_value(root_type, {})

        return {
            field_name: generate_value(field_info.annotation, extract_metadata(field_info.metadata))
            for field_name, field_info in model.model_fields.items()
        }

    # Create the dummy instance and return as JSON string
    dummy_instance: Any = generate_dummy_instance(model)
    return json.dumps(dummy_instance, indent=4)
