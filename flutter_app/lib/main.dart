import 'package:flutter/material.dart';
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
}\n