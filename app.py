import os
import tkinter as tk
from tkinter import scrolledtext, ttk
import random
import time
from pynput import keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import threading
from datetime import datetime, timedelta

class AutomationDashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Automation Dashboard")
        self.master.geometry("900x600")
        self.master.configure(bg='#F5F5F5')
        self.master.bind("<Escape>", self.unfocus)
        self.master.bind("<F10>", self.reset_automation)

        self.is_running = False
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        self.total_clicks = 0
        self.total_keystrokes = 0
        self.log_clicks = 0
        self.log_keystrokes = 0
        self.start_time = None
        self.elapsed_time = 0
        self.log_interval = tk.StringVar(value="30 detik")

        self.create_widgets()

        # Global hotkey listener
        self.hotkey_listener = keyboard.GlobalHotKeys({'<f9>': self.toggle_automation})
        self.hotkey_listener.start()

        # Start clock update
        self.update_clock()

    def create_widgets(self):
        # Title frame
        title_frame = tk.Frame(self.master, bg='#f5f5f5')
        title_frame.pack(fill=tk.X, pady=10)

        # Title label
        title_label = tk.Label(title_frame, text="Auto Click and Keystroke", font=("Montserrat", 20, "bold"), fg='#333333', bg='#f5f5f5')
        title_label.pack(side=tk.LEFT, padx=(20, 0), anchor='w')

        # Clock and Date Frame
        clock_date_frame = tk.Frame(title_frame, bg='#f5f5f5')
        clock_date_frame.pack(side=tk.RIGHT, padx=(0, 20), anchor='ne')

        # Date label (above the clock)
        self.date_label = tk.Label(title_frame, font=("Montserrat", 10), fg='#333333', bg='#f5f5f5')
        self.date_label.pack(anchor='ne')

        # Clock label (smaller and positioned at top-right)
        self.clock_label = tk.Label(title_frame, font=("Montserrat", 10), fg='#333333', bg='#f5f5f5')
        self.clock_label.pack(anchor='ne')

        # Main frame
        main_frame = tk.Frame(self.master, bg='#f5f5f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.timer_label = tk.Label(main_frame, text="Timer: 00:00:00", font=("Montserrat", 18), fg='#333333', bg='#f5f5f5')
        self.timer_label.pack(pady=5)

        # Settings frame
        settings_frame = tk.Frame(main_frame, bg='#ffffff', bd=1, relief=tk.SOLID)
        settings_frame.pack(fill=tk.X, pady=10)

        # Log interval setting
        tk.Label(settings_frame, text="Log Interval:", font=("Helvetica", 12), fg='#333333', bg='#ffffff').pack(side=tk.LEFT, padx=10, pady=5)

        interval_options = ["30 detik", "1 menit", "5 menit", "10 menit", "15 menit", "30 menit"]
        log_interval_dropdown = ttk.Combobox(settings_frame, textvariable=self.log_interval, values=interval_options,
                                             state="readonly", font=("Helvetica", 12), width=12)
        log_interval_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Status and Controls
        control_frame = tk.Frame(main_frame, bg='#ffffff', bd=1, relief=tk.SOLID)
        control_frame.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(control_frame, text="Status: Stopped", font=("Montserrat", 12, "bold"), fg='#e74c3c', bg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.toggle_button = tk.Button(control_frame, text="Start (F9)", command=self.toggle_automation, font=("Montserrat", 12, "bold"),
                                       fg='#ffffff', bg='#27ae60', activebackground='#2ecc71')
        self.toggle_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(control_frame, text="Reset (F10)", command=self.reset_automation, font=("Montserrat", 12, "bold"),
                                      fg='#ffffff', bg='#3498db', activebackground='#2980b9')
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Counters
        counter_frame = tk.Frame(main_frame, bg='#ffffff', bd=1, relief=tk.SOLID)
        counter_frame.pack(fill=tk.X, pady=10)

        self.click_label = tk.Label(counter_frame, text="Clicks: 0", font=("Montserrat", 12, "bold"), fg='#333333', bg='#ffffff')
        self.click_label.pack(side=tk.LEFT, expand=True, padx=10, pady=5)

        self.keystroke_label = tk.Label(counter_frame, text="Keystrokes: 0", font=("Montserrat", 12, "bold"), fg='#333333', bg='#ffffff')
        self.keystroke_label.pack(side=tk.LEFT, expand=True, padx=10, pady=5)

        # Log section
        log_frame = tk.Frame(main_frame, bg='#ffffff', bd=1, relief=tk.SOLID)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        log_label = tk.Label(log_frame, text="Activity Log", font=("Montserrat", 14, "bold"), fg='#333333', bg='#ffffff')
        log_label.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, bg='#ecf0f1', fg='#2c3e50')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime('%d %B %Y')
        self.clock_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.master.after(1000, self.update_clock)

    def update_timer(self):
        if self.is_running and self.start_time:
            elapsed_time = datetime.now() - self.start_time
            self.timer_label.config(text=f"Timer: {str(elapsed_time).split('.')[0]}")
            self.master.after(1000, self.update_timer)

    def toggle_automation(self):
        if not self.is_running:  # If starting automation
            self.is_running = True
            self.start_time = datetime.now()
            self.update_status("Running")
            self.update_timer()

            threading.Thread(target=self.run_automation, daemon=True).start()
        else:  # If stopping automation
            self.is_running = False
            self.update_status("Stopped")

    def update_status(self, status):
        if status == "Running":
            self.status_label.config(text="Status: Running", fg='#2ECC71')
            self.toggle_button.config(text="Stop (F9)", bg='#E74C3C', activebackground='#C0392B')
        else:
            self.status_label.config(text="Status: Stopped", fg='#E74C3C')
            self.toggle_button.config(text="Start (F9)", bg='#27AE60', activebackground='#2ECC71')

    def log_info(self, elapsed_time, mouse_clicks, keystrokes, total_actions):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timer_duration = datetime.now() - self.start_time if self.start_time else timedelta()
        log_message = (f"[{current_time}] > "
                       f"{str(timer_duration).split(".")[0]} - "
                       f"{elapsed_time:.2f}s - "
                       f"Mouse Clicks: {mouse_clicks} - "
                       f"Keystrokes: {keystrokes} - "
                       f"Total Actions: {total_actions}")
        self.log_text.insert(tk.END, log_message + '\n')
        self.log_text.see(tk.END)
        return log_message

    def run_automation(self):
        last_action_time = time.time()
        last_log_time = last_action_time

        self.unfocus()

        self.log_text.insert(tk.END, f"Log started at: {datetime.now()}" + '\n')
        self.log_text.see(tk.END)

        while self.is_running:
            current_time = time.time()

            # Randomize the interval between actions (0.5 to 3 seconds)
            if current_time - last_action_time > random.uniform(0.2, 1):
                # Randomly choose between mouse click and keystroke
                if random.random() < 0.6:  # 60% chance for mouse click
                    self.mouse.click(Button.left)
                    self.total_clicks += 1
                    self.log_clicks += 1
                else:
                    self.keyboard.press(Key.space)
                    self.keyboard.release(Key.space)
                    self.total_keystrokes += 2
                    self.log_keystrokes += 2

                last_action_time = current_time

                # Update counters
                self.master.after(0, self.update_counters)

            if current_time - last_log_time >= self.get_log_interval_seconds():
                self.elapsed_time = current_time - last_log_time
                self.master.after(0, self.update_log)
                last_log_time = current_time

            time.sleep(0.1)  # Small sleep to prevent excessive CPU usage

        self.update_status("Stopped")
        self.log_text.insert(tk.END, f"Log stopped at: {datetime.now()}" + '\n')
        self.log_text.see(tk.END)

        end_time = datetime.now()
        total_duration = end_time - self.start_time if self.start_time else timedelta()
        summary = ( f"Summary > "
                    f"Total Duration: {str(total_duration).split(".")[0]} - "
                    f"Total Mouse Clicks: {self.total_clicks} - "
                    f"Total Keystrokes: {self.total_keystrokes} - "
                    f"Total Actions: {self.total_clicks + self.total_keystrokes}")
        self.log_text.insert(tk.END, summary + '\n')
        self.log_text.see(tk.END)

    def get_log_interval_seconds(self):
        interval = self.log_interval.get()
        if interval == "30 detik":
            return 30
        elif interval == "1 menit":
            return 60
        elif interval == "5 menit":
            return 300
        elif interval == "10 menit":
            return 600
        elif interval == "15 menit":
            return 900
        elif interval == "30 menit":
            return 1800
        else:
            return 30  # default to 30 seconds if something goes wrong

    def update_log(self):
        elapsed_time = self.get_log_interval_seconds()  # Log interval is fixed at 30 seconds
        total_actions = self.log_clicks + self.log_keystrokes

        self.log_info(elapsed_time, self.log_clicks, self.log_keystrokes, total_actions)

        # Reset log counters after logging
        self.log_clicks = 0
        self.log_keystrokes = 0

    def update_counters(self):
        self.click_label.config(text=f"Clicks: {self.total_clicks}")
        self.keystroke_label.config(text=f"Keystrokes: {self.total_keystrokes}")

    def reset_automation(self, event=None):
        self.is_running = False
        self.total_clicks = 0
        self.total_keystrokes = 0
        self.log_clicks = 0
        self.log_keystrokes = 0
        self.start_time = None
        self.update_status("Stopped")
        self.update_counters()
        self.timer_label.config(text="Timer: 00:00:00")
        self.log_text.delete('1.0', tk.END)

    def on_closing(self):
        self.is_running = False
        self.hotkey_listener.stop()
        self.master.quit()

    def unfocus(self, event=None):
        self.master.focus()  # Set focus to the root window

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
