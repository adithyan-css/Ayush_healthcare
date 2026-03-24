from fastapi import APIRouter
router = APIRouter()

@router.post("/firebase-verify")
async def verify_firebase(token: str): pass

@router.post("/refresh")
async def refresh_token(): pass

@router.post("/logout")
async def logout(): pass

@router.get("/me")
async def get_me(): pass

@router.put("/me")
async def update_me(): pass
