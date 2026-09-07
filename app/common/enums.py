from enum import Enum


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    VILLA = "villa"
    PLOT = "plot"
    HOUSE = "house"
    COMMERCIAL = "commercial"
    PROJECT = "project"


class PropertyStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    RENTED = "rented"
    EXPIRED = "expired"
    PENDING = "pending"


class InquiryType(str, Enum):
    BUY = "buy"
    RENT = "rent"
    PROJECT = "project"


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    AGENT = "agent"
    BUILDER = "builder"
    ADMIN = "admin"
