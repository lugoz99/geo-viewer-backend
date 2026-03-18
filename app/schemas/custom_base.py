from pydantic import BaseModel, ConfigDict


class CustomBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, validate_assignment=True, str_strip_whitespace=True
    )


# All models inherit this
class UserCreate(CustomBase):
    name: str
    email: str


class UserResponse(CustomBase):
    id: int
    name: str
    email: str
