from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    position: str
    jersey_number: int
    phone: str | None = None
    email: EmailStr | None = None
    emergency_contact: str | None = None
    medical_notes: str | None = None
    team_id: int


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    position: str | None = None
    jersey_number: int | None = None
    phone: str | None = None
    email: EmailStr | None = None
    emergency_contact: str | None = None
    medical_notes: str | None = None
    team_id: int | None = None
    is_active: bool | None = None


class PlayerResponse(PlayerBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)