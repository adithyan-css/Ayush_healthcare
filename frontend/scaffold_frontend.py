import os

FILES = {
    "pubspec.yaml": """name: prakriti_os
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
  flutter_local_notifications: ^16.2.0
""",
    "lib/main.dart": """import 'package:flutter/material.dart';
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
}
""",
    "lib/core/theme.dart": """import 'package:flutter/material.dart';
class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    primarySwatch: Colors.green,
    scaffoldBackgroundColor: Colors.white,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.green,
      foregroundColor: Colors.white,
    ),
  );
}""",
    "lib/data/models/user_model.dart": """class UserModel {
  final String uid;
  final String email;
  final String name;
  UserModel({required this.uid, required this.email, required this.name});
}""",
    "lib/data/models/prakriti_model.dart": """class PrakritiModel {
  final double vataScore;
  final double pittaScore;
  final double kaphaScore;
  final String dominantDosha;
  PrakritiModel({required this.vataScore, required this.pittaScore, required this.kaphaScore, required this.dominantDosha});  
}""",
    "lib/data/models/recommendation_model.dart": """class RecommendationModel {
  final List<String> herbs;
  final Map<String, List<String>> diet;
  final List<String> yoga;
  final List<String> dinacharya;
  final String prevention30;
  RecommendationModel({required this.herbs, required this.diet, required this.yoga, required this.dinacharya, required this.prevention30});
}""",
    "lib/data/models/district_risk_model.dart": """class DistrictRiskModel {
  final String districtId;
  final String stateId;
  final String riskLevel;
  final String dominantSymptom;
  DistrictRiskModel({required this.districtId, required this.stateId, required this.riskLevel, required this.dominantSymptom});
}""",
    "lib/data/models/forecast_model.dart": """class ForecastModel {}""",
    "lib/data/models/nadi_diagnosis.dart": """class NadiDiagnosis {}""",
    "lib/services/api_service.dart": """import 'package:dio/dio.dart';
class ApiService {
  final Dio dio = Dio(BaseOptions(baseUrl: "http://localhost:8000/"));
  Future<Response> get(String path) => dio.get(path);
  Future<Response> post(String path, dynamic data) => dio.post(path, data: data);
}""",
    "lib/services/hive_service.dart": """class HiveService {
  Future<void> init() async {}
}""",
    "lib/services/health_service.dart": """class HealthService {
  Future<void> init() async {}
}""",
    "lib/services/notification_service.dart": """class NotificationService {
  Future<void> init() async {}
}""",
    "lib/presentation/cubits/auth_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
class AuthCubit extends Cubit<bool> {
  AuthCubit() : super(false);
  void login() => emit(true);
  void logout() => emit(false);
}""",
    "lib/presentation/cubits/prakriti_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/prakriti_model.dart';
class PrakritiCubit extends Cubit<PrakritiModel?> {
  PrakritiCubit() : super(null);
  void evaluate(Map<String, int> answers) {
    emit(PrakritiModel(vataScore: 40, pittaScore: 30, kaphaScore: 30, dominantDosha: "Vata"));
  }
}""",
    "lib/presentation/cubits/recommendation_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
class RecommendationCubit extends Cubit<String?> {
  RecommendationCubit() : super(null);
}""",
    "lib/presentation/cubits/heatmap_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
class HeatmapCubit extends Cubit<String?> {
  HeatmapCubit() : super(null);
}""",
    "lib/presentation/cubits/forecast_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
class ForecastCubit extends Cubit<String?> {
  ForecastCubit() : super(null);
}""",
    "lib/presentation/cubits/wearable_cubit.dart": """import 'package:flutter_bloc/flutter_bloc.dart';
class WearableCubit extends Cubit<String?> {
  WearableCubit() : super(null);
}""",
    "lib/presentation/screens/splash_screen.dart": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class SplashScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    Future.delayed(Duration(seconds: 2), () {
      context.go('/login');
    });
    return Scaffold(body: Center(child: Text("PrakritiOS\\nLoading...")));
  }
}""",
    "lib/presentation/screens/login_screen.dart": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Login")), 
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Login"))));
  }
}""",
    "lib/presentation/screens/register_screen.dart": """import 'package:flutter/material.dart';
class RegisterScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Register")), body: Center(child: Text("Register")));
  }
}""",
    "lib/presentation/screens/prakriti_quiz_screen.dart": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiQuizScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Quiz")),
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/quiz-result'), child: Text("Submit 10 Questions"))));
  }
}""",
    "lib/presentation/screens/prakriti_result_screen.dart": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Result")),
      body: Center(child: Column(children: [Text("Pie Chart showing Doshas"), ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Go Home"))])));
  }
}""",
    "lib/presentation/screens/home_screen.dart": """import 'package:flutter/material.dart';
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
}""",
    "lib/presentation/screens/symptom_selection_screen.dart": """import 'package:flutter/material.dart';
class SymptomSelectionScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Symptoms")), body: Center(child: Text("Chips & Free Text")));
  }
}""",
    "lib/presentation/screens/recommendation_result_screen.dart": """import 'package:flutter/material.dart';
class RecommendationResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(length: 4, child: Scaffold(
      appBar: AppBar(title: Text("Recommendations"), bottom: TabBar(tabs: [Tab(text:"Herbs"), Tab(text:"Diet"), Tab(text:"Yoga"), Tab(text:"Dinacharya")])), 
      body: TabBarView(children: [Center(child: Text("Herbs List")), Center(child: Text("Diet List")), Center(child: Text("Yoga List")), Center(child: Text("Dinacharya List"))])
    ));
  }
}""",
    "lib/presentation/screens/heatmap_screen.dart": """import 'package:flutter/material.dart';
class HeatmapScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("India Heatmap")), body: Center(child: Text("Flutter Map Widget")));
  }
}""",
    "lib/presentation/screens/state_detail_screen.dart": """import 'package:flutter/material.dart';
class StateDetailScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("State Detail")), body: Center(child: Text("Trend chart and AYUSH Tips")));
  }
}""",
    "lib/presentation/screens/forecast_screen.dart": """import 'package:flutter/material.dart';
class ForecastScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("30-Day Forecast")), body: Center(child: Text("Forecast Charts")));
  }
}""",
    "lib/presentation/screens/nadi_monitor_screen.dart": """import 'package:flutter/material.dart';
class NadiMonitorScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Nadi Monitor (HRV)")), body: Center(child: Text("Radar Chart Anomaly Detection")));
  }
}""",
    "lib/presentation/screens/vaidya_copilot_screen.dart": """import 'package:flutter/material.dart';
class VaidyaCopilotScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Vaidya Copilot")), body: Center(child: Text("Doctor Dashboard & AI Suggestions")));
  }
}""",
    "lib/presentation/screens/settings_screen.dart": """import 'package:flutter/material.dart';
class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Settings")), body: Center(child: Text("Settings UI")));
  }
}""",
    "lib/widgets/dosha_gauge.dart": """import 'package:flutter/material.dart';
class DoshaGauge extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Dosha Gauge Widget"));
}""",
    "lib/widgets/data_banner.dart": """import 'package:flutter/material.dart';
class DataBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Data Banner Widget"));
}""",
    "lib/widgets/alert_banner.dart": """import 'package:flutter/material.dart';
class AlertBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Alert Banner Widget"));
}""",
    "lib/widgets/trend_chart.dart": """import 'package:flutter/material.dart';
class TrendChart extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Trend Chart Widget"));
}""",
    "lib/widgets/herb_card.dart": """import 'package:flutter/material.dart';
class HerbCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Herb Card Widget"));
}""",
    "lib/widgets/risk_card.dart": """import 'package:flutter/material.dart';
class RiskCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(child: Text("Risk Card Widget"));
}"""
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/flutter_app"
    for path, content in FILES.items():
        full_path = os.path.join(root, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content.strip() + "\\n")
    print("Frontend scaffolded.")

if __name__ == "__main__":
    main()
