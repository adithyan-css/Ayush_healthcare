from datetime import datetime
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
	async with AsyncSessionLocal() as session:
		yield session


async def get_redis():
	try:
		client = redis.from_url(settings.REDIS_URL, decode_responses=True)
		await client.ping()
		return client
	except Exception:
		return None


async def _seed_default_districts() -> None:
	from app.models.district import DistrictRisk

	seed_rows = [
		('MH', 'Maharashtra', 71, 'high', 'Fever/Viral', 'rising', [120, 134, 142, 160, 181, 205], 19.0760, 72.8777),
		('DL', 'Delhi', 82, 'critical', 'Respiratory', 'rising', [140, 152, 169, 183, 196, 222], 28.6139, 77.2090),
		('TN', 'Tamil Nadu', 49, 'medium', 'Digestive', 'stable', [88, 92, 95, 97, 98, 102], 13.0827, 80.2707),
		('KA', 'Karnataka', 56, 'high', 'Respiratory', 'stable', [96, 102, 109, 115, 119, 125], 12.9716, 77.5946),
		('KL', 'Kerala', 58, 'high', 'Fever/Viral', 'rising', [90, 101, 114, 128, 141, 149], 8.5241, 76.9366),
		('RJ', 'Rajasthan', 42, 'medium', 'Joint', 'stable', [72, 74, 75, 78, 81, 83], 26.9124, 75.7873),
		('UP', 'Uttar Pradesh', 63, 'high', 'Fever/Viral', 'rising', [122, 130, 141, 155, 170, 188], 26.8467, 80.9462),
		('WB', 'West Bengal', 46, 'medium', 'Skin', 'stable', [86, 88, 92, 94, 96, 99], 22.5726, 88.3639),
		('GJ', 'Gujarat', 39, 'medium', 'Joint', 'falling', [98, 95, 91, 88, 84, 81], 23.0225, 72.5714),
		('PB', 'Punjab', 52, 'high', 'Respiratory', 'rising', [89, 93, 98, 104, 112, 121], 30.9010, 75.8573),
	]
	seasons_map = {
		'winter': 'Respiratory',
		'summer': 'Digestive',
		'monsoon': 'Fever/Viral',
		'autumn': 'Joint',
	}

	async with AsyncSessionLocal() as session:
		count = await session.scalar(select(func.count()).select_from(DistrictRisk))
		if (count or 0) > 0:
			return
		for code, name, score, level, top, trend, monthly_cases, lat, lng in seed_rows:
			session.add(
				DistrictRisk(
					state_code=code,
					state_name=name,
					risk_score=score,
					risk_level=level,
					top_condition=top,
					trend=trend,
					monthly_cases=monthly_cases,
					seasons_map=seasons_map,
					latitude=lat,
					longitude=lng,
					updated_at=datetime.utcnow(),
				)
			)
		await session.commit()


async def init_db():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
		try:
			await conn.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR'))
		except Exception:
			pass
	await _seed_default_districts()
