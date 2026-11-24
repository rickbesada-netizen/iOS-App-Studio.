import 'package:flutter/material.dart';

void main() => runApp(const StudioApp());

class StudioApp extends StatelessWidget {
  const StudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'iOS App Studio',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF7C77FF),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0D1020),
      ),
      home: const StudioHome(),
    );
  }
}

class StudioHome extends StatefulWidget {
  const StudioHome({super.key});

  @override
  State<StudioHome> createState() => _StudioHomeState();
}

class _StudioHomeState extends State<StudioHome> {
  int selected = 0;
  bool reminders = true;
  bool darkAppearance = true;
  final List<String> sampleIdeas = <String>[
    'My first iPhone app',
    'Daily habit tracker',
    'Personal notes',
  ];

  @override
  Widget build(BuildContext context) {
    const color = Color(0xFF9D98FF);
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('iOS App Studio', style: TextStyle(fontWeight: FontWeight.w800)),
        centerTitle: false,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 12),
              Text(
                selected == 0 ? 'Build something great.' : 'Your preferences',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 29),
              ),
              const SizedBox(height: 9),
              Text(
                selected == 0
                    ? 'Your first iPhone app is ready to customise.'
                    : 'A working example of interactive Flutter settings.',
                style: const TextStyle(color: Color(0xFFADB1C8), fontSize: 15),
              ),
              const SizedBox(height: 25),
              if (selected == 0) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(24),
                    gradient: const LinearGradient(
                      colors: [Color(0xFF6257DB), Color(0xFF2B387D)],
                    ),
                  ),
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.rocket_launch_rounded, size: 34, color: Colors.white),
                      SizedBox(height: 20),
                      Text('Built on Windows.', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                      SizedBox(height: 7),
                      Text('Compiled for iPhone in the cloud. No personal Mac required.'),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
                const Text('Example app ideas', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 19)),
                const SizedBox(height: 12),
                Expanded(
                  child: ListView.separated(
                    itemCount: sampleIdeas.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 10),
                    itemBuilder: (context, index) => Card(
                      color: const Color(0xFF1A1E33),
                      child: ListTile(
                        leading: const Icon(Icons.apps_rounded, color: color),
                        title: Text(sampleIdeas[index]),
                        subtitle: const Text('Example project'),
                        trailing: const Icon(Icons.chevron_right_rounded),
                        onTap: () => showDialog<void>(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: Text(sampleIdeas[index]),
                            content: const Text('Replace this sample with your own app features in lib/main.dart.'),
                            actions: [
                              TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ] else ...[
                SwitchListTile(
                  title: const Text('Example reminders'),
                  subtitle: const Text('Illustrates interactive application state'),
                  value: reminders,
                  onChanged: (value) => setState(() => reminders = value),
                ),
                SwitchListTile(
                  title: const Text('Dark appearance'),
                  subtitle: const Text('Example preference (not yet persisted)'),
                  value: darkAppearance,
                  onChanged: (value) => setState(() => darkAppearance = value),
                ),
              ],
            ],
          ),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selected,
        backgroundColor: const Color(0xFF171B2E),
        onDestinationSelected: (index) => setState(() => selected = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_rounded), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.tune_rounded), label: 'Settings'),
        ],
      ),
    );
  }
}
