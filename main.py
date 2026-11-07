
import os
import re
import webbrowser
import unicodedata

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

Window.clearcolor = (0.07, 0.08, 0.12, 1)

def normalize(text):
    text = text.lower().replace("ı", "i")
    return unicodedata.normalize("NFKD", text)

class ResadApp(App):
    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=10
        )

        root.add_widget(Label(
            text="REŞAD XƏLİFƏ",
            font_size=25,
            bold=True,
            size_hint_y=None,
            height=55
        ))

        root.add_widget(Label(
            text="48 video üzrə söz axtarışı",
            font_size=16,
            size_hint_y=None,
            height=30
        ))

        self.search_box = TextInput(
            hint_text="Axtarılacaq sözü yazın...",
            multiline=False,
            font_size=18,
            size_hint_y=None,
            height=52
        )
        root.add_widget(self.search_box)

        btn = Button(
            text="AXTAR",
            size_hint_y=None,
            height=50
        )
        btn.bind(on_press=self.search)
        root.add_widget(btn)

        self.results = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None
        )
        self.results.bind(
            minimum_height=self.results.setter("height")
        )

        scroll = ScrollView()
        scroll.add_widget(self.results)
        root.add_widget(scroll)

        self.message("Axtarış üçün söz daxil edin.")
        return root

    def message(self, text):
        self.results.clear_widgets()
        self.results.add_widget(Label(
            text=text,
            size_hint_y=None,
            height=60
        ))

    def search(self, instance):
        word = normalize(self.search_box.text.strip())

        if not word:
            self.message("Zəhmət olmasa söz yazın.")
            return

        self.results.clear_widgets()
        found = 0

        titles = {}
        if os.path.exists("video_list.txt"):
            with open("video_list.txt", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|", 1)
                    if len(parts) == 2:
                        titles[parts[0]] = parts[1]

        folder = "srt"

        if not os.path.isdir(folder):
            self.message("Transkripsiya faylları hələ əlavə edilməyib.")
            return

        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".srt"):
                continue

            video_id = filename[:-4]
            title = titles.get(video_id, video_id)
            path = os.path.join(folder, filename)

            try:
                with open(path, encoding="utf-8-sig") as f:
                    content = f.read()

                blocks = re.split(r"\n\s*\n", content)

                for block in blocks:
                    lines = block.strip().splitlines()
                    if len(lines) < 3:
                        continue

                    timing = lines[1]
                    match = re.search(
                        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})",
                        timing
                    )
                    if not match:
                        continue

                    speech = " ".join(lines[2:])
                    if word not in normalize(speech):
                        continue

                    h, m, s, ms = map(int, match.groups())
                    seconds = h * 3600 + m * 60 + s

                    btn = Button(
                        text=f"{title}\n"
                             f"{h:02d}:{m:02d}:{s:02d}\n"
                             f"{speech[:180]}",
                        size_hint_y=None,
                        height=105
                    )
                    btn.bind(
                        on_press=lambda x, vid=video_id,
                        sec=seconds: self.open_video(vid, sec)
                    )
                    self.results.add_widget(btn)
                    found += 1

            except Exception:
                continue

        if found == 0:
            self.message("Bu söz tapılmadı.")

    def open_video(self, video_id, seconds):
        url = (
            f"https://www.youtube.com/watch?v={video_id}"
            f"&t={seconds}s"
        )
        webbrowser.open(url)

if __name__ == "__main__":
    ResadApp().run()
