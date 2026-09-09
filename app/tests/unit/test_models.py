import pytest
from sqlalchemy.orm import configure_mappers
from app.models import (
    User,
    Agent,
    Builder,
    Admin,
    AdminActionLog,
    Property,
    ResidentialPropertyDetails,
    CommercialPropertyDetails,
    PlotPropertyDetails,
    PropertyMedia,
    PropertyDocument,
    ProjectMedia,
    Project,
    ProjectUnit,
    Amenity,
    Country,
    State,
    City,
    Locality,
    SubLocality,
    Favorite,
    SavedSearch,
    Inquiry,
    Visit,
    Notification,
    Review,
    Report,
    Payment,
    RefreshToken,
    OTPVerification,
)


def test_sqlalchemy_mappers_configure_cleanly():
    """Verify configure_mappers() does not raise InvalidRequestError or relationship errors."""
    configure_mappers()


def test_user_relationships_exist():
    """Verify User model has all defined bidirectional relationships."""
    user = User()
    assert hasattr(user, "agent_profile")
    assert hasattr(user, "builder_profile")
    assert hasattr(user, "admin_profile")
    assert hasattr(user, "properties")
    assert hasattr(user, "favorites")
    assert hasattr(user, "saved_searches")
    assert hasattr(user, "inquiries")
    assert hasattr(user, "visits")
    assert hasattr(user, "notifications")
    assert hasattr(user, "subscriptions")
    assert hasattr(user, "payments")
    assert hasattr(user, "reviews")
    assert hasattr(user, "reports")
    assert hasattr(user, "refresh_tokens")
    assert hasattr(user, "otp_verifications")


def test_agent_relationships_exist():
    agent = Agent()
    assert hasattr(agent, "user")
    assert hasattr(agent, "properties")
    assert hasattr(agent, "visits")
    assert hasattr(agent, "inquiries")
    assert hasattr(agent, "reviews")


def test_builder_relationships_exist():
    builder = Builder()
    assert hasattr(builder, "user")
    assert hasattr(builder, "projects")
    assert hasattr(builder, "properties")
    assert hasattr(builder, "inquiries")
    assert hasattr(builder, "reviews")


def test_admin_relationships_exist():
    admin = Admin()
    assert hasattr(admin, "user")
    assert hasattr(admin, "action_logs")

    log = AdminActionLog()
    assert hasattr(log, "admin")


def test_property_relationships_exist():
    prop = Property()
    assert hasattr(prop, "owner")
    assert hasattr(prop, "agent")
    assert hasattr(prop, "builder")
    assert hasattr(prop, "project")
    assert hasattr(prop, "country")
    assert hasattr(prop, "state")
    assert hasattr(prop, "city")
    assert hasattr(prop, "locality")
    assert hasattr(prop, "sub_locality")
    assert hasattr(prop, "media")
    assert hasattr(prop, "documents")
    assert hasattr(prop, "amenities")
    assert hasattr(prop, "residential_details")
    assert hasattr(prop, "commercial_details")
    assert hasattr(prop, "plot_details")
    assert hasattr(prop, "inquiries")
    assert hasattr(prop, "visits")
    assert hasattr(prop, "favorites")


def test_property_sub_details_relationships():
    res = ResidentialPropertyDetails()
    assert hasattr(res, "property")

    comm = CommercialPropertyDetails()
    assert hasattr(comm, "property")

    plot = PlotPropertyDetails()
    assert hasattr(plot, "property")


def test_project_relationships_exist():
    proj = Project()
    assert hasattr(proj, "builder")
    assert hasattr(proj, "units")
    assert hasattr(proj, "media")
    assert hasattr(proj, "amenities")
    assert hasattr(proj, "properties")
    assert hasattr(proj, "inquiries")

    unit = ProjectUnit()
    assert hasattr(unit, "project")


def test_amenity_relationships_exist():
    amenity = Amenity()
    assert hasattr(amenity, "properties")
    assert hasattr(amenity, "projects")


def test_locations_hierarchy_relationships():
    c = Country()
    assert hasattr(c, "states")

    s = State()
    assert hasattr(s, "country")
    assert hasattr(s, "cities")

    city = City()
    assert hasattr(city, "state")
    assert hasattr(city, "localities")

    loc = Locality()
    assert hasattr(loc, "city")
    assert hasattr(loc, "sub_localities")

    sub_loc = SubLocality()
    assert hasattr(sub_loc, "locality")


def test_engagement_models_relationships():
    fav = Favorite()
    assert hasattr(fav, "user")
    assert hasattr(fav, "property")

    inq = Inquiry()
    assert hasattr(inq, "user")
    assert hasattr(inq, "property")
    assert hasattr(inq, "project")
    assert hasattr(inq, "agent")
    assert hasattr(inq, "builder")

    visit = Visit()
    assert hasattr(visit, "user")
    assert hasattr(visit, "property")
    assert hasattr(visit, "agent")

    review = Review()
    assert hasattr(review, "user")
    assert hasattr(review, "agent")
    assert hasattr(review, "builder")

    report = Report()
    assert hasattr(report, "reporter")
    assert hasattr(report, "reported_user")
    assert hasattr(report, "property")
    assert hasattr(report, "agent")
    assert hasattr(report, "builder")
    assert hasattr(report, "resolver")

    rt = RefreshToken()
    assert hasattr(rt, "user")

    otp = OTPVerification()
    assert hasattr(otp, "user")
