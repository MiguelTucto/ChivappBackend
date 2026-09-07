from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    fullname: str | None = None
    role: str
    username: str | None = None
    phone: str | None = None
    accepted_terms: bool = False


class SetPasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
    token: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = ""
    new_password: str = Field(min_length=8, max_length=128)


class PasswordSetupPreviewOut(BaseModel):
    email: EmailStr
    fullname: str
    specialties: list[str] = Field(default_factory=list)
    leader_name: str | None = None
    requires_password: bool = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthCompleteRequest(BaseModel):
    role: str
    username: str | None = None
    phone: str | None = None


class OAuthAccountOut(BaseModel):
    provider: str
    email: str | None = None
    linked: bool = True


class OAuthAccountsOut(BaseModel):
    accounts: list[OAuthAccountOut]
    has_password: bool


class OAuthPendingOut(BaseModel):
    email: str | None = None
    fullname: str
    provider: str
    picture_url: str | None = None
