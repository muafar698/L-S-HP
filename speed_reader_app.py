import tkinter as tk
from tkinter import ttk
import time
import re


class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Läshastighetstränare")
        self.root.geometry("900x650")

        # ===== STATE =====
        self.words = []
        self.current_index = 0
        self.running = False
        self.paused = False
        self.start_time = None
        self.pause_time = 0
        self.after_id = None

        # ===== DARK THEME =====
        self.bg = "#121212"
        self.fg = "#e0e0e0"
        self.accent = "#ffd54f"

        self.root.configure(bg=self.bg)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("TButton", padding=6)

        # ===== UI =====
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)

        self.text_widget = tk.Text(
            main_frame,
            wrap="word",
            font=("Segoe UI", 14),
            bg="#1e1e1e",
            fg=self.fg,
            insertbackground="white",
            padx=10,
            pady=10
        )
        self.text_widget.pack(fill="both", expand=True)

        self.text_widget.tag_configure("highlight", background=self.accent, foreground="black")

        controls = ttk.Frame(main_frame)
        controls.pack(fill="x", pady=10)

        # Start
        self.start_button = ttk.Button(
            controls,
            text="Starta",
            command=self.start_reading
        )
        self.start_button.pack(side="left", padx=5)

        # Pause/Resume
        self.pause_button = ttk.Button(
            controls,
            text="Paus",
            command=self.toggle_pause
        )
        self.pause_button.pack(side="left", padx=5)

        # WPM slider
        self.wpm_var = tk.IntVar(value=250)
        self.slider = ttk.Scale(
            controls,
            from_=100,
            to=600,
            orient="horizontal",
            variable=self.wpm_var,
            command=self.update_wpm_label
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=10)

        self.wpm_label = ttk.Label(controls, text="250 WPM")
        self.wpm_label.pack(side="left")

        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=5)

        self.word_count_label = ttk.Label(info_frame, text="Ord: 0")
        self.word_count_label.pack(side="left", padx=5)

        self.timer_label = ttk.Label(info_frame, text="Tid: 0.0 s")
        self.timer_label.pack(side="left", padx=20)

        self.result_label = ttk.Label(info_frame, text="")
        self.result_label.pack(side="right", padx=5)

    def update_wpm_label(self, event=None):
        self.wpm_label.config(text=f"{int(self.wpm_var.get())} WPM")

    def start_reading(self):
        if self.running:
            return

        text = self.text_widget.get("1.0", "end-1c")
        self.words = list(re.finditer(r"\\S+", text))
        self.current_index = 0

        word_count = len(self.words)
        self.word_count_label.config(text=f"Ord: {word_count}")

        if word_count == 0:
            return

        self.running = True
        self.paused = False
        self.start_time = time.time()
        self.pause_time = 0
        self.result_label.config(text="")

        self.run_reader()

    def toggle_pause(self):
        if not self.running:
            return

        if not self.paused:
            # Pause
            self.paused = True
            self.pause_start = time.time()
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.pause_button.config(text="Återuppta")
        else:
            # Resume
            self.paused = False
            self.pause_time += time.time() - self.pause_start
            self.pause_button.config(text="Paus")
            self.run_reader()

    def run_reader(self):
        if not self.running or self.paused:
            return

        if self.current_index >= len(self.words):
            self.finish_reading()
            return

        self.text_widget.tag_remove("highlight", "1.0", "end")

        match = self.words[self.current_index]
        start_index = f"1.0 + {match.start()} chars"
        end_index = f"1.0 + {match.end()} chars"

        self.text_widget.tag_add("highlight", start_index, end_index)
        self.text_widget.see(start_index)

        elapsed = time.time() - self.start_time - self.pause_time
        self.timer_label.config(text=f"Tid: {elapsed:.1f} s")

        self.current_index += 1

        wpm = self.wpm_var.get()
        delay = int(60000 / wpm)

        self.after_id = self.root.after(delay, self.run_reader)

    def finish_reading(self):
        self.running = False

        total_time = time.time() - self.start_time - self.pause_time
        total_words = len(self.words)

        actual_wpm = int((total_words / total_time) * 60) if total_time > 0 else 0

        self.result_label.config(
            text=f"Klar! Tid: {total_time:.1f}s | Ord: {total_words} | Hastighet: {actual_wpm} WPM"
        )


def main():
    root = tk.Tk()
    app = SpeedReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
