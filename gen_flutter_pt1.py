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
  health: ^13.0.1
  pdf: ^3.10.4
  flutter_local_notifications: ^16.2.0
  equatable: ^2.0.5
  hydrated_bloc: ^9.1.2
  flutter_secure_storage: ^9.0.0
  lottie: ^2.7.0
  shimmer: ^3.0.0
  intl: ^0.18.1
  printing: ^5.12.0
  share_plus: ^7.2.1
  latlong2: ^0.9.0
  permission_handler: ^11.1.0
  connectivity_plus: ^5.0.2
  cached_network_image: ^3.3.0
  google_sign_in: ^6.1.6
""",
    "assets/data/prakriti_questions.json": """[
  {"id":1,"question":"My body frame is...","options":[{"text":"Thin, find it hard to gain weight","dosha":"vata"},{"text":"Medium, gain/lose weight easily","dosha":"pitta"},{"text":"Broad, sturdy, gain weight easily","dosha":"kapha"}]},
  {"id":2,"question":"My skin type currently is...","options":[{"text":"Dry, rough, or tending to crack","dosha":"vata"},{"text":"Warm, oily, prone to acne or redness","dosha":"pitta"},{"text":"Thick, moist, smooth or shiny","dosha":"kapha"}]},
  {"id":3,"question":"Regarding my appetite...","options":[{"text":"Variable, irregular, sometimes skip meals","dosha":"vata"},{"text":"Strong, sharp, get irritable if hungry","dosha":"pitta"},{"text":"Steady, slow, can easily skip a meal","dosha":"kapha"}]},
  {"id":4,"question":"My preferred weather is...","options":[{"text":"Warm and moist","dosha":"vata"},{"text":"Cool and dry","dosha":"pitta"},{"text":"Warm and dry","dosha":"kapha"}]},
  {"id":5,"question":"My energy patterns are...","options":[{"text":"Bursts of high energy followed by fatigue","dosha":"vata"},{"text":"Steady, moderate to high energy","dosha":"pitta"},{"text":"Slow to start, but enduring stamina","dosha":"kapha"}]},
  {"id":6,"question":"My typical stress response is...","options":[{"text":"Anxiety, worry, racing thoughts","dosha":"vata"},{"text":"Frustration, anger, irritability","dosha":"pitta"},{"text":"Withdrawal, stubbornness, slow to react","dosha":"kapha"}]},
  {"id":7,"question":"How is your sleep...","options":[{"text":"Light, easily interrupted, insomnia-prone","dosha":"vata"},{"text":"Moderate, but fall back asleep easily","dosha":"pitta"},{"text":"Deep, heavy, hard to wake up early","dosha":"kapha"}]},
  {"id":8,"question":"Your digestion typically involves...","options":[{"text":"Gas, bloating, occasional constipation","dosha":"vata"},{"text":"Acidity, heartburn, loose stools","dosha":"pitta"},{"text":"Sluggishness, heaviness after eating","dosha":"kapha"}]},
  {"id":9,"question":"Your memory works best by...","options":[{"text":"Grasping quickly but forgetting quickly","dosha":"vata"},{"text":"Sharp, good at logical recall","dosha":"pitta"},{"text":"Slow to learn, but retains forever","dosha":"kapha"}]},
  {"id":10,"question":"Your typical speech pattern is...","options":[{"text":"Fast, talkative, tending to jump topics","dosha":"vata"},{"text":"Clear, precise, organized, occasionally sharp","dosha":"pitta"},{"text":"Slow, rhythmic, sweet, thoughtful","dosha":"kapha"}]}
]""",
    "lib/main.dart": """import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:hydrated_bloc/hydrated_bloc.dart';
import 'package:path_provider/path_provider.dart';
import 'presentation/cubits/auth_cubit.dart';
import 'presentation/cubits/prakriti_cubit.dart';
import 'presentation/cubits/recommendation_cubit.dart';
import 'presentation/cubits/heatmap_cubit.dart';
import 'presentation/cubits/forecast_cubit.dart';
import 'presentation/cubits/wearable_cubit.dart';
import 'presentation/screens/splash_screen.dart';
import 'presentation/screens/login_screen.dart';
import 'presentation/screens/prakriti_quiz_screen.dart';
import 'presentation/screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // await Firebase.initializeApp(); // add google services config
  await Hive.initFlutter();
  await Hive.openBox('prakriti');
  await Hive.openBox('sessions');
  await Hive.openBox('settings');
  await Hive.openBox('districtRisk');
  await Hive.openBox('forecast');
  
  HydratedBloc.storage = await HydratedStorage.build(
    storageDirectory: await getApplicationDocumentsDirectory(),
  );

  runApp(const PrakritiOSApp());
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (_, __) => SplashScreen()),
    GoRoute(path: '/login', builder: (_, __) => LoginScreen()),
    GoRoute(path: '/quiz', builder: (_, __) => PrakritiQuizScreen()),
    GoRoute(path: '/home', builder: (_, __) => HomeScreen()),
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
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
""",
    "lib/services/api_service.dart": """import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  final Dio dio = Dio(BaseOptions(baseUrl: 'http://10.0.2.2:8000/api/v1'));
  final _storage = const FlutterSecureStorage();

  ApiService() {
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'jwt'); 
        if (token != null) options.headers['Authorization'] = 'Bearer $token';
        return handler.next(options);
      },
      onError: (e, handler) async {
        if (e.response?.statusCode == 401) {
          await _storage.delete(key: 'jwt');
        }
        return handler.next(e);
      }
    ));
  }

  Future<Response> get(String path) => dio.get(path);
  Future<Response> post(String path, dynamic data) => dio.post(path, data: data);
  Future<Response> put(String path, dynamic data) => dio.put(path, data: data);
  Future<Response> delete(String path) => dio.delete(path);
}
"""
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/flutter_app"
    for path, content in FILES.items():
        fp = os.path.join(root, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\\n")
    print("Flutter core scaffolded.")

if __name__ == "__main__":
    main()
