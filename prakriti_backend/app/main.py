import logging
from sqlalchemy import text
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.config import settings
from app.dependencies import error_response
from app.database import AsyncSessionLocal, init_db
from app.routers import auth, prakriti, recommendations, heatmap, symptoms, forecast, wearable, vaidya

app = FastAPI(title='PrakritiOS API', version='1.0.0')
logger = logging.getLogger('prakriti_backend')
logging.basicConfig(level=logging.INFO)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins_list,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)


@app.on_event('startup')
async def on_startup():
	if not settings.SECRET_KEY:
		logger.error('Missing SECRET_KEY environment variable')
		raise RuntimeError('Missing SECRET_KEY environment variable')
	await init_db()
	logger.info('PrakritiOS backend startup complete')


@app.middleware('http')
async def request_logging_middleware(request: Request, call_next):
	response = await call_next(request)
	logger.info('%s %s -> %s', request.method, request.url.path, response.status_code)
	return response


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
	return {'success': True, 'data': {'status': 'running', 'api': 'PrakritiOS Backend v1'}, 'message': 'Service running'}


@app.get('/health')
async def health():
	db_ok = False
	try:
		async with AsyncSessionLocal() as session:
			await session.execute(text('SELECT 1'))
		db_ok = True
	except Exception:
		db_ok = False

	status = 'ok' if db_ok else 'degraded'
	return {
		'success': True,
		'data': {
			'status': status,
			'environment': settings.ENVIRONMENT,
			'database': 'connected' if db_ok else 'unavailable',
		},
		'message': 'Health status loaded',
	}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
	logger.exception('Unhandled error at %s', request.url.path)
	return JSONResponse(status_code=500, content=error_response('Internal server error'))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
	if isinstance(exc.detail, dict) and {'success', 'data', 'message'}.issubset(exc.detail.keys()):
		return JSONResponse(status_code=exc.status_code, content=exc.detail)
	message = str(exc.detail) if exc.detail else 'Request failed'
	return JSONResponse(status_code=exc.status_code, content=error_response(message))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(status_code=422, content=error_response('Validation failed', {'errors': exc.errors()}))
