import 'package:flutter/widgets.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../presentation/cubits/language_cubit.dart';

class AppText {
  static const List<Map<String, String>> supportedLanguages = <Map<String, String>>[
    <String, String>{'code': 'en', 'name': 'English'},
    <String, String>{'code': 'ta', 'name': 'Tamil'},
    <String, String>{'code': 'hi', 'name': 'Hindi'},
    <String, String>{'code': 'ja', 'name': 'Japanese'},
  ];

  static const Map<String, Map<String, String>> _strings = <String, Map<String, String>>{
    'app_name': <String, String>{'en': 'PrakritiOS', 'ta': 'பிரகிருதிOS', 'hi': 'प्रकृतिOS', 'ja': 'プラクリティOS'},
    'settings': <String, String>{'en': 'Settings', 'ta': 'அமைப்புகள்', 'hi': 'सेटिंग्स', 'ja': '設定'},
    'language': <String, String>{'en': 'Language', 'ta': 'மொழி', 'hi': 'भाषा', 'ja': '言語'},
    'notifications': <String, String>{'en': 'Notifications', 'ta': 'அறிவிப்புகள்', 'hi': 'सूचनाएं', 'ja': '通知'},
    'retake_quiz': <String, String>{'en': 'Retake Prakriti Quiz', 'ta': 'பிரகிருதி வினாடி வினாவை மீண்டும் எடுக்கவும்', 'hi': 'प्रकृति क्विज़ फिर से लें', 'ja': 'プラクリティクイズを再受験'},
    'clear_cache': <String, String>{'en': 'Clear Cache', 'ta': 'கேச் நீக்கு', 'hi': 'कैश साफ करें', 'ja': 'キャッシュをクリア'},
    'about': <String, String>{'en': 'About', 'ta': 'பற்றி', 'hi': 'परिचय', 'ja': '概要'},
    'sign_out': <String, String>{'en': 'Sign Out', 'ta': 'வெளியேறு', 'hi': 'साइन आउट', 'ja': 'サインアウト'},
    'unable_reset_quiz': <String, String>{'en': 'Unable to reset quiz right now', 'ta': 'இப்போது வினாடி வினாவை மீட்டமைக்க முடியவில்லை', 'hi': 'अभी क्विज़ रीसेट नहीं हो सका', 'ja': '現在クイズをリセットできません'},
    'cache_cleared': <String, String>{'en': 'Cache cleared', 'ta': 'கேச் நீக்கப்பட்டது', 'hi': 'कैश साफ हो गया', 'ja': 'キャッシュをクリアしました'},
    'cache_clear_failed': <String, String>{'en': 'Failed to clear cache', 'ta': 'கேச் நீக்க முடியவில்லை', 'hi': 'कैश साफ करने में विफल', 'ja': 'キャッシュのクリアに失敗しました'},
    'ritucharya_7_days': <String, String>{'en': 'Ritucharya (7 days)', 'ta': 'ருதுசரியா (7 நாட்கள்)', 'hi': 'ऋतुचर्या (7 दिन)', 'ja': 'リトゥチャリヤ（7日間）'},
    'recent_sessions': <String, String>{'en': 'Recent Sessions', 'ta': 'சமீபத்திய அமர்வுகள்', 'hi': 'हाल की सत्रें', 'ja': '最近のセッション'},
    'recent': <String, String>{'en': 'Recent', 'ta': 'சமீபம்', 'hi': 'हाल का', 'ja': '最近'},
    'get_recommendations': <String, String>{'en': 'Get Recommendations', 'ta': 'பரிந்துரைகள் பெறவும்', 'hi': 'सिफारिशें प्राप्त करें', 'ja': '推奨を取得'},
    'disease_heatmap': <String, String>{'en': 'Disease Heatmap', 'ta': 'நோய் ஹீட்மேப்', 'hi': 'रोग हीटमैप', 'ja': '疾患ヒートマップ'},
    'forecast': <String, String>{'en': 'Forecast', 'ta': 'முன்னறிவு', 'hi': 'पूर्वानुमान', 'ja': '予測'},
    'nadi_monitor': <String, String>{'en': 'Nadi Monitor', 'ta': 'நாடி மானிட்டர்', 'hi': 'नाड़ी मॉनिटर', 'ja': '脈モニター'},
    'sign_in': <String, String>{'en': 'Sign In', 'ta': 'உள்நுழை', 'hi': 'साइन इन', 'ja': 'サインイン'},
    'google_sign_in': <String, String>{'en': 'Google Sign In', 'ta': 'Google மூலம் உள்நுழை', 'hi': 'Google से साइन इन', 'ja': 'Googleでサインイン'},
    'new_user_register': <String, String>{'en': 'New user? Register', 'ta': 'புதிய பயனரா? பதிவு செய்யவும்', 'hi': 'नए उपयोगकर्ता? पंजीकरण करें', 'ja': '新規ユーザーですか？登録'},
    'register': <String, String>{'en': 'Register', 'ta': 'பதிவு', 'hi': 'पंजीकरण', 'ja': '登録'},
    'name': <String, String>{'en': 'Name', 'ta': 'பெயர்', 'hi': 'नाम', 'ja': '名前'},
    'email': <String, String>{'en': 'Email', 'ta': 'மின்னஞ்சல்', 'hi': 'ईमेल', 'ja': 'メール'},
    'password': <String, String>{'en': 'Password', 'ta': 'கடவுச்சொல்', 'hi': 'पासवर्ड', 'ja': 'パスワード'},
    'create_account': <String, String>{'en': 'Create Account', 'ta': 'கணக்கு உருவாக்கவும்', 'hi': 'खाता बनाएं', 'ja': 'アカウント作成'},
    'already_have_account': <String, String>{'en': 'Already have an account? Sign in', 'ta': 'ஏற்கனவே கணக்கு உள்ளதா? உள்நுழைக', 'hi': 'पहले से खाता है? साइन इन करें', 'ja': 'すでにアカウントがありますか？サインイン'},
    'valid_email': <String, String>{'en': 'Enter a valid email', 'ta': 'சரியான மின்னஞ்சலை உள்ளிடவும்', 'hi': 'मान्य ईमेल दर्ज करें', 'ja': '有効なメールを入力してください'},
    'minimum_6_chars': <String, String>{'en': 'Minimum 6 characters', 'ta': 'குறைந்தது 6 எழுத்துகள்', 'hi': 'कम से कम 6 अक्षर', 'ja': '6文字以上必要です'},
    'name_required': <String, String>{'en': 'Name required', 'ta': 'பெயர் தேவை', 'hi': 'नाम आवश्यक है', 'ja': '名前は必須です'},
    'valid_email_required': <String, String>{'en': 'Valid email required', 'ta': 'சரியான மின்னஞ்சல் தேவை', 'hi': 'मान्य ईमेल आवश्यक', 'ja': '有効なメールが必要です'},
  };

  static String byCode(String key, String languageCode) {
    final String code = languageCode.toLowerCase();
    final Map<String, String> row = _strings[key] ?? const <String, String>{};
    return row[code] ?? row['en'] ?? key;
  }

  static String languageName(String code) {
    for (final Map<String, String> item in supportedLanguages) {
      if ((item['code'] ?? '') == code) {
        return item['name'] ?? code;
      }
    }
    return 'English';
  }
}

extension AppLanguageText on BuildContext {
  String t(String key) {
    final String code = select((LanguageCubit cubit) => cubit.state.languageCode);
    return AppText.byCode(key, code);
  }
}
