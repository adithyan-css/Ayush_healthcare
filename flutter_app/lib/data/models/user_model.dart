class UserModel {
	final String uid;
	final String email;
	final String displayName;
	final String? photoUrl;
	final String role;
	final DateTime createdAt;

	UserModel({
		required this.uid,
		required this.email,
		required this.displayName,
		this.photoUrl,
		required this.role,
		required this.createdAt,
	});

	factory UserModel.fromJson(Map<String, dynamic> json) {
		return UserModel(
			uid: json['uid']?.toString() ?? json['id']?.toString() ?? '',
			email: json['email']?.toString() ?? '',
			displayName: json['display_name']?.toString() ?? json['displayName']?.toString() ?? '',
			photoUrl: json['photo_url']?.toString() ?? json['photoUrl']?.toString(),
			role: json['role']?.toString() ?? 'patient',
			createdAt: DateTime.tryParse(json['created_at']?.toString() ?? json['createdAt']?.toString() ?? '') ?? DateTime.now(),
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'uid': uid,
			'email': email,
			'display_name': displayName,
			'photo_url': photoUrl,
			'role': role,
			'created_at': createdAt.toIso8601String(),
		};
	}
}
