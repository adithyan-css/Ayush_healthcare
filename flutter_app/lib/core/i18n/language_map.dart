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
    'prakriti_quiz': <String, String>{'en': 'Prakriti Quiz', 'ta': 'பிரகிருதி வினாடி வினா', 'hi': 'प्रकृति क्विज़', 'ja': 'プラクリティクイズ'},
    'question': <String, String>{'en': 'Question', 'ta': 'கேள்வி', 'hi': 'प्रश्न', 'ja': '質問'},
    'of': <String, String>{'en': 'of', 'ta': 'இல்', 'hi': 'में से', 'ja': ' / '},
    'see_results': <String, String>{'en': 'See Results', 'ta': 'முடிவுகளை காண்க', 'hi': 'परिणाम देखें', 'ja': '結果を見る'},
    'next': <String, String>{'en': 'Next', 'ta': 'அடுத்து', 'hi': 'अगला', 'ja': '次へ'},
    'selected': <String, String>{'en': 'selected', 'ta': 'தேர்ந்தெடுக்கப்பட்டது', 'hi': 'चयनित', 'ja': '選択済み'},
    'select_symptoms': <String, String>{'en': 'Select Symptoms', 'ta': 'அறிகுறிகளைத் தேர்ந்தெடுக்கவும்', 'hi': 'लक्षण चुनें', 'ja': '症状を選択'},
    'optional_notes': <String, String>{'en': 'Optional notes', 'ta': 'விருப்ப குறிப்புகள்', 'hi': 'वैकल्पिक नोट्स', 'ja': '任意メモ'},
    'describe_symptoms': <String, String>{'en': 'Describe your symptoms in your own words', 'ta': 'உங்கள் அறிகுறிகளை உங்கள் சொற்களில் விளக்கவும்', 'hi': 'अपने लक्षण अपने शब्दों में बताएं', 'ja': '症状をあなたの言葉で説明してください'},
    'submit': <String, String>{'en': 'Submit', 'ta': 'சமர்ப்பிக்கவும்', 'hi': 'जमा करें', 'ja': '送信'},
    'generating': <String, String>{'en': 'Generating...', 'ta': 'உருவாக்கப்படுகிறது...', 'hi': 'जेनरेट हो रहा है...', 'ja': '生成中...'},
    'recommendations': <String, String>{'en': 'Recommendations', 'ta': 'பரிந்துரைகள்', 'hi': 'सिफारिशें', 'ja': '推奨'},
    'retry': <String, String>{'en': 'Retry', 'ta': 'மீண்டும் முயற்சி', 'hi': 'पुनः प्रयास', 'ja': '再試行'},
    'herbs': <String, String>{'en': 'HERBS', 'ta': 'மூலிகைகள்', 'hi': 'जड़ी-बूटियाँ', 'ja': 'ハーブ'},
    'diet': <String, String>{'en': 'DIET', 'ta': 'உணவு', 'hi': 'आहार', 'ja': '食事'},
    'yoga': <String, String>{'en': 'YOGA', 'ta': 'யோகம்', 'hi': 'योग', 'ja': 'ヨガ'},
    'dinacharya': <String, String>{'en': 'DINACHARYA', 'ta': 'தினச்சரியா', 'hi': 'दिनचर्या', 'ja': 'ディナチャリヤ'},
    'eat': <String, String>{'en': 'Eat', 'ta': 'உண்ணவும்', 'hi': 'खाएं', 'ja': '食べる'},
    'avoid': <String, String>{'en': 'Avoid', 'ta': 'தவிர்க்கவும்', 'hi': 'परहेज करें', 'ja': '避ける'},
    'prevention_30_day_plan': <String, String>{'en': '30-Day Prevention Plan', 'ta': '30 நாள் தடுப்பு திட்டம்', 'hi': '30-दिवसीय रोकथाम योजना', 'ja': '30日予防プラン'},
    'download_report': <String, String>{'en': 'Download Report', 'ta': 'அறிக்கையை பதிவிறக்கு', 'hi': 'रिपोर्ट डाउनलोड करें', 'ja': 'レポートをダウンロード'},
    'regenerate': <String, String>{'en': 'Regenerate', 'ta': 'மீண்டும் உருவாக்கு', 'hi': 'पुनः जेनरेट करें', 'ja': '再生成'},
    'condition': <String, String>{'en': 'Condition', 'ta': 'நிலை', 'hi': 'स्थिति', 'ja': '状態'},
    'bulletin': <String, String>{'en': 'Bulletin', 'ta': 'புல்லட்டின்', 'hi': 'बुलेटिन', 'ja': '速報'},
    'seasonal_advisory': <String, String>{'en': 'Seasonal Advisory', 'ta': 'பருவ ஆலோசனை', 'hi': 'मौसमी सलाह', 'ja': '季節アドバイス'},
    'dominant_nadi': <String, String>{'en': 'Dominant Nadi', 'ta': 'முக்கிய நாடி', 'hi': 'प्रमुख नाड़ी', 'ja': '主要な脈'},
    'avg_7_day_hrv': <String, String>{'en': '7-day avg HRV', 'ta': '7 நாள் சராசரி HRV', 'hi': '7-दिवसीय औसत HRV', 'ja': '7日平均HRV'},
    'anomaly': <String, String>{'en': 'ANOMALY', 'ta': 'மாறுபாடு', 'hi': 'असामान्यता', 'ja': '異常'},
    'stable': <String, String>{'en': 'Stable', 'ta': 'நிலையானது', 'hi': 'स्थिर', 'ja': '安定'},
    'sync': <String, String>{'en': 'Sync', 'ta': 'ஒத்திசை', 'hi': 'सिंक', 'ja': '同期'},
    'vaidya_copilot': <String, String>{'en': 'Vaidya Copilot', 'ta': 'வைத்யா கோபைலட்', 'hi': 'वैद्य कोपायलट', 'ja': 'ヴァイディヤ コパイロット'},
    'search_patient': <String, String>{'en': 'Search patient', 'ta': 'நோயாளியைத் தேடு', 'hi': 'रोगी खोजें', 'ja': '患者を検索'},
    'unknown': <String, String>{'en': 'Unknown', 'ta': 'தெரியாது', 'hi': 'अज्ञात', 'ja': '不明'},
    'evidence_snapshot': <String, String>{'en': 'Evidence snapshot', 'ta': 'ஆதார சுருக்கம்', 'hi': 'एविडेंस स्नैपशॉट', 'ja': 'エビデンス概要'},
    'success': <String, String>{'en': 'success', 'ta': 'வெற்றி', 'hi': 'सफलता', 'ja': '成功'},
    'no_patient': <String, String>{'en': 'No Patient', 'ta': 'நோயாளர் இல்லை', 'hi': 'कोई रोगी नहीं', 'ja': '患者なし'},
    'prakriti': <String, String>{'en': 'Prakriti', 'ta': 'பிரகிருதி', 'hi': 'प्रकृति', 'ja': 'プラクリティ'},
    'symptoms_comma': <String, String>{'en': 'Symptoms (comma-separated)', 'ta': 'அறிகுறிகள் (கமா பிரித்து)', 'hi': 'लक्षण (कॉमा से अलग)', 'ja': '症状（カンマ区切り）'},
    'symptoms_hint': <String, String>{'en': 'fever, cough, acidity', 'ta': 'காய்ச்சல், இருமல், அமிலம்', 'hi': 'बुखार, खांसी, एसिडिटी', 'ja': '発熱、咳、胃酸'},
    'loading': <String, String>{'en': 'Loading...', 'ta': 'ஏற்றப்படுகிறது...', 'hi': 'लोड हो रहा है...', 'ja': '読み込み中...'},
    'get_ai_suggestion': <String, String>{'en': 'Get AI Suggestion', 'ta': 'AI பரிந்துரை பெற', 'hi': 'AI सुझाव प्राप्त करें', 'ja': 'AI提案を取得'},
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
