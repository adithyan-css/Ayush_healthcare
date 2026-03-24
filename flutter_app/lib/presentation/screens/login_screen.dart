import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Login")), 
      body: Center(child: ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Login"))));
  }
}\n