import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  NotificationService._internal();

  static final NotificationService instance = NotificationService._internal();

  final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();

  static const String _channelId = 'prakriti_alerts';
  static const String _channelName = 'PrakritiOS Alerts';

  Future<void> initialize() async {
    try {
      const AndroidInitializationSettings androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
      const DarwinInitializationSettings iosSettings = DarwinInitializationSettings(
        requestAlertPermission: true,
        requestBadgePermission: true,
        requestSoundPermission: true,
      );

      const InitializationSettings settings = InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      );

      await _plugin.initialize(settings);

      const AndroidNotificationChannel channel = AndroidNotificationChannel(
        _channelId,
        _channelName,
        description: 'Alerts for district risk and dosha guidance',
        importance: Importance.max,
      );

      final AndroidFlutterLocalNotificationsPlugin? androidImplementation =
          _plugin.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      await androidImplementation?.createNotificationChannel(channel);
    } catch (_) {
      // Silent fail to avoid crashing app startup on unsupported platforms.
    }
  }

  Future<void> showBasic(String title, String body) async {
    try {
      final int id = DateTime.now().millisecondsSinceEpoch ~/ 1000;

      const NotificationDetails details = NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          channelDescription: 'Alerts for district risk and dosha guidance',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(),
      );

      await _plugin.show(id, title, body, details);
    } catch (_) {
      // Silent fail keeps app responsive when notifications are unavailable.
    }
  }

  Future<void> showDoshaAlert(String dosha, String tip) async {
    await showBasic('Your $dosha Dosha Alert', tip);
  }

  Future<void> showRisingAlertNotification(String stateName, String condition) async {
    await showBasic('Health Alert: $stateName', '$condition risk is rising in your region');
  }
}
