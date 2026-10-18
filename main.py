"""
Auto Visit - Kivy Android App
- Quản lý danh sách URL
- Start/Stop vòng lặp visit
- Log real-time
- Chạy nền khi tắt màn hình
"""
import os
import random
import threading
import time
from datetime import datetime

import requests

# cloudscraper tùy chọn — fallback requests nếu không có
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except Exception:
    HAS_CLOUDSCRAPER = False

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.textfield import MDTextField

# ====== GIAO DIỆN (KivyMD) ======
KV = """
Screen:
    name: "main"

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(8)

        # Tiêu đề
        MDLabel:
            text: "Auto Visit"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: dp(40)

        # Ô nhập URL (mỗi dòng 1 URL)
        MDTextField:
            id: url_input
            hint_text: "URL (mỗi dòng 1 URL)"
            mode: "rectangle"
            multiline: True
            size_hint_y: None
            height: dp(120)

        # 2 ô interval + duration
        MDBoxLayout:
            size_hint_y: None
            height: dp(70)
            spacing: dp(8)

            MDTextField:
                id: interval_input
                hint_text: "Interval (giây)"
                text: "40"
                mode: "rectangle"
                input_filter: "int"

            MDTextField:
                id: duration_input
                hint_text: "Thời lượng (giờ)"
                text: "5"
                mode: "rectangle"
                input_filter: "int"

        # Nút Start / Stop
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(8)

            MDRaisedButton:
                id: btn_start
                text: "BẮT ĐẦU"
                md_bg_color: 0.2, 0.7, 0.3, 1
                on_release: app.start_worker()

            MDRaisedButton:
                id: btn_stop
                text: "DỪNG"
                md_bg_color: 0.8, 0.2, 0.2, 1
                disabled: True
                on_release: app.stop_worker()

        # Thống kê
        MDLabel:
            id: stats_label
            text: "Sẵn sàng"
            halign: "center"
            size_hint_y: None
            height: dp(30)

        # Danh sách log
        MDLabel:
            text: "Log:"
            size_hint_y: None
            height: dp(24)
            font_style: "Subtitle2"

        ScrollView:
            MDList:
                id: log_list
"""


# ====== LOGIC VISIT URL ======
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://docln.sbs/",
]


class VisitWorker:
    """Chạy nền, gọi callback mỗi khi có kết quả."""

    def __init__(self, urls, interval, max_duration, on_log, on_stats, on_done):
        self.urls = urls
        self.interval = max(1, int(interval))
        self.max_duration = max(60, int(max_duration))
        self.on_log = on_log
        self.on_stats = on_stats
        self.on_done = on_done

        self._stop = False
        self._thread = None

        self.success = 0
        self.fail = 0
        self.round_num = 0

        # Tạo session
        if HAS_CLOUDSCRAPER:
            self.session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "android", "mobile": True}
            )
        else:
            self.session = requests.Session()

    def _headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": random.choice(REFERERS),
        }

    def _visit_once(self, url):
        try:
            r = self.session.get(url, headers=self._headers(), timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 500:
                return True, f"OK {r.status_code} ({len(r.text)} bytes)"
            return False, f"status={r.status_code} size={len(r.text)}"
        except Exception as e:
            return False, str(e)[:60]

    def _run(self):
        end_time = time.monotonic() + self.max_duration
        while not self._stop and time.monotonic() < end_time:
            self.round_num += 1
            for url in self.urls:
                if self._stop:
                    break
                ok, msg = self._visit_once(url)
                if ok:
                    self.success += 1
                else:
                    self.fail += 1
                self.on_log(ok, msg, url, self.round_num)
                self.on_stats(self.success, self.fail, self.round_num)

            if self._stop or time.monotonic() >= end_time:
                break
            # Sleep ngắn từng giây để dừng nhanh khi bấm Stop
            slept = 0
            while slept < self.interval and not self._stop:
                time.sleep(0.5)
                slept += 0.5

        self.on_done()

    def start(self):
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True


# ====== APP CHÍNH ======
class AutoApp(MDApp):
    is_running = BooleanProperty(False)

    def build(self):
        self.title = "Auto Visit"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def start_worker(self):
        if self.is_running:
            return

        # Lấy URL
        raw = self.root.ids.url_input.text.strip()
        urls = [u.strip() for u in raw.splitlines() if u.strip()]
        if not urls:
            self._toast("Chưa có URL nào")
            return

        # Lấy tham số
        try:
            interval = int(self.root.ids.interval_input.text or "40")
            hours = int(self.root.ids.duration_input.text or "5")
        except ValueError:
            self._toast("Tham số không hợp lệ")
            return

        max_duration = hours * 3600

        # Reset log
        self.root.ids.log_list.clear_widgets()
        self.root.ids.stats_label.text = f"Bắt đầu: {len(urls)} URL, mỗi {interval}s, trong {hours}h"

        # Khởi động worker
        self.worker = VisitWorker(
            urls=urls,
            interval=interval,
            max_duration=max_duration,
            on_log=self._on_log,
            on_stats=self._on_stats,
            on_done=self._on_done,
        )
        self.worker.start()

        self.is_running = True
        self.root.ids.btn_start.disabled = True
        self.root.ids.btn_stop.disabled = False

    def stop_worker(self):
        if not self.is_running:
            return
        self.worker.stop()
        self._toast("Đang dừng...")

    # ----- Callback từ worker (chạy trên thread khác) -----
    def _on_log(self, ok, msg, url, round_num):
        # Phải gọi về main thread
        def update(dt):
            ts = datetime.now().strftime("%H:%M:%S")
            prefix = "✅" if ok else "❌"
            line = f"{ts} #{round_num} {prefix} {msg}\n   {url[:50]}{'...' if len(url) > 50 else ''}"
            item = OneLineListItem(
                text=line,
                theme_text_color="Custom",
                text_color=(0.1, 0.6, 0.2, 1) if ok else (0.8, 0.2, 0.2, 1),
            )
            self.root.ids.log_list.add_widget(item)
            # Giữ tối đa 100 dòng
            children = self.root.ids.log_list.children
            if len(children) > 100:
                self.root.ids.log_list.remove_widget(children[0])

        Clock.schedule_once(update, 0)

    def _on_stats(self, ok, fail, round_num):
        def update(dt):
            self.root.ids.stats_label.text = (
                f"Đợt {round_num}  •  ✅ {ok}  •  ❌ {fail}  •  Tỉ lệ: {ok*100//max(1,ok+fail)}%"
            )
        Clock.schedule_once(update, 0)

    def _on_done(self):
        def update(dt):
            self.is_running = False
            self.root.ids.btn_start.disabled = False
            self.root.ids.btn_stop.disabled = True
            self._toast("Đã hoàn tất phiên")
        Clock.schedule_once(update, 0)

    def _toast(self, msg):
        # Android toast đơn giản
        try:
            from kivymd.toast import toast
            toast(msg)
        except Exception:
            print(msg)


if __name__ == "__main__":
    AutoApp().run()
