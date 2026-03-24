import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:hydrated_bloc/hydrated_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';
// import 'package:firebase_core/firebase_core.dart';

import 'core/theme.dart';
import 'presentation/cubits/auth_cubit.dart';
import 'presentation/cubits/prakriti_cubit.dart';
import 'presentation/cubits/recommendation_cubit.dart';
import 'presentation/cubits/heatmap_cubit.dart';
import 'presentation/cubits/forecast_cubit.dart';
import 'presentation/cubits/wearable_cubit.dart';
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

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // await Firebase.initializeApp(); // Enable after adding google-services.json

  await Hive.initFlutter();
  await Hive.openBox('prakriti');
  await Hive.openBox('sessions');
  await Hive.openBox('settings');
  await Hive.openBox('districtRisk');
  await Hive.openBox('forecast');

  HydratedBloc.storage = await HydratedStorage.build(
    storageDirectory: HydratedStorageDirectory((await getApplicationDocumentsDirectory()).path),
  );

  runApp(const PrakritiApp());
}

class PrakritiApp extends StatelessWidget {
  const PrakritiApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final jwt = Hive.box('settings').get('jwt') as String?;
        final isLoggedIn = jwt != null && jwt.isNotEmpty;
        final isAuthPage = state.matchedLocation == '/login' || state.matchedLocation == '/register' || state.matchedLocation == '/';

        if (!isLoggedIn && !isAuthPage) {
          return '/login';
        }

        if (isLoggedIn && state.matchedLocation == '/home' && Hive.box('prakriti').isEmpty) {
          return '/quiz';
        }

        return null;
      },
      routes: [
        GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
        GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
        GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
        GoRoute(path: '/quiz', builder: (context, state) => const PrakritiQuizScreen()),
        GoRoute(path: '/quiz-result', builder: (context, state) => const PrakritiResultScreen()),
        GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
        GoRoute(path: '/symptoms', builder: (context, state) => const SymptomSelectionScreen()),
        GoRoute(path: '/recommendations', builder: (context, state) => const RecommendationResultScreen()),
        GoRoute(path: '/heatmap', builder: (context, state) => const HeatmapScreen()),
        GoRoute(path: '/state-detail', builder: (context, state) => StateDetailScreen(stateId: (state.extra as String?) ?? 'MH')),
        GoRoute(path: '/forecast', builder: (context, state) => const ForecastScreen()),
        GoRoute(path: '/nadi', builder: (context, state) => const NadiMonitorScreen()),
        GoRoute(path: '/vaidya', builder: (context, state) => const VaidyaCopilotScreen()),
        GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
      ],
    );

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
        title: 'PrakritiOS',
        theme: AppTheme.lightTheme,
        routerConfig: router,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
import 'package:flutter/material.dart';
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
