import asyncio
import json
import os
import re
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app import models  # noqa: F401 - Register all models with SQLAlchemy
from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.modules.admin.models import Admin
from app.modules.agents.models import Agent
from app.modules.amenities.models import Amenity, property_amenities, project_amenities
from app.modules.builders.models import Builder
from app.modules.inquiries.models import Inquiry
from app.modules.locations.models import City, Country, Locality, State, SubLocality
from app.modules.media.models import ProjectMedia, PropertyMedia
from app.modules.projects.models import Project, ProjectUnit
from app.modules.properties.models import (
    CommercialPropertyDetails,
    PlotPropertyDetails,
    Property,
    ResidentialPropertyDetails,
)
from app.modules.reports.models import Report
from app.modules.reviews.models import Review
from app.modules.subscriptions.models import SubscriptionPlan
from app.modules.users.models import User
from app.modules.visits.models import Visit


def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", s or "").strip("-").lower()


def parse_numeric(val, default=0.0) -> float:
    if val is None:
        return default
    if isinstance(val, (int, float, Decimal)):
        return float(val)
    if isinstance(val, str):
        # Remove currency symbols and formatting
        cleaned = re.sub(r"[^\d.]", "", val)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


async def seed():
    print("=== Starting 99-Hectare Data Seeder ===")
    json_path = os.path.join(os.path.dirname(__file__), "frontend_seed_data.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Missing {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with AsyncSessionLocal() as db:
        # ── 1. Seed Locations ────────────────────────────────────────────────
        print("\n--- Seeding Locations ---")
        # Country
        country_res = await db.execute(select(Country).where(Country.name == "India"))
        country = country_res.scalars().first()
        if not country:
            country = Country(name="India", iso_code="IN", phone_code="+91")
            db.add(country)
            await db.flush()
        country_id = country.id
        print(f"Country: India (ID: {country_id})")

        # States
        state_map = {}
        for st in data.get("states", []):
            res = await db.execute(select(State).where(State.name == st["name"]))
            existing = res.scalars().first()
            if not existing:
                existing = State(country_id=country_id, name=st["name"], state_code=st.get("state_code", "IN"))
                db.add(existing)
                await db.flush()
            state_map[st["name"].lower()] = existing.id
            state_map[existing.name.lower()] = existing.id
        print(f"States loaded: {len(state_map)}")

        # Cities
        city_map = {}
        for ct in data.get("cities", []):
            res = await db.execute(select(City).where(City.name == ct["name"]))
            existing = res.scalars().first()
            st_id = state_map.get(list(state_map.keys())[0], 1)
            # Find state
            if ct.get("state_id") == 1:
                st_id = state_map.get("haryana", st_id)
            elif ct.get("state_id") == 2:
                st_id = state_map.get("maharashtra", st_id)
            elif ct.get("state_id") == 3:
                st_id = state_map.get("karnataka", st_id)
            elif ct.get("state_id") == 4:
                st_id = state_map.get("uttar pradesh", st_id)
            elif ct.get("state_id") == 5:
                st_id = state_map.get("delhi ncr", st_id)

            if not existing:
                existing = City(
                    state_id=st_id,
                    name=ct["name"],
                    latitude=ct.get("latitude"),
                    longitude=ct.get("longitude"),
                )
                db.add(existing)
                await db.flush()
            city_map[ct["name"].lower()] = existing.id
            city_map[existing.name.lower()] = existing.id

        # Common city synonyms
        city_map["gurgaon"] = city_map.get("gurugram", 1)
        city_map["bangalore"] = city_map.get("bengaluru", 3)
        city_map["delhi"] = city_map.get("south delhi", 5)
        city_map["noida"] = city_map.get("noida", 4)
        city_map["mumbai"] = city_map.get("mumbai", 2)
        print(f"Cities loaded: {len(city_map)}")

        # Localities
        locality_map = {}
        for loc in data.get("localities", []):
            res = await db.execute(select(Locality).where(Locality.name == loc["name"]))
            existing = res.scalars().first()
            cid = loc.get("city_id", 1)
            if not existing:
                existing = Locality(
                    city_id=cid,
                    name=loc["name"],
                    pincode=loc.get("pincode"),
                    latitude=loc.get("latitude"),
                    longitude=loc.get("longitude"),
                )
                db.add(existing)
                await db.flush()
            locality_map[loc["name"].lower()] = existing.id
            # Also map simplified name
            simple_name = loc["name"].split("(")[0].strip().lower()
            locality_map[simple_name] = existing.id
        print(f"Localities loaded: {len(locality_map)}")

        # ── 2. Seed Amenities ────────────────────────────────────────────────
        print("\n--- Seeding Amenities ---")
        amenity_map = {}
        for am in data.get("amenities", []):
            res = await db.execute(select(Amenity).where(Amenity.name == am["name"]))
            existing = res.scalars().first()
            if not existing:
                existing = Amenity(
                    name=am["name"],
                    category=am.get("category", "Convenience"),
                    icon=am.get("icon", "ShieldCheck"),
                    is_active=True,
                )
                db.add(existing)
                await db.flush()
            amenity_map[am["name"].lower()] = existing.id
            amenity_map[existing.name.lower()] = existing.id
            # Also map keyword
            for word in am["name"].lower().split():
                if len(word) > 3 and word not in amenity_map:
                    amenity_map[word] = existing.id
        print(f"Amenities loaded: {len(amenity_map)}")

        # ── 3. Seed Users & Admins ───────────────────────────────────────────
        print("\n--- Seeding Users & Admins ---")
        user_map = {}
        default_user_pw = hash_password("password123")
        admin_pw = hash_password("admin123")

        for u in data.get("users", []):
            email = u["email"].lower().strip()
            res = await db.execute(select(User).where(User.email == email))
            existing_user = res.scalars().first()
            pw = admin_pw if u.get("role") == "admin" else default_user_pw

            if not existing_user:
                existing_user = User(
                    full_name=u["full_name"],
                    email=email,
                    phone=u.get("phone"),
                    password_hash=pw,
                    role=u.get("role", "buyer").lower(),
                    is_active=True,
                    is_verified=True,
                )
                db.add(existing_user)
                await db.flush()
            else:
                existing_user.full_name = u["full_name"]
                existing_user.phone = u.get("phone")
                existing_user.password_hash = pw
                existing_user.role = u.get("role", "buyer").lower()
                existing_user.is_active = True
                existing_user.is_verified = True
                await db.flush()

            user_map[email] = existing_user.id

            # If admin, ensure admin record
            if existing_user.role == "admin":
                adm_res = await db.execute(select(Admin).where(Admin.user_id == existing_user.id))
                admin_rec = adm_res.scalars().first()
                if not admin_rec:
                    admin_rec = Admin(
                        user_id=existing_user.id,
                        admin_level="SUPER_ADMIN",
                        department="Operations",
                        is_active=True,
                    )
                    db.add(admin_rec)
                    await db.flush()

        print(f"Users seeded: {len(user_map)}")

        # ── 4. Seed Builders ─────────────────────────────────────────────────
        print("\n--- Seeding Builders ---")
        builder_map = {}
        for idx, b in enumerate(data.get("topBuilders", [])):
            b_name = b["name"].strip()
            slug = slugify(b_name)
            b_email = f"contact@{slug}.com"
            b_phone = f"+91 1800 100 {2000 + idx}"
            b_user_res = await db.execute(select(User).where(User.email == b_email))
            b_user = b_user_res.scalars().first()
            if not b_user:
                b_user = User(
                    full_name=f"{b_name} Representative",
                    email=b_email,
                    phone=b_phone,
                    password_hash=default_user_pw,
                    role="builder",
                    is_active=True,
                    is_verified=True,
                )
                db.add(b_user)
                await db.flush()

            b_res = await db.execute(select(Builder).where(Builder.company_name == b_name))
            existing_builder = b_res.scalars().first()
            if not existing_builder:
                existing_builder = Builder(
                    user_id=b_user.id,
                    company_name=b_name,
                    description=f"{b_name} is one of India's leading and most trusted property developers.",
                    website=f"https://www.{slug}.com",
                    email=b_email,
                    phone=b_phone,
                    logo=b.get("logo"),
                    license_number=f"BUILDER-LIC-{slug.upper()[:8]}",
                    rera_registration_number=f"RERA-BLD-{slug.upper()[:8]}-2024",
                    verification_status="VERIFIED",
                    established_year=b.get("experienceYears", 15),
                    is_featured=True,
                    is_active=True,
                )
                db.add(existing_builder)
                await db.flush()
            builder_map[b_name.lower()] = existing_builder.id
            builder_map[slug] = existing_builder.id

        # Additional default builder if needed
        default_builder_id = list(builder_map.values())[0] if builder_map else 1
        print(f"Builders seeded: {len(builder_map)}")

        # ── 5. Seed Agents ───────────────────────────────────────────────────
        print("\n--- Seeding Agents ---")
        agent_map = {}
        for ag in data.get("agents", []):
            ag_user_id = user_map.get(ag.get("email", "").lower())
            if not ag_user_id:
                # Default to Vikram Sharma user
                ag_user_id = user_map.get("vikram.sharma@horizonrealty.in", 3)

            ag_res = await db.execute(select(Agent).where(Agent.user_id == ag_user_id))
            existing_agent = ag_res.scalars().first()
            if not existing_agent:
                existing_agent = Agent(
                    user_id=ag_user_id,
                    agency_name=ag.get("agency_name", "Premier Advisory Partners"),
                    description=ag.get("description"),
                    license_number=ag.get("license_number", "LIC-DEFAULT-001"),
                    experience_years=ag.get("experience_years", 10),
                    profile_image=ag.get("profile_image"),
                    verification_status="VERIFIED",
                    rera_registration_number=ag.get("rera_registration_number", "HRERA-AG-001"),
                    phone=ag.get("phone", "+91 98765 43210"),
                    email=ag.get("email", "agent@horizonrealty.in"),
                    website=ag.get("website", "https://horizonrealty.in"),
                    is_featured=ag.get("is_featured", True),
                    is_active=True,
                )
                db.add(existing_agent)
                await db.flush()
            agent_map[existing_agent.agency_name.lower()] = existing_agent.id
            agent_map[str(existing_agent.id)] = existing_agent.id
            agent_map[ag.get("agency_name", "").lower()] = existing_agent.id
        default_agent_id = list(agent_map.values())[0] if agent_map else 1
        print(f"Agents seeded: {len(agent_map)}")

        # ── 6. Seed Projects ─────────────────────────────────────────────────
        print("\n--- Seeding Projects ---")
        project_map = {}
        all_projects = (
            data.get("projects", {}).get("marketplaceProjects", [])
            + data.get("projects", {}).get("builderProjects", [])
        )
        for proj in all_projects:
            name = proj.get("name") or proj.get("title")
            if not name or name.lower() in project_map:
                continue

            slug = slugify(name)
            p_res = await db.execute(select(Project).where(Project.name == name))
            existing_project = p_res.scalars().first()

            b_name = proj.get("builder", "DLF Limited").lower()
            b_id = builder_map.get(b_name, default_builder_id)

            city_key = proj.get("city", "gurgaon").lower()
            c_id = city_map.get(city_key, 1)

            loc_key = proj.get("location", "").split(",")[0].strip().lower()
            loc_id = locality_map.get(loc_key, 1)

            min_p = parse_numeric(proj.get("minPrice") or proj.get("price"))
            max_p = parse_numeric(proj.get("maxPrice") or proj.get("price")) or (min_p * 1.5 if min_p else None)

            if not existing_project:
                existing_project = Project(
                    builder_id=b_id,
                    name=name,
                    description=proj.get("description", f"Luxury residential development {name}"),
                    project_type=proj.get("type", "Residential Apartments"),
                    status=proj.get("status", "Under Construction"),
                    price_from=Decimal(str(min_p)) if min_p else None,
                    price_to=Decimal(str(max_p)) if max_p else None,
                    total_units=parse_numeric(proj.get("units"), 150),
                    total_towers=parse_numeric(proj.get("towers"), 4),
                    country_id=country_id,
                    state_id=1,
                    city_id=c_id,
                    locality_id=loc_id,
                    address=proj.get("location", "Prime Corridor"),
                    pincode="122002",
                    rera_number=proj.get("reraId", "HRERA-PRJ-2024-999"),
                )
                db.add(existing_project)
                await db.flush()

            project_map[name.lower()] = existing_project.id
            project_map[slug] = existing_project.id

            # Project Media
            images = proj.get("images") or ([proj["image"]] if "image" in proj else [])
            for idx, img_url in enumerate(images):
                pm_res = await db.execute(
                    select(ProjectMedia).where(
                        ProjectMedia.project_id == existing_project.id,
                        ProjectMedia.url == img_url,
                    )
                )
                if not pm_res.scalars().first():
                    db.add(
                        ProjectMedia(
                            project_id=existing_project.id,
                            media_type="IMAGE",
                            url=img_url,
                            sort_order=idx,
                            is_primary=(idx == 0),
                        )
                    )

            # Project Units
            configs = proj.get("configurations") or ["2 BHK", "3 BHK", "4 BHK"]
            for cfg in configs:
                bhk_num = 2
                match = re.search(r"\d+", cfg)
                if match:
                    bhk_num = int(match.group(0))
                pu_res = await db.execute(
                    select(ProjectUnit).where(
                        ProjectUnit.project_id == existing_project.id,
                        ProjectUnit.name == cfg,
                    )
                )
                if not pu_res.scalars().first():
                    db.add(
                        ProjectUnit(
                            project_id=existing_project.id,
                            name=cfg,
                            configuration=cfg,
                            bedrooms=bhk_num,
                            bathrooms=bhk_num,
                            area=Decimal("1800"),
                            price_from=Decimal(str(min_p)) if min_p else Decimal("10000000"),
                            total_units=50,
                            available_units=20,
                        )
                    )
            await db.flush()

        print(f"Projects seeded: {len(project_map)}")

        # ── 7. Seed Properties ───────────────────────────────────────────────
        print("\n--- Seeding Properties ---")
        prop_pools = [
            ("SALE", data.get("properties", {}).get("saleProperties", [])),
            ("RENT", data.get("properties", {}).get("rentProperties", [])),
            ("COMMERCIAL", data.get("properties", {}).get("commercialProperties", [])),
            ("PLOT", data.get("properties", {}).get("landProperties", [])),
            ("SALE", data.get("properties", {}).get("featuredProperties", [])),
            ("SALE", data.get("properties", {}).get("storeProperties", [])),
        ]

        seen_titles = set()
        properties_seeded_count = 0

        for default_listing, prop_list in prop_pools:
            for p in prop_list:
                title = p.get("title")
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                # Determine listing type
                raw_lt = (p.get("listingType") or p.get("listing_type") or p.get("mode") or default_listing).upper()
                listing_type = "SALE"
                if "RENT" in raw_lt:
                    listing_type = "RENT"
                elif "COMMERCIAL" in raw_lt:
                    listing_type = "COMMERCIAL"
                elif "LAND" in raw_lt or "PLOT" in raw_lt:
                    listing_type = "PLOT"

                # Determine property type
                pt = (p.get("propertyType") or p.get("property_type") or p.get("type") or "Apartment").lower()
                if "villa" in pt:
                    property_type = "villa"
                elif "plot" in pt or "land" in pt:
                    property_type = "plot"
                elif "commercial" in pt or "office" in pt or "shop" in pt:
                    property_type = "commercial"
                else:
                    property_type = "apartment"

                # Price & Area
                price = parse_numeric(p.get("price"))
                if not price and "numericPriceLakhs" in p:
                    price = float(p["numericPriceLakhs"]) * 100000.0
                if not price:
                    price = 10000000.0

                area = parse_numeric(p.get("area") or p.get("built_up_area") or p.get("carpet_area"), 1500)
                bhk = p.get("bedrooms") or p.get("baths") or 3
                if isinstance(p.get("bhk"), str):
                    m = re.search(r"\d+", p["bhk"])
                    if m:
                        bhk = int(m.group(0))

                baths = p.get("bathrooms") or p.get("baths") or max(1, bhk)
                park = p.get("parking") or p.get("parking_spaces") or 1

                # Location resolution
                city_name = (p.get("city") or p.get("city_name") or "Gurugram").lower()
                c_id = city_map.get(city_name, 1)

                loc_name = (p.get("locality") or p.get("locality_name") or p.get("location") or "").split(",")[0].strip().lower()
                loc_id = locality_map.get(loc_name, 1)

                # Builder / Agent / Owner resolution
                b_id = None
                if p.get("builderName") or p.get("builder"):
                    b_id = builder_map.get((p.get("builderName") or p.get("builder")).lower())

                ag_id = default_agent_id
                owner_id = user_map.get("pooja.s@singhaniagroup.in", 2)

                # Check if property exists
                p_res = await db.execute(select(Property).where(Property.title == title))
                prop_model = p_res.scalars().first()

                if not prop_model:
                    prop_model = Property(
                        title=title,
                        description=p.get("description", f"Premium verified listing {title}"),
                        property_type=property_type,
                        listing_type=listing_type,
                        status="APPROVED",
                        price=Decimal(str(price)),
                        price_per_sqft=Decimal(str(round(price / max(1, area), 2))),
                        carpet_area=Decimal(str(area)),
                        built_up_area=Decimal(str(area * 1.15)),
                        area_unit="SQFT",
                        bedrooms=bhk if property_type != "plot" else None,
                        bathrooms=baths if property_type != "plot" else None,
                        parking_spaces=park,
                        floor_number=p.get("floor_number", 5),
                        total_floors=p.get("total_floors", 18),
                        furnishing_status=p.get("furnishing", "Semi-Furnished"),
                        facing=p.get("facing", "North-East"),
                        construction_status=p.get("status", "Ready to Move"),
                        country_id=country_id,
                        state_id=1,
                        city_id=c_id,
                        locality_id=loc_id,
                        address=p.get("location") or p.get("address") or "Prime Sector Reach",
                        landmark=p.get("landmark", "Near Metro Station"),
                        pincode=p.get("pincode", "122002"),
                        latitude=p.get("coordinates", {}).get("lat") if isinstance(p.get("coordinates"), dict) else p.get("latitude", 28.455),
                        longitude=p.get("coordinates", {}).get("lng") if isinstance(p.get("coordinates"), dict) else p.get("longitude", 77.085),
                        owner_id=owner_id,
                        agent_id=ag_id,
                        builder_id=b_id,
                        rera_number=p.get("reraId") or p.get("rera_number") or "HRERA-PRP-2024-884",
                        is_verified=True,
                        is_featured=p.get("featured", True),
                        is_premium=True,
                        is_active=True,
                        published_at=datetime.now(timezone.utc),
                    )
                    db.add(prop_model)
                    await db.flush()
                else:
                    prop_model.price = Decimal(str(price))
                    prop_model.status = "APPROVED"
                    prop_model.is_verified = True
                    prop_model.is_active = True
                    await db.flush()

                properties_seeded_count += 1

                # Add Media
                imgs = p.get("images") or p.get("gallery") or ([p["image"]] if "image" in p else [])
                for idx, url in enumerate(imgs):
                    m_res = await db.execute(
                        select(PropertyMedia).where(
                            PropertyMedia.property_id == prop_model.id,
                            PropertyMedia.url == url,
                        )
                    )
                    if not m_res.scalars().first():
                        db.add(
                            PropertyMedia(
                                property_id=prop_model.id,
                                media_type="IMAGE",
                                url=url,
                                sort_order=idx,
                                is_primary=(idx == 0),
                            )
                        )

                # Sub-details
                if property_type in ["apartment", "villa"]:
                    res_det = await db.execute(
                        select(ResidentialPropertyDetails).where(
                            ResidentialPropertyDetails.property_id == prop_model.id
                        )
                    )
                    if not res_det.scalars().first():
                        db.add(
                            ResidentialPropertyDetails(
                                property_id=prop_model.id,
                                servant_room=True,
                                study_room=True,
                                pooja_room=True,
                                store_room=True,
                                electricity_available=True,
                                water_supply="24/7 Municipal & Borewell",
                                gas_pipeline=True,
                            )
                        )
                elif property_type == "commercial":
                    comm_det = await db.execute(
                        select(CommercialPropertyDetails).where(
                            CommercialPropertyDetails.property_id == prop_model.id
                        )
                    )
                    if not comm_det.scalars().first():
                        db.add(
                            CommercialPropertyDetails(
                                property_id=prop_model.id,
                                commercial_sub_type="Office Space",
                                washrooms=2,
                                conference_rooms=1,
                                cabins=2,
                                pantry=True,
                                reception_area=True,
                                power_backup=True,
                            )
                        )
                elif property_type == "plot":
                    plot_det = await db.execute(
                        select(PlotPropertyDetails).where(
                            PlotPropertyDetails.property_id == prop_model.id
                        )
                    )
                    if not plot_det.scalars().first():
                        db.add(
                            PlotPropertyDetails(
                                property_id=prop_model.id,
                                boundary_wall=True,
                                corner_plot=True,
                                gated_community=True,
                            )
                        )

                await db.flush()

        print(f"Total unique properties processed and seeded: {properties_seeded_count}")

        # ── 8. Seed Subscription Plans ───────────────────────────────────────
        print("\n--- Seeding Subscription Plans ---")
        for sp in data.get("subscriptionPlans", []):
            sp_res = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == sp["name"])
            )
            existing_plan = sp_res.scalars().first()
            if not existing_plan:
                existing_plan = SubscriptionPlan(
                    name=sp["name"],
                    description=sp.get("description"),
                    price=Decimal(str(sp.get("price", 4999))),
                    duration_days=sp.get("duration_days", 30),
                    max_listings=sp.get("max_listings", 20),
                    max_inquiries=sp.get("max_inquiries", 50),
                    max_saved_searches=sp.get("max_saved_searches", 50),
                    featured_listing_allowed=sp.get("featured_listing_allowed", False),
                    priority_support=sp.get("priority_support", False),
                    is_active=True,
                )
                db.add(existing_plan)
                await db.flush()
        print("Subscription plans seeded successfully.")

        # ── 9. Seed Inquiries & Visits ────────────────────────────────────────
        print("\n--- Seeding Inquiries & Visits ---")
        first_prop_res = await db.execute(select(Property).limit(1))
        sample_prop = first_prop_res.scalars().first()

        aditya_id = user_map.get("aditya.mehta@example.com", 1)

        if sample_prop:
            inq_res = await db.execute(select(Inquiry).where(Inquiry.user_id == aditya_id))
            if not inq_res.scalars().first():
                db.add(
                    Inquiry(
                        user_id=aditya_id,
                        property_id=sample_prop.id,
                        agent_id=default_agent_id,
                        name="Aditya Mehta",
                        email="aditya.mehta@example.com",
                        phone="+91 98101 23456",
                        message="Interested in scheduling a VIP walkthrough this Saturday.",
                        status="APPROVED",
                        is_admin_approved=True,
                    )
                )

            vis_res = await db.execute(select(Visit).where(Visit.user_id == aditya_id))
            if not vis_res.scalars().first():
                db.add(
                    Visit(
                        user_id=aditya_id,
                        property_id=sample_prop.id,
                        agent_id=default_agent_id,
                        requested_date=datetime.now(timezone.utc),
                        confirmed_date=datetime.now(timezone.utc),
                        status="CONFIRMED",
                        user_notes="VIP visit scheduled.",
                    )
                )

        await db.commit()
        print("\n=== Seeding completed successfully and committed! ===")


if __name__ == "__main__":
    asyncio.run(seed())
