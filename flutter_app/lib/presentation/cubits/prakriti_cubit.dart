import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/prakriti_model.dart';
class PrakritiCubit extends Cubit<PrakritiModel?> {
  PrakritiCubit() : super(null);
  void evaluate(Map<String, int> answers) {
    emit(PrakritiModel(vataScore: 40, pittaScore: 30, kaphaScore: 30, dominantDosha: "Vata"));
  }
}\n