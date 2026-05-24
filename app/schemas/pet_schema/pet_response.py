from app.schemas.pet_schema.pet_base import PetBase



class PetResponse(PetBase):
    id_pet: int

    class Config:
        from_attributes = True