from pydantic import BaseModel

class Product(BaseModel):
    """Validation model for a product in the inventory system."""
    id: int
    name: str
    description: str
    price: float
    quantity: int

