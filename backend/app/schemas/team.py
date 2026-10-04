from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    name: str
    category: str
    description: str | None = None
    coach_name: str | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    coach_name: str | None = None
    is_active: bool | None = None


class TeamResponse(TeamBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)