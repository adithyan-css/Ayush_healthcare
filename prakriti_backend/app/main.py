from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, prakriti, recommendations, heatmap, symptoms, forecast, wearable, vaidya
from app.database import init_db

app = FastAPI(title='PrakritiOS API', version='1.0.0')

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)


@app.on_event('startup')
async def on_startup():
	await init_db()


app.include_router(auth.router, prefix='/api/v1/auth', tags=['Auth'])
app.include_router(prakriti.router, prefix='/api/v1/prakriti', tags=['Prakriti'])
app.include_router(recommendations.router, prefix='/api/v1/recommendations', tags=['Recommendations'])
app.include_router(heatmap.router, prefix='/api/v1/heatmap', tags=['Heatmap'])
app.include_router(symptoms.router, prefix='/api/v1/symptoms', tags=['Symptoms'])
app.include_router(forecast.router, prefix='/api/v1/forecast', tags=['Forecast'])
app.include_router(wearable.router, prefix='/api/v1/wearable', tags=['Wearable'])
app.include_router(vaidya.router, prefix='/api/v1/vaidya', tags=['Vaidya Copilot'])


@app.get('/')
async def root():
	return {'status': 'running', 'api': 'PrakritiOS Backend v1'}
