from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, prakriti, recommendations, heatmap, symptoms, forecast, wearable, vaidya

app = FastAPI(title="PrakritiOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(prakriti.router, prefix="/prakriti", tags=["prakriti"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(heatmap.router, prefix="/heatmap", tags=["heatmap"])
app.include_router(symptoms.router, prefix="/symptoms", tags=["symptoms"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
app.include_router(wearable.router, prefix="/wearable", tags=["wearable"])
app.include_router(vaidya.router, prefix="/vaidya", tags=["vaidya"])

@app.get("/")
def health_check():
    return {"status": "ok", "system": "PrakritiOS"}
