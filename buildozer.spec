[app]
title = Auto Visit
package.name = autovisit
package.domain = com.autovisit
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests,urllib3,certifi,cloudscraper
orientation = portrait
os.android.api = 33
os.android.minapi = 21

# Quyền truy cập Internet
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Nếu muốn chạy nền khi tắt màn hình
android.presplash_lottie = data/lottie/watermelon.json

# Icon
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
