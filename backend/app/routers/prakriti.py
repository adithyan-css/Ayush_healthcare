from fastapi import APIRouter
router = APIRouter()

@router.post("/profile")
async def create_profile(): pass

@router.get("/profile")
async def get_profile(): pass

@router.put("/profile")
async def update_profile(): pass

@router.post("/vision-analyse")
async def vision_analyse(): pass

@router.get("/tips")
async def get_tips(): pass
