from pydantic import BaseModel, EmailStr
from typing import List, Optional

class OperatingHours(BaseModel):
    day: str
    opening_time: str
    closing_time: str

class WasteCategory(BaseModel):
    category_id: int
    name: str
    description: str
    process: str
    tips: str
    icon: Optional[str] = None

class RecyclingCenter(BaseModel):
    center_id: int
    name: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    operating_hours: List[OperatingHours]
    waste_categories: List[WasteCategory]