import asyncio
import logging
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.modules.locations.models import Country, State, City, Locality, SubLocality

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def seed_locations():
    async with AsyncSessionLocal() as db:
        # Check if India country already exists
        result = await db.execute(select(Country).where(Country.name == "India"))
        country = result.scalar_one_or_none()

        if not country:
            country = Country(
                name="India",
                iso_code="IN",
                phone_code="+91",
            )
            db.add(country)
            await db.flush()
            logger.info(f"Created Country: {country.name} (ID: {country.id})")
        else:
            logger.info(f"Country exists: {country.name} (ID: {country.id})")

        # ── State: Haryana ────────────────────────────────────────────────
        res = await db.execute(
            select(State).where(State.name == "Haryana", State.country_id == country.id)
        )
        haryana = res.scalar_one_or_none()
        if not haryana:
            haryana = State(
                country_id=country.id,
                name="Haryana",
                state_code="HR",
            )
            db.add(haryana)
            await db.flush()
            logger.info(f"Created State: {haryana.name} (ID: {haryana.id})")

        # City: Gurugram
        res = await db.execute(
            select(City).where(City.name == "Gurugram", City.state_id == haryana.id)
        )
        gurugram = res.scalar_one_or_none()
        if not gurugram:
            gurugram = City(
                state_id=haryana.id,
                name="Gurugram",
                latitude=28.4595,
                longitude=77.0266,
            )
            db.add(gurugram)
            await db.flush()
            logger.info(f"Created City: {gurugram.name} (ID: {gurugram.id})")

        # Locality: Sector 57
        res = await db.execute(
            select(Locality).where(
                Locality.name == "Sector 57", Locality.city_id == gurugram.id
            )
        )
        sector_57 = res.scalar_one_or_none()
        if not sector_57:
            sector_57 = Locality(
                city_id=gurugram.id,
                name="Sector 57",
                pincode="122011",
                latitude=28.4211,
                longitude=77.0985,
            )
            db.add(sector_57)
            await db.flush()
            logger.info(f"Created Locality: {sector_57.name} (ID: {sector_57.id})")

        # SubLocality: Block A
        res = await db.execute(
            select(SubLocality).where(
                SubLocality.name == "Block A",
                SubLocality.locality_id == sector_57.id,
            )
        )
        sub_loc = res.scalar_one_or_none()
        if not sub_loc:
            sub_loc = SubLocality(
                locality_id=sector_57.id,
                name="Block A",
                pincode="122011",
                latitude=28.4211,
                longitude=77.0985,
            )
            db.add(sub_loc)
            await db.flush()
            logger.info(f"Created SubLocality: {sub_loc.name} (ID: {sub_loc.id})")

        # Locality: Golf Course Road
        res = await db.execute(
            select(Locality).where(
                Locality.name == "Golf Course Road", Locality.city_id == gurugram.id
            )
        )
        if not res.scalar_one_or_none():
            gcr = Locality(
                city_id=gurugram.id,
                name="Golf Course Road",
                pincode="122002",
                latitude=28.4682,
                longitude=77.0977,
            )
            db.add(gcr)
            await db.flush()

        # Locality: Sector 54
        res = await db.execute(
            select(Locality).where(
                Locality.name == "Sector 54", Locality.city_id == gurugram.id
            )
        )
        if not res.scalar_one_or_none():
            s54 = Locality(
                city_id=gurugram.id,
                name="Sector 54",
                pincode="122011",
                latitude=28.4410,
                longitude=77.1080,
            )
            db.add(s54)
            await db.flush()

        # ── State: Delhi ──────────────────────────────────────────────────
        res = await db.execute(
            select(State).where(State.name == "Delhi", State.country_id == country.id)
        )
        delhi_state = res.scalar_one_or_none()
        if not delhi_state:
            delhi_state = State(
                country_id=country.id,
                name="Delhi",
                state_code="DL",
            )
            db.add(delhi_state)
            await db.flush()

        res = await db.execute(
            select(City).where(City.name == "New Delhi", City.state_id == delhi_state.id)
        )
        new_delhi = res.scalar_one_or_none()
        if not new_delhi:
            new_delhi = City(
                state_id=delhi_state.id,
                name="New Delhi",
                latitude=28.6139,
                longitude=77.2090,
            )
            db.add(new_delhi)
            await db.flush()

            db.add(
                Locality(
                    city_id=new_delhi.id,
                    name="Connaught Place",
                    pincode="110001",
                    latitude=28.6315,
                    longitude=77.2167,
                )
            )
            db.add(
                Locality(
                    city_id=new_delhi.id,
                    name="Saket",
                    pincode="110017",
                    latitude=28.5245,
                    longitude=77.2066,
                )
            )
            await db.flush()

        # ── State: Uttar Pradesh ──────────────────────────────────────────
        res = await db.execute(
            select(State).where(
                State.name == "Uttar Pradesh", State.country_id == country.id
            )
        )
        up_state = res.scalar_one_or_none()
        if not up_state:
            up_state = State(
                country_id=country.id,
                name="Uttar Pradesh",
                state_code="UP",
            )
            db.add(up_state)
            await db.flush()

        res = await db.execute(
            select(City).where(City.name == "Noida", City.state_id == up_state.id)
        )
        noida = res.scalar_one_or_none()
        if not noida:
            noida = City(
                state_id=up_state.id,
                name="Noida",
                latitude=28.5355,
                longitude=77.3910,
            )
            db.add(noida)
            await db.flush()

            db.add(
                Locality(
                    city_id=noida.id,
                    name="Sector 62",
                    pincode="201309",
                    latitude=28.6270,
                    longitude=77.3685,
                )
            )
            db.add(
                Locality(
                    city_id=noida.id,
                    name="Sector 150",
                    pincode="201310",
                    latitude=28.4357,
                    longitude=77.4984,
                )
            )
            await db.flush()

        # ── State: Karnataka ──────────────────────────────────────────────
        res = await db.execute(
            select(State).where(
                State.name == "Karnataka", State.country_id == country.id
            )
        )
        karnataka = res.scalar_one_or_none()
        if not karnataka:
            karnataka = State(
                country_id=country.id,
                name="Karnataka",
                state_code="KA",
            )
            db.add(karnataka)
            await db.flush()

        res = await db.execute(
            select(City).where(City.name == "Bengaluru", City.state_id == karnataka.id)
        )
        bengaluru = res.scalar_one_or_none()
        if not bengaluru:
            bengaluru = City(
                state_id=karnataka.id,
                name="Bengaluru",
                latitude=12.9716,
                longitude=77.5946,
            )
            db.add(bengaluru)
            await db.flush()

            db.add(
                Locality(
                    city_id=bengaluru.id,
                    name="Indiranagar",
                    pincode="560038",
                    latitude=12.9784,
                    longitude=77.6408,
                )
            )
            db.add(
                Locality(
                    city_id=bengaluru.id,
                    name="Whitefield",
                    pincode="560066",
                    latitude=12.9698,
                    longitude=77.7500,
                )
            )
            await db.flush()

        # ── State: Maharashtra ────────────────────────────────────────────
        res = await db.execute(
            select(State).where(
                State.name == "Maharashtra", State.country_id == country.id
            )
        )
        maharashtra = res.scalar_one_or_none()
        if not maharashtra:
            maharashtra = State(
                country_id=country.id,
                name="Maharashtra",
                state_code="MH",
            )
            db.add(maharashtra)
            await db.flush()

        res = await db.execute(
            select(City).where(City.name == "Mumbai", City.state_id == maharashtra.id)
        )
        mumbai = res.scalar_one_or_none()
        if not mumbai:
            mumbai = City(
                state_id=maharashtra.id,
                name="Mumbai",
                latitude=19.0760,
                longitude=72.8777,
            )
            db.add(mumbai)
            await db.flush()

            db.add(
                Locality(
                    city_id=mumbai.id,
                    name="Bandra West",
                    pincode="400050",
                    latitude=19.0596,
                    longitude=72.8295,
                )
            )
            db.add(
                Locality(
                    city_id=mumbai.id,
                    name="Andheri West",
                    pincode="400058",
                    latitude=19.1363,
                    longitude=72.8277,
                )
            )
            await db.flush()

        await db.commit()
        logger.info("Successfully seeded locations!")


if __name__ == "__main__":
    asyncio.run(seed_locations())
