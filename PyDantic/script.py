from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int=Field(gt=0)
    name: str=Field(min_length=3)
    email: EmailStr
    is_active: bool=True

user=User(id=1,name="Shubham",email="test@sample.com")

print(user)
