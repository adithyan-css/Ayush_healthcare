import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class PrakritiResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: Text("Prakriti Result")),
      body: Center(child: Column(children: [Text("Pie Chart showing Doshas"), ElevatedButton(onPressed: ()=>context.go('/home'), child: Text("Go Home"))])));
  }
}\n