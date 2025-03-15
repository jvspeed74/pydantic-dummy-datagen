# Pydantic Dummy Data Generator

A utility library for generating realistic dummy JSON data from Pydantic v2 models. Perfect for testing, development, and documentation purposes.

## Features

- Generates JSON data that conforms to your Pydantic model structure and constraints
- Supports a wide variety of field types:
  - Basic types (str, int, float, bool)
  - Complex types (List, Dict, Tuple)
  - Nested Pydantic models
  - Enum values
  - Optional fields
  - Pydantic's RootModel
- Respects field constraints such as:
  - String length (min_length, max_length)
  - Numeric bounds (ge, gt, le, lt)
  - Required vs optional fields
- Produces realistic data using the Faker library

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from pydantic import BaseModel, conint, constr
from enum import Enum
from typing import List, Dict, Any, Optional

from main import generate_dummy_data

# Define your Pydantic models
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
    role: UserRole
    address: Address
    active: bool
    tags: List[str]

# Generate dummy data as JSON
dummy_data = generate_dummy_data(User)
print(dummy_data)
```

## Example Output

```json
{
    "id": 542,
    "name": "Drive family.",
    "role": "guest",
    "address": {
        "city": "Stock mission.",
        "zip_code": 5847
    },
    "active": true,
    "tags": [
        "Door",
        "long",
        "decision"
    ]
}
```

## Advanced Features

### Root Models

The generator supports Pydantic's RootModel:

```python
from pydantic import RootModel
from typing import List

class RootString(RootModel[str]):
    root: str

class RootList(RootModel[List[User]]):
    root: List[User]

# Generate data for root models
root_string_data = generate_dummy_data(RootString)
root_list_data = generate_dummy_data(RootList)
```

### Exact Value Generation

For fields with exact constraints (min and max are equal), the generator will create values of the exact required length or value.

## Testing

The project includes comprehensive pytest tests that verify all functionality:

```bash
pytest test_main.py
```

## Dependencies

- pydantic >= 2.0
- faker
- annotated-types
- typing-extensions

## License

[MIT](LICENSE)