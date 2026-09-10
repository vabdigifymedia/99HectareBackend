from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reviews.models import Review
from app.modules.reviews.schemas import ReviewCreate, ReviewUpdate


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, data: ReviewCreate) -> Review:
        review = Review(
            user_id=user_id,
            agent_id=data.agent_id,
            builder_id=data.builder_id,
            rating=data.rating,
            comment=data.comment,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.db.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.user_id == user_id).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_agent(self, agent_id: int) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.agent_id == agent_id).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_builder(self, builder_id: int) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.builder_id == builder_id).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_all(self) -> list[Review]:
        result = await self.db.execute(
            select(Review).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, review: Review, data: ReviewUpdate) -> Review:
        if data.rating is not None:
            review.rating = data.rating
        if data.comment is not None:
            review.comment = data.comment
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review: Review) -> None:
        await self.db.delete(review)
        await self.db.commit()

    async def update_moderation(self, review: Review, is_verified: bool | None, is_published: bool | None) -> Review:
        if is_verified is not None:
            review.is_verified = is_verified
        if is_published is not None:
            review.is_published = is_published
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_pending_verification(self) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.is_verified == False).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_published(self) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.is_published == True).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_unpublished(self) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(Review.is_published == False).order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_agent_and_user(self, agent_id: int, user_id: int) -> Review | None:
        result = await self.db.execute(
            select(Review).where(Review.agent_id == agent_id, Review.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_builder_and_user(self, builder_id: int, user_id: int) -> Review | None:
        result = await self.db.execute(
            select(Review).where(Review.builder_id == builder_id, Review.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_average_rating_by_agent(self, agent_id: int) -> float:
        result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.agent_id == agent_id, Review.is_verified == True)
        )
        return result.scalar_one_or_none() or 0.0

    async def get_average_rating_by_builder(self, builder_id: int) -> float:
        result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.builder_id == builder_id, Review.is_verified == True)
        )
        return result.scalar_one_or_none() or 0.0

    async def get_total_count(self) -> int:
        result = await self.db.execute(
            select(func.count(Review.id)).where(Review.is_verified == True, Review.is_published == True)
        )
        return result.scalar_one()
