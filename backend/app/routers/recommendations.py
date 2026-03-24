from fastapi import APIRouter
router = APIRouter()

@router.post("/generate")
async def generate_rec(): pass

@router.get("/history")
async def get_history(): pass

@router.get("/{id}")
async def get_rec(id: str): pass

@router.delete("/{id}")
async def delete_rec(id: str): pass

@router.post("/prevention")
async def prevention(): pass
