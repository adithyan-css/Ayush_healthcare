from fastapi import APIRouter
router = APIRouter()

@router.post("/hrv-sync")
async def hrv_sync(): pass

@router.get("/nadi")
async def nadi(): pass

@router.get("/trend")
async def trend(): pass

@router.get("/anomalies")
async def anomalies(): pass\n