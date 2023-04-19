from pydantic import (
    BaseModel,
    Field,
    validator,
    BaseSettings,
)
from pendulum import Date
from decimal import Decimal


class Mixin(BaseModel):
    id: int
    time_stamp: Date


class AD_URL(Mixin):
    url: str
    status: str
    tablez: str
    locality: str
    section_id: int


class Section(Mixin):
    status: str
    site: str


class AVITO_ERROR(Mixin):
    status: str
    urls: str


class AD_SALES(Mixin):
    name: str
    address: str
    price_value: Decimal
    price_currency: str
    price_original: str
    x: float
    y: float
    square_value: float
    square_currency: str
    square_original: str
    description: str
    other: str
    screenshot_file: str | None
    url: str
    phone: str | None
    avito_id: int
    category: str
    locality: str
    section_id: int


class AD_SALES_FLAT(AD_SALES):
    floor: int
    house_floors: int
    house_type: str
    rooms: int


class AD_SALES_GARAGE(AD_SALES):
    pass


class AD_SALES_HOUSE(AD_SALES):
    wall: str
    to_city: str
    floors: int
    square_zu: str


class AD_SALES_ZU(AD_SALES):
    to_city: str


class AD_SALES_COMMERCIAL(AD_SALES):
    pass

