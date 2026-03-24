import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:hydrated_bloc/hydrated_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';
// import 'package:firebase_core/firebase_core.dart';

import 'core/theme.dart';
import 'presentation/cubits/auth_cubit.dart';
import 'presentation/cubits/forecast_cubit.dart';
import 'presentation/cubits/heatmap_cubit.dart';
import 'presentation/cubits/language_cubit.dart';
import 'presentation/cubits/prakriti_cubit.dart';
import 'presentation/cubits/recommendation_cubit.dart';
import 'presentation/cubits/wearable_cubit.dart';
import 'core/i18n/language_map.dart';
import 'presentation/screens/forecast_screen.dart';
import 'presentation/screens/heatmap_screen.dart';
import 'presentation/screens/home_screen.dart';
import 'presentation/screens/login_screen.dart';
import 'presentation/screens/nadi_monitor_screen.dart';
import 'presentation/screens/prakriti_quiz_screen.dart';
import 'presentation/screens/prakriti_result_screen.dart';
import 'presentation/screens/recommendation_result_screen.dart';
import 'presentation/screens/register_screen.dart';
import 'presentation/screens/settings_screen.dart';
import 'presentation/screens/splash_screen.dart';
import 'presentation/screens/state_detail_screen.dart';
import 'presentation/screens/symptom_selection_screen.dart';
import 'presentation/screens/vaidya_copilot_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // await Firebase.initializeApp();

  await Hive.initFlutter();
  await Hive.openBox('prakriti');
  await Hive.openBox('sessions');
  await Hive.openBox('settings');
  await Hive.openBox('districtRisk');
  await Hive.openBox('forecast');
  await Hive.openBox('nadiReadings');

  HydratedBloc.storage = await HydratedStorage.build(
    storageDirectory: HydratedStorageDirectory((await getApplicationDocumentsDirectory()).path),
  );

  runApp(const PrakritiApp());
}

class PrakritiApp extends StatelessWidget {
  const PrakritiApp({super.key});

  @override
  Widget build(BuildContext context) {
    final GoRouter router = GoRouter(
      initialLocation: '/',
      redirect: (BuildContext context, GoRouterState state) {
        final String? jwt = Hive.box('settings').get('jwt') as String?;
        final bool hasJwt = jwt != null && jwt.isNotEmpty;
        final String path = state.matchedLocation;

        const Set<String> publicRoutes = {'/', '/login', '/register'};

        if (!hasJwt && !publicRoutes.contains(path)) {
          return '/login';
        }

        if (hasJwt && path == '/home' && Hive.box('prakriti').isEmpty) {
          return '/quiz';
        }

        return null;
      },
      routes: <GoRoute>[
        GoRoute(path: '/', builder: (BuildContext context, GoRouterState state) => const SplashScreen()),
        GoRoute(path: '/login', builder: (BuildContext context, GoRouterState state) => const LoginScreen()),
        GoRoute(path: '/register', builder: (BuildContext context, GoRouterState state) => const RegisterScreen()),
        GoRoute(path: '/quiz', builder: (BuildContext context, GoRouterState state) => const PrakritiQuizScreen()),
        GoRoute(path: '/quiz-result', builder: (BuildContext context, GoRouterState state) => const PrakritiResultScreen()),
        GoRoute(path: '/home', builder: (BuildContext context, GoRouterState state) => const HomeScreen()),
        GoRoute(path: '/symptoms', builder: (BuildContext context, GoRouterState state) => const SymptomSelectionScreen()),
        GoRoute(path: '/recommendations', builder: (BuildContext context, GoRouterState state) => const RecommendationResultScreen()),
        GoRoute(path: '/heatmap', builder: (BuildContext context, GoRouterState state) => const HeatmapScreen()),
        GoRoute(
          path: '/state-detail',
          builder: (BuildContext context, GoRouterState state) => StateDetailScreen(stateId: state.extra as String),
        ),
        GoRoute(path: '/forecast', builder: (BuildContext context, GoRouterState state) => const ForecastScreen()),
        GoRoute(path: '/nadi', builder: (BuildContext context, GoRouterState state) => const NadiMonitorScreen()),
        GoRoute(path: '/vaidya', builder: (BuildContext context, GoRouterState state) => const VaidyaCopilotScreen()),
        GoRoute(path: '/settings', builder: (BuildContext context, GoRouterState state) => const SettingsScreen()),
      ],
    );

    return MultiBlocProvider(
      providers: <BlocProvider<dynamic>>[
        BlocProvider<AuthCubit>(create: (_) => AuthCubit()),
        BlocProvider<LanguageCubit>(create: (_) => LanguageCubit()..loadSavedLanguage()),
        BlocProvider<PrakritiCubit>(create: (_) => PrakritiCubit()),
        BlocProvider<RecommendationCubit>(create: (_) => RecommendationCubit()),
        BlocProvider<HeatmapCubit>(create: (_) => HeatmapCubit()),
        BlocProvider<ForecastCubit>(create: (_) => ForecastCubit()),
        BlocProvider<WearableCubit>(create: (_) => WearableCubit()),
      ],
      child: Builder(
        builder: (BuildContext context) => BlocBuilder<LanguageCubit, LanguageState>(
          builder: (BuildContext context, LanguageState state) => MaterialApp.router(
            title: AppText.byCode('app_name', state.languageCode),
            theme: AppTheme.lightTheme,
            debugShowCheckedModeBanner: false,
            routerConfig: router,
          ),
        ),
      ),
    );
  }
}
