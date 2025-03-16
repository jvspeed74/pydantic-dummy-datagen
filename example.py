from enum import Enum
from typing import List, Tuple, Any, Dict, Optional, Union

from pydantic import RootModel, Field, constr, conint, BaseModel

from main import generate_dummy_data


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Address(BaseModel):
    city: str
    zip_code: conint(gt=10000, lt=99999)


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


class RootList(RootModel[List[User]]):
    root: List[User]

# Generate dummy data for User and output to console
print(generate_dummy_data(User))

# Generate dummy data for RootList and write to JSON file
with open("dummy_data.json", "w") as f:
    f.write(generate_dummy_data(RootList))
