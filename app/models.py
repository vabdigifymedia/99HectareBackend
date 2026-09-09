# app/core/models.py

# =========================
# Users
# =========================
from app.modules.users.models import User


# =========================
# Auth
# =========================
from app.modules.auth.models import (
    RefreshToken,
    OTPVerification,
)


# =========================
# Admin
# =========================
from app.modules.admin.models import (
    Admin,
    AdminActionLog,
)


# =========================
# Locations
# =========================
from app.modules.locations.models import (
    Country,
    State,
    City,
    Locality,
    SubLocality,
)


# =========================
# Builders
# =========================
from app.modules.builders.models import Builder


# =========================
# Projects
# =========================
from app.modules.projects.models import (
    Project,
    ProjectUnit,
)


# =========================
# Properties
# =========================
from app.modules.properties.models import (
    Property,
    ResidentialPropertyDetails,
    CommercialPropertyDetails,
    PlotPropertyDetails,
)


# =========================
# Agents
# =========================
from app.modules.agents.models import Agent


# =========================
# Amenities
# =========================
from app.modules.amenities.models import (
    Amenity,
    property_amenities,
    project_amenities,
)


# =========================
# Media
# =========================
from app.modules.media.models import (
    PropertyMedia,
    PropertyDocument,
    ProjectMedia,
)


# =========================
# Favorites
# =========================
from app.modules.favorites.models import Favorite


# =========================
# Saved Searches
# =========================
from app.modules.saved_searches.models import SavedSearch


# =========================
# Inquiries
# =========================
from app.modules.inquiries.models import Inquiry


# =========================
# Visits
# =========================
from app.modules.visits.models import Visit


# =========================
# Notifications
# =========================
from app.modules.notifications.models import Notification


# =========================
# Reviews
# =========================
from app.modules.reviews.models import Review


# =========================
# Reports
# =========================
from app.modules.reports.models import Report


# =========================
# Subscriptions
# =========================
from app.modules.subscriptions.models import (
    SubscriptionPlan,
    UserSubscription,
)


# =========================
# Payments
# =========================
from app.modules.payments.models import Payment


__all__ = [
    # Users
    "User",

    # Auth
    "RefreshToken",
    "OTPVerification",

    # Admin
    "Admin",
    "AdminActionLog",

    # Locations
    "Country",
    "State",
    "City",
    "Locality",
    "SubLocality",

    # Builders
    "Builder",

    # Projects
    "Project",
    "ProjectUnit",

    # Properties
    "Property",
    "ResidentialPropertyDetails",
    "CommercialPropertyDetails",
    "PlotPropertyDetails",

    # Agents
    "Agent",

    # Amenities
    "Amenity",
    "property_amenities",
    "project_amenities",

    # Media
    "PropertyMedia",
    "PropertyDocument",
    "ProjectMedia",

    # Favorites
    "Favorite",

    # Saved Searches
    "SavedSearch",

    # Inquiries
    "Inquiry",

    # Visits
    "Visit",

    # Notifications
    "Notification",

    # Reviews
    "Review",

    # Reports
    "Report",

    # Subscriptions
    "SubscriptionPlan",
    "UserSubscription",

    # Payments
    "Payment",
]