from fastapi import APIRouter
router = APIRouter()

@router.get("/national")
async def national(): pass

@router.get("/regions")
async def regions(): pass

@router.get("/population")
async def population(): pass

@router.get("/seasonal")
async def seasonal(): pass

@router.get("/explain/{district_id}")
async def explain(district_id: str): pass

@router.post("/bulletin")
async def bulletin(): pass

@router.post("/refresh")
async def refresh(): pass\n