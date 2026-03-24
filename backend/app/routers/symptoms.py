from fastapi import APIRouter
router = APIRouter()

@router.post("/report")
async def report(): pass

@router.get("/community")
async def community(): pass

@router.get("/clusters")
async def clusters(): pass\n