from fastapi import APIRouter
router = APIRouter()

@router.get("/districts")
async def get_districts(): pass

@router.get("/state/{state_id}")
async def get_state(state_id: str): pass

@router.get("/trend/{state_id}")
async def get_trend(state_id: str): pass

@router.get("/rising")
async def get_rising(): pass

@router.post("/refresh")
async def refresh(): pass\n