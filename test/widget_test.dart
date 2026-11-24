import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ios_app_studio/main.dart';

void main() {
  testWidgets('studio starter renders and navigation works', (tester) async {
    await tester.pumpWidget(const StudioApp());
    expect(find.text('Build something great.'), findsOneWidget);
    expect(find.text('My first iPhone app'), findsOneWidget);
    await tester.tap(find.text('Settings').last);
    await tester.pumpAndSettle();
    expect(find.text('Your preferences'), findsOneWidget);
    expect(find.byType(SwitchListTile), findsNWidgets(2));
  });
}
