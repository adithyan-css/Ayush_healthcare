import 'package:flutter/material.dart';
class RecommendationResultScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(length: 4, child: Scaffold(
      appBar: AppBar(title: Text("Recommendations"), bottom: TabBar(tabs: [Tab(text:"Herbs"), Tab(text:"Diet"), Tab(text:"Yoga"), Tab(text:"Dinacharya")])), 
      body: TabBarView(children: [Center(child: Text("Herbs List")), Center(child: Text("Diet List")), Center(child: Text("Yoga List")), Center(child: Text("Dinacharya List"))])
    ));
  }
}\n