import 'package:flutter_bloc/flutter_bloc.dart';
class AuthCubit extends Cubit<bool> {
  AuthCubit() : super(false);
  void login() => emit(true);
  void logout() => emit(false);
}\n