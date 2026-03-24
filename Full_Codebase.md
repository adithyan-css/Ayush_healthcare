FILE: backend\requirements.txt\n<code>\nfastapi
uvicorn
sqlalchemy[asyncio]
asyncpg
pydantic
pydantic-settings
firebase-admin
anthropic
python-jose
passlib
python-multipart
fpdf2
httpx
alembic
scikit-learn
statsmodels
\n</code>\n\nFILE: backend\app\database.py\n<code>\nfrom sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./test.db" # Mocking PG for quick setup but structured for Async PG "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
\n</code>\n\nFILE: backend\app\main.py\n<code>\nfrom fastapi import FastAPI, Depends
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
\n</code>\n\nFILE: backend\app\__init__.py\n<code>\n\n\n</code>\n\nFILE: backend\app\models\user.py\n<code>\nfrom sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)

class PrakritiProfile(Base):
    __tablename__ = "prakriti_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    vata_score = Column(Float)
    pitta_score = Column(Float)
    kapha_score = Column(Float)
    dominant_dosha = Column(String)

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    session_data = Column(String)
    created_at = Column(String)

class DistrictRisk(Base):
    __tablename__ = "district_risks"
    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(String)
    district_id = Column(String)
    risk_level = Column(String)
    dominant_symptom = Column(String)

class HrvReading(Base):
    __tablename__ = "hrv_readings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    hrv_value = Column(Float)
    timestamp = Column(String)\n\n</code>\n\nFILE: backend\app\models\__init__.py\n<code>\n\n\n</code>\n\nFILE: backend\app\routers\auth.py\n<code>\nfrom fastapi import APIRouter
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
async def update_me(): pass\n\n</code>\n\nFILE: backend\app\routers\forecast.py\n<code>\nfrom fastapi import APIRouter
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
async def refresh(): pass\n\n</code>\n\nFILE: backend\app\routers\heatmap.py\n<code>\nfrom fastapi import APIRouter
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
async def refresh(): pass\n\n</code>\n\nFILE: backend\app\routers\prakriti.py\n<code>\nfrom fastapi import APIRouter
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
async def get_tips(): pass\n\n</code>\n\nFILE: backend\app\routers\recommendations.py\n<code>\nfrom fastapi import APIRouter
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
async def prevention(): pass\n\n</code>\n\nFILE: backend\app\routers\symptoms.py\n<code>\nfrom fastapi import APIRouter
router = APIRouter()

@router.post("/report")
async def report(): pass

@router.get("/community")
async def community(): pass

@router.get("/clusters")
async def clusters(): pass\n\n</code>\n\nFILE: backend\app\routers\vaidya.py\n<code>\nfrom fastapi import APIRouter
router = APIRouter()

@router.get("/patients")
async def patients(): pass

@router.get("/patients/{uid}")
async def patient(uid: str): pass

@router.post("/suggest")
async def suggest(): pass

@router.post("/interactions")
async def interactions(): pass

@router.post("/consult")
async def consult(): pass

@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str): pass\n\n</code>\n\nFILE: backend\app\routers\wearable.py\n<code>\nfrom fastapi import APIRouter
router = APIRouter()

@router.post("/hrv-sync")
async def hrv_sync(): pass

@router.get("/nadi")
async def nadi(): pass

@router.get("/trend")
async def trend(): pass

@router.get("/anomalies")
async def anomalies(): pass\n\n</code>\n\nFILE: backend\app\routers\__init__.py\n<code>\n\n\n</code>\n\nFILE: backend\app\schemas\schemas.py\n<code>\nfrom pydantic import BaseModel
from typing import List, Optional, Dict

class UserSchema(BaseModel):
    uid: str
    email: str
    name: str

class PrakritiProfileSchema(BaseModel):
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str

class RecommendationOutput(BaseModel):
    herbs: List[str]
    diet: Dict[str, List[str]]
    yoga: List[str]
    dinacharya: List[str]
    prevention30: str\n\n</code>\n\nFILE: backend\app\schemas\__init__.py\n<code>\n\n\n</code>\n\nFILE: backend\app\services\claude.py\n<code>\nimport json
class ClaudeService:
    def get_recommendation(self, history, dosha, season, symptoms):
        return {
            "herbs": ["Ashwagandha", "Tulsi"],
            "diet": {"eat": ["Warm foods"], "avoid": ["Cold drinks"]},
            "yoga": ["Surya Namaskar"],
            "dinacharya": ["Early to bed"],
            "prevention30": "Risk of Vata imbalance"
        }\n\n</code>\n\nFILE: backend\app\services\ml.py\n<code>\nclass MLService:
    def predict_prophet(self): pass
    def lstm_output(self): pass\n\n</code>\n\nFILE: backend\app\services\nlp.py\n<code>\nclass NLPService:
    def detect_social_signals(self): pass\n\n</code>\n\nFILE: backend\app\services\pdf.py\n<code>\nclass PDFService:
    def generate_pdf(self, data): pass\n\n</code>\n\nFILE: backend\app\services\prakriti_logic.py\n<code>\nclass PrakritiLogic:
    def calculate_scores(self, answers): pass\n\n</code>\n\nFILE: backend\app\services\weather.py\n<code>\nclass WeatherService:
    def get_weather(self): pass\n\n</code>\n\nFILE: backend\app\services\__init__.py\n<code>\n\n\n</code>\n\nFILE: backend\app\utils\auth_utils.py\n<code>\ndef verify_token(token): pass\n\n</code>\n\nFILE: backend\app\utils\xai.py\n<code>\ndef generate_xai_reasoning(data): pass\n\n</code>\n\nFILE: backend\app\utils\__init__.py\n<code>\n\n\n</code>\n\nFILE: flutter_app\pubspec.yaml\n<code>\nname: prakriti_os
description: PrakritiOS App
publish_to: 'none'
version: 1.0.0+1
environment:
  sdk: '>=3.0.0 <4.0.0'
dependencies:
  flutter:
    sdk: flutter
  flutter_bloc: ^8.1.3
  go_router: ^12.1.1
  dio: ^5.3.3
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  firebase_auth: ^4.10.1
  firebase_core: ^2.16.0
  fl_chart: ^0.65.0
  flutter_map: ^6.1.0
  google_ml_kit: ^0.16.2
  health: ^7.2.1
  pdf: ^3.10.4
  flutter_local_notifications: ^16.2.0\n\n</code>\n\nFILE: flutter_app\lib\main.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'core/theme.dart';
import 'presentation/screens/splash_screen.dart';
import 'presentation/screens/login_screen.dart';
import 'presentation/screens/register_screen.dart';
import 'presentation/screens/prakriti_quiz_screen.dart';
import 'presentation/screens/prakriti_result_screen.dart';
import 'presentation/screens/home_screen.dart';
import 'presentation/screens/symptom_selection_screen.dart';
import 'presentation/screens/recommendation_result_screen.dart';
import 'presentation/screens/heatmap_screen.dart';
import 'presentation/screens/state_detail_screen.dart';
import 'presentation/screens/forecast_screen.dart';
import 'presentation/screens/nadi_monitor_screen.dart';
import 'presentation/screens/vaidya_copilot_screen.dart';
import 'presentation/screens/settings_screen.dart';
import 'presentation/cubits/auth_cubit.dart';
import 'presentation/cubits/prakriti_cubit.dart';
import 'presentation/cubits/recommendation_cubit.dart';
import 'presentation/cubits/heatmap_cubit.dart';
import 'presentation/cubits/forecast_cubit.dart';
import 'presentation/cubits/wearable_cubit.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PrakritiOSApp());
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (context, state) => SplashScreen()),
    GoRoute(path: '/login', builder: (context, state) => LoginScreen()),
    GoRoute(path: '/register', builder: (context, state) => RegisterScreen()),
    GoRoute(path: '/quiz', builder: (context, state) => PrakritiQuizScreen()),
    GoRoute(path: '/quiz-result', builder: (context, state) => PrakritiResultScreen()),
    GoRoute(path: '/home', builder: (context, state) => HomeScreen()),
    GoRoute(path: '/symptoms', builder: (context, state) => SymptomSelectionScreen()),
    GoRoute(path: '/recommendations', builder: (context, state) => RecommendationResultScreen()),
    GoRoute(path: '/heatmap', builder: (context, state) => HeatmapScreen()),
    GoRoute(path: '/state-detail', builder: (context, state) => StateDetailScreen()),
    GoRoute(path: '/forecast', builder: (context, state) => ForecastScreen()),
    GoRoute(path: '/nadi', builder: (context, state) => NadiMonitorScreen()),
    GoRoute(path: '/vaidya', builder: (context, state) => VaidyaCopilotScreen()),
    GoRoute(path: '/settings', builder: (context, state) => SettingsScreen()),
  ],
);

class PrakritiOSApp extends StatelessWidget {
  const PrakritiOSApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => AuthCubit()),
        BlocProvider(create: (_) => PrakritiCubit()),
        BlocProvider(create: (_) => RecommendationCubit()),
        BlocProvider(create: (_) => HeatmapCubit()),
        BlocProvider(create: (_) => ForecastCubit()),
        BlocProvider(create: (_) => WearableCubit()),
      ],
      child: MaterialApp.router(
        routerConfig: _router,
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}\n\n</code>\n\nFILE: flutter_app\lib\core\theme.dart\n<code>\nimport 'package:flutter/material.dart';
class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    primarySwatch: Colors.green,
    scaffoldBackgroundColor: Colors.white,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.green,
      foregroundColor: Colors.white,
    ),
  );
}\n\n</code>\n\nFILE: flutter_app\lib\data\models\district_risk_model.dart\n<code>\nclass DistrictRiskModel {
  final String districtId;
  final String stateId;
  final String riskLevel;
  final String dominantSymptom;
  DistrictRiskModel({required this.districtId, required this.stateId, required this.riskLevel, required this.dominantSymptom});
}\n\n</code>\n\nFILE: flutter_app\lib\data\models\forecast_model.dart\n<code>\nclass ForecastModel {}\n\n</code>\n\nFILE: flutter_app\lib\data\models\nadi_diagnosis.dart\n<code>\nclass NadiDiagnosis {}\n\n</code>\n\nFILE: flutter_app\lib\data\models\prakriti_model.dart\n<code>\nclass PrakritiModel {
  final double vataScore;
  final double pittaScore;
  final double kaphaScore;
  final String dominantDosha;
  PrakritiModel({required this.vataScore, required this.pittaScore, required this.kaphaScore, required this.dominantDosha});  
}\n\n</code>\n\nFILE: flutter_app\lib\data\models\recommendation_model.dart\n<code>\nclass RecommendationModel {
  final List<String> herbs;
  final Map<String, List<String>> diet;
  final List<String> yoga;
  final List<String> dinacharya;
  final String prevention30;
  RecommendationModel({required this.herbs, required this.diet, required this.yoga, required this.dinacharya, required this.prevention30});
}\n\n</code>\n\nFILE: flutter_app\lib\data\models\user_model.dart\n<code>\nclass UserModel {
  final String uid;
  final String email;
  final String name;
  UserModel({required this.uid, required this.email, required this.name});
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\auth_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
class AuthCubit extends Cubit<bool> {
  AuthCubit() : super(false);
  void login() => emit(true);
  void logout() => emit(false);
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\forecast_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
class ForecastCubit extends Cubit<String?> {
  ForecastCubit() : super(null);
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\heatmap_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
class HeatmapCubit extends Cubit<String?> {
  HeatmapCubit() : super(null);
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\prakriti_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/prakriti_model.dart';
class PrakritiCubit extends Cubit<PrakritiModel?> {
  PrakritiCubit() : super(null);
  void evaluate(Map<String, int> answers) {
    emit(PrakritiModel(vataScore: 40, pittaScore: 30, kaphaScore: 30, dominantDosha: "Vata"));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\recommendation_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
class RecommendationCubit extends Cubit<String?> {
  RecommendationCubit() : super(null);
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\cubits\wearable_cubit.dart\n<code>\nimport 'package:flutter_bloc/flutter_bloc.dart';
class WearableCubit extends Cubit<String?> {
  WearableCubit() : super(null);
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\forecast_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class ForecastScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("30-Day Forecast")), body: Center(child: Text("Forecast Charts")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\heatmap_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class HeatmapScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("India Heatmap")), body: Center(child: Text("Flutter Map Widget")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\home_screen.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("PrakritiOS Home")), 
      body: ListView(
        children: [
          ListTile(title: Text("Symptom Report"), onTap: ()=>context.go('/symptoms')),
          ListTile(title: Text("Recommendations"), onTap: ()=>context.go('/recommendations')),
          ListTile(title: Text("Heatmap"), onTap: ()=>context.go('/heatmap')),
          ListTile(title: Text("Forecast"), onTap: ()=>context.go('/forecast')),
          ListTile(title: Text("Nadi Monitor"), onTap: ()=>context.go('/nadi')),
          ListTile(title: Text("Vaidya Copilot"), onTap: ()=>context.go('/vaidya')),
        ]
      )
    );
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\login_screen.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Login")), 
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Login"))));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\nadi_monitor_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class NadiMonitorScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Nadi Monitor (HRV)")), body: Center(child: Text("Radar Chart Anomaly Detection")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\prakriti_quiz_screen.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiQuizScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Quiz")),
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/quiz-result'), child: Text("Submit 10 Questions"))));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\prakriti_result_screen.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Result")),
      body: Center(child: Column(children: [Text("Pie Chart showing Doshas"), ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Go Home"))])));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\recommendation_result_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class RecommendationResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(length: 4, child: Scaffold(
      appBar: AppBar(title: Text("Recommendations"), bottom: TabBar(tabs: [Tab(text:"Herbs"), Tab(text:"Diet"), Tab(text:"Yoga"), Tab(text:"Dinacharya")])), 
      body: TabBarView(children: [Center(child: Text("Herbs List")), Center(child: Text("Diet List")), Center(child: Text("Yoga List")), Center(child: Text("Dinacharya List"))])
    ));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\register_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class RegisterScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Register")), body: Center(child: Text("Register")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\settings_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Settings")), body: Center(child: Text("Settings UI")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\splash_screen.dart\n<code>\nimport 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class SplashScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    Future.delayed(Duration(seconds: 2), () {
      context.go('/login');
    });
    return Scaffold(body: Center(child: Text("PrakritiOS\nLoading...")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\state_detail_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class StateDetailScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("State Detail")), body: Center(child: Text("Trend chart and AYUSH Tips")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\symptom_selection_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class SymptomSelectionScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Symptoms")), body: Center(child: Text("Chips & Free Text")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\presentation\screens\vaidya_copilot_screen.dart\n<code>\nimport 'package:flutter/material.dart';
class VaidyaCopilotScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Vaidya Copilot")), body: Center(child: Text("Doctor Dashboard & AI Suggestions")));
  }
}\n\n</code>\n\nFILE: flutter_app\lib\services\api_service.dart\n<code>\nimport 'package:dio/dio.dart';
class ApiService {
  final Dio dio = Dio(BaseOptions(baseUrl: "http://localhost:8000/"));
  Future<Response> get(String path) => dio.get(path);
  Future<Response> post(String path, dynamic data) => dio.post(path, data: data);
}\n\n</code>\n\nFILE: flutter_app\lib\services\health_service.dart\n<code>\nclass HealthService {
  Future<void> init() async {}
}\n\n</code>\n\nFILE: flutter_app\lib\services\hive_service.dart\n<code>\nclass HiveService {
  Future<void> init() async {}
}\n\n</code>\n\nFILE: flutter_app\lib\services\notification_service.dart\n<code>\nclass NotificationService {
  Future<void> init() async {}
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\alert_banner.dart\n<code>\nimport 'package:flutter/material.dart';
class AlertBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Alert Banner Widget"));
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\data_banner.dart\n<code>\nimport 'package:flutter/material.dart';
class DataBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Data Banner Widget"));
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\dosha_gauge.dart\n<code>\nimport 'package:flutter/material.dart';
class DoshaGauge extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Dosha Gauge Widget"));
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\herb_card.dart\n<code>\nimport 'package:flutter/material.dart';
class HerbCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Herb Card Widget"));
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\risk_card.dart\n<code>\nimport 'package:flutter/material.dart';
class RiskCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Risk Card Widget"));
}\n\n</code>\n\nFILE: flutter_app\lib\widgets\trend_chart.dart\n<code>\nimport 'package:flutter/material.dart';
class TrendChart extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Trend Chart Widget"));
}\n\n</code>\n\n