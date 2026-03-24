import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("PrakritiOS Home")), 
      body: ListView(
        children: [
          ListTile(title: Text("Symptom Report"), onTap: ()=>context.go('/symptoms')),
          ListTile(title: Text("Recommendations"), onTap: ()=>context.go('/recommendations')),
          ListTile(title: Text("Heatmap"), onTap: ()=>context.go('/heatmap')),
          ListTile(title: Text("Forecast"), onTap: ()=>context.go('/forecast')),
          ListTile(title: Text("Nadi Monitor"), onTap: ()=>context.go('/nadi')),
          ListTile(title: Text("Vaidya Copilot"), onTap: ()=>context.go('/vaidya')),
        ]
      )
    );
  }
}\n