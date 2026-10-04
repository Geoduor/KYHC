from pydantic import BaseModel, ConfigDict, EmailStr


class CoachBase(BaseModel):
    first_name: str
    last_name: str
    phone: str | None = None
    email: EmailStr
    qualification: str | None = None
    experience_years: int = 0
    team_id: int


class CoachCreate(CoachBase):
    pass


class CoachUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    qualification: str | None = None
    experience_years: int | None = None
    team_id: int | None = None
    is_active: bool | None = None


class CoachResponse(CoachBase):
    id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )