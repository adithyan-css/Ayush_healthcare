import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiQuizScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Quiz")),
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/quiz-result'), child: Text("Submit 10 Questions"))));
  }
}\n