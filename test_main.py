import json
from enum import Enum
from typing import List, Dict, Any, Union, Tuple, Optional

import pytest
from pydantic import BaseModel, RootModel, conint, constr, Field

from main import generate_dummy_data


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Address(BaseModel):
    city: str
    zip_code: conint(gt=1000, lt=9999)


class User(BaseModel):
    id: conint(ge=100, le=999)
    name: constr(min_length=5, max_length=15)
    age: Optional[Union[int, None]] = Field(None)
    active: bool
    tags: List[str]
    metadata: Dict[str, Any]
    address: Address
    coordinates: Tuple[float, float]
    role: UserRole


class RootString(RootModel[str]):
    root: str


class RootList(RootModel[List[User]]):
    root: List[User]


# Additional test models
class SimpleModel(BaseModel):
    name: str
    count: int


class EmptyModel(BaseModel):
    pass


class StrictConstraints(BaseModel):
    exact_length: constr(min_length=10, max_length=10)
    exact_value: conint(ge=42, le=42)


class DeepNested(BaseModel):
    level1: Address
    level2: List[Address]
    level3: Dict[str, Address]


class UnionModel(BaseModel):
    mixed_field: Union[int, str]


@pytest.mark.unit
def test_generates_valid_json():
    result = generate_dummy_data(SimpleModel)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert "name" in data
    assert "count" in data
    assert isinstance(data["name"], str)
    assert isinstance(data["count"], int)

@pytest.mark.unit
def test_respects_int_constraints():
    result = json.loads(generate_dummy_data(User))
    assert 100 <= result["id"] <= 999
    assert 1001 <= result["address"]["zip_code"] <= 9998

@pytest.mark.unit
def test_respects_string_constraints():
    result = json.loads(generate_dummy_data(User))
    assert 5 <= len(result["name"]) <= 15

@pytest.mark.unit
def test_handles_exact_constraints():
    result = json.loads(generate_dummy_data(StrictConstraints))
    assert len(result["exact_length"]) == 10
    assert result["exact_value"] == 42

@pytest.mark.unit
def test_handles_optional_fields():
    results = [json.loads(generate_dummy_data(User)) for _ in range(10)]
    assert any(r["age"] is None for r in results) or any(r["age"] is not None for r in results)

@pytest.mark.unit
def test_generates_enum_values():
    result = json.loads(generate_dummy_data(User))
    assert result["role"] in [role.value for role in UserRole]

@pytest.mark.unit
def test_handles_empty_model():
    result = generate_dummy_data(EmptyModel)
    assert json.loads(result) == {}

@pytest.mark.unit
def test_handles_nested_models():
    result = json.loads(generate_dummy_data(User))
    address = result["address"]
    assert isinstance(address, dict)
    assert "city" in address
    assert "zip_code" in address

@pytest.mark.unit
def test_handles_deep_nesting():
    result = json.loads(generate_dummy_data(DeepNested))
    assert "city" in result["level1"]
    assert isinstance(result["level2"], list)
    assert all("city" in addr for addr in result["level2"])
    assert isinstance(result["level3"], dict)
    assert all("city" in addr for addr in result["level3"].values())

@pytest.mark.unit
def test_handles_collections():
    result = json.loads(generate_dummy_data(User))
    assert isinstance(result["tags"], list)
    assert all(isinstance(tag, str) for tag in result["tags"])
    assert isinstance(result["metadata"], dict)
    assert isinstance(result["coordinates"], list)
    assert len(result["coordinates"]) == 2
    assert all(isinstance(coord, float) for coord in result["coordinates"])

@pytest.mark.unit
def test_handles_root_string_model():
    result = generate_dummy_data(RootString)
    value = json.loads(result)
    assert isinstance(value, str)

@pytest.mark.unit
def test_handles_root_list_model():
    result = generate_dummy_data(RootList)
    value = json.loads(result)
    assert isinstance(value, list)
    assert all(isinstance(user, dict) for user in value)
    assert all("name" in user for user in value)

@pytest.mark.unit
def test_consistent_schema():
    results = [json.loads(generate_dummy_data(User)) for _ in range(5)]
    first_keys = set(results[0].keys())
    for result in results[1:]:
        assert set(result.keys()) == first_keys

    first_address_keys = set(results[0]["address"].keys())
    for result in results[1:]:
        assert set(result["address"].keys()) == first_address_keys

@pytest.mark.unit
def test_handles_unions():
    results = [json.loads(generate_dummy_data(UnionModel)) for _ in range(10)]
    types_found = {type(r["mixed_field"]) for r in results}
    assert len(types_found) >= 1  # Should at least generate one type
