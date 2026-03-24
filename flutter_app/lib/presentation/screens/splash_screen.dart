import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class SplashScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    Future.delayed(Duration(seconds: 2), () {
      context.go('/login');
    });
    return Scaffold(body: Center(child: Text("PrakritiOS\nLoading...")));
  }
}\n