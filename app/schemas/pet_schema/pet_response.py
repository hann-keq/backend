from app.schemas.pet_schema.pet_base import PetBase



class PetResponse(PetBase):
    id: int

    class Config:
        from_attributes = True