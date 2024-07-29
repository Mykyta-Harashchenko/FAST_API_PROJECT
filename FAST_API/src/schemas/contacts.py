from datetime import datetime

from pydantic import BaseModel, EmailStr, Field



class ContactSchema(BaseModel):
    id: int = Field(1, ge=1)
    name: str = Field('Simon', min_length=3, max_length=25)
    surname: str = Field('Simon', min_length=3, max_length=25)
    phone: str = Field(1, min_length=3, max_length=25)
    email: EmailStr = Field('simon@example.com')
    birthday: datetime = Field('2000-01-01')
    extra: str = Field('Simon', min_length=3, max_length=255)


class ContactUpdateSchema(ContactSchema):
    id: int = Field(1, ge=1)


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    phone: str
    email: EmailStr
    birthday: datetime
    extra: str



    class Config:
        from_attributes = True
