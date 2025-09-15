from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from models.models import (ContractStatusEnum, DepartmentEnum,
                           PermissionTypeEnum, ResourceTypeEnum)


class Permission(BaseModel):
    id: int
    permission_type: PermissionTypeEnum
    resource_type: ResourceTypeEnum

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    username: str
    department: DepartmentEnum
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    id: int
    name: str
    email: EmailStr
    username: str
    password: str
    department: DepartmentEnum
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


class Resource(BaseModel):
    id: int
    type: str
    creation_date: datetime
    modified_date: datetime
    user_id: int
    user: User

    class Config:
        from_attributes = True


class Contract(Resource):
    id: int
    amount: int
    due_amount: int
    status: ContractStatusEnum
    client_id: int
    event_id: int
    client: Optional["Client"] = []
    event: List["Event"] = []


class Client(Resource):
    id: int
    full_name: str
    email: EmailStr
    telephone: str
    company_name: str
    # events: List["Event"] = []
    # contracts: List[Contract] = []


class Event(Resource):
    id: int
    start: datetime
    end: datetime
    location: str
    attendees: int
    notes: str
    client_id: int
    client: Optional[Client] = None
    contract: Optional[Contract] = None
