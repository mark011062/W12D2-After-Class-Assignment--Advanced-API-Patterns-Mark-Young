from pydantic import BaseModel, EmailStr, field_validator, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt limit

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters.")
        if v.lower() == v or v.upper() == v:
            raise ValueError("Password must include mixed case letters.")
        if not any(ch.isdigit() for ch in v):
            raise ValueError("Password must include a digit.")
        if not any(not ch.isalnum() for ch in v):
            raise ValueError("Password must include a symbol.")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
