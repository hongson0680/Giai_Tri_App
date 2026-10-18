[app]
title = Auto Visit
package.name = autovisit
package.domain = com.autovisit
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
# Bỏ cloudscraper (gây lỗi build Android), chỉ dùng requests thường
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,certifi
orientation = portrait
os.android.api = 33
os.android.minapi = 21

# Quyền truy cập Internet
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Icon
icon.filename = %(source.dir)s/icon.png

# Splash screen màu
android.presplash_color = #2196F3

[buildozer]
log_level = 2
warn_on_root = 1
