import tkinter as tk
from tkinter import ttk, filedialog
import os
import configparser

class CountdownTimerApp:
    def __init__(self, master):
        self.master = master
        master.title("Countdown Timer by Noah Dobie")

        # Initialize variables
        self.hours_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")
        self.path_var = tk.StringVar(value="")
        self.remaining_time = tk.StringVar(value="00:00:00")
        self.time = 0

        self.file_path = ""
        self.file_path_set = False

        self.timer_state = "START"
        self.timer_running = False

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config_file_path = os.path.join(os.path.expanduser("~"), "countdown_timer_config.ini")
        self.load_config()

        self.create_widgets()

    def create_widgets(self):
        # Label to display the remaining time
        ttk.Label(self.master, textvariable=self.remaining_time, font=('Helvetica', 32)).grid(row=0, column=0, columnspan=8, pady=20)

        # Labels and Entries for Hours, Minutes, Seconds
        self.create_label_and_entry("Hours:", self.hours_var, 1, 0)
        self.create_label_and_entry("Minutes:", self.minutes_var, 1, 2)
        self.create_label_and_entry("Seconds:", self.seconds_var, 1, 4)

        # Button to start/pause/resume the countdown
        self.toggle_button = ttk.Button(self.master, text="Start", command=self.toggle_countdown)
        self.toggle_button.grid(row=2, column=2, pady=10)

        # Button to stop the countdown
        self.stop_button = ttk.Button(self.master, text="Reset", command=self.stop_countdown)
        self.stop_button.grid(row=2, column=3, pady=10)

        # Button to select a file path
        self.create_path_entry_and_button()

    def create_label_and_entry(self, label_text, variable, row, column):
        ttk.Label(self.master, text=label_text).grid(row=row, column=column, pady=5)
        ttk.Entry(self.master, textvariable=variable, width=5, font=('Helvetica', 14)).grid(row=row, column=column + 1, padx=10, pady=5)

    def create_path_entry_and_button(self):
        ttk.Entry(self.master, textvariable=self.path_var, width=50, font=('Helvetica', 8)).grid(row=3, column=0, columnspan=5, padx=10, pady=10)
        ttk.Button(self.master, text="Browse", command=self.select_directory).grid(row=3, column=5, pady=10)

    def toggle_countdown(self):
        if self.file_path_set:
            actions = {
                "START": self.start_countdown,
                "PAUSE": self.pause_countdown,
                "RESUME": self.resume_countdown,
                "STOP": self.stop_countdown
            }
            actions[self.timer_state]()
        else:
            self.remaining_time.set("Select file path!")

    def check_not_zero(self, variable):
        value = variable.get()
        if not value:
            variable.set(0)
            return 0
        else:
            return int(value)

    def start_countdown(self):
        # Set toggle conditions
        self.timer_running = True
        self.timer_state = "PAUSE"
        self.toggle_button["text"] = "Pause"

        try:
            # Get input values
            hours = self.check_not_zero(self.hours_var)
            minutes = self.check_not_zero(self.minutes_var)
            seconds = self.check_not_zero(self.seconds_var)

            # Check for negative values
            if any(val < 0 for val in [hours, minutes, seconds]):
                self.handle_invalid_input()
                return

            # Calculate total seconds
            self.time = hours * 3600 + minutes * 60 + seconds

            # Check if the total time is non-negative
            if self.time <= 0:
                self.handle_invalid_input()
                return

            # Start the countdown
            self.update_countdown()

        except ValueError:
            self.handle_invalid_input()

    def handle_invalid_input(self):
        self.remaining_time.set("Invalid Input!")
        self.timer_running = False
        self.timer_state = "START"
        self.toggle_button["text"] = "Start"

    def stop_countdown(self):
        # Set toggle conditions
        self.timer_running = False
        self.timer_state = "START"
        self.toggle_button["text"] = "Start"

        remaining_time_str = "{:02d}:{:02d}:{:02d}".format(
            self.check_not_zero(self.hours_var),
            self.check_not_zero(self.minutes_var),
            self.check_not_zero(self.seconds_var)
        )
        self.remaining_time.set(remaining_time_str)
        self.save_countdown(remaining_time_str)

    def pause_countdown(self):
        # Set toggle conditions
        self.timer_running = False
        self.timer_state = "RESUME"
        self.toggle_button["text"] = "Resume"

    def resume_countdown(self):
        # Set toggle conditions
        self.timer_running = True
        self.timer_state = "PAUSE"
        self.toggle_button["text"] = "Pause"

        with open(self.file_path, "r") as file:
            hours, minutes, seconds = map(int, file.readline().split(':'))
            self.time = hours * 3600 + minutes * 60 + seconds

        self.update_countdown()

    def update_countdown(self):
        if self.timer_running:
            hours, remainder = divmod(self.time, 3600)
            minutes, seconds = divmod(remainder, 60)

            remaining_time_str = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
            self.remaining_time.set(remaining_time_str)
            self.save_countdown(remaining_time_str)

            if self.time == 0:
                self.handle_countdown_complete()
            else:
                # Update remaining time after 1000 milliseconds (1 second)
                self.time -= 1
                self.master.after(1000, self.update_countdown)

    def handle_countdown_complete(self):
        self.timer_running = False
        self.remaining_time.set("Time's up!")
        self.save_countdown("Time's up!")
        # Set toggle conditions
        self.timer_running = False
        self.timer_state = "START"
        self.toggle_button["text"] = "Start"

    def save_countdown(self, remaining_time_str):
        with open(self.file_path, "w") as file:
            file.write(remaining_time_str)

    def load_config(self):
        if os.path.exists(self.config_file_path):
            self.config.read(self.config_file_path)
            user_path = self.config["Settings"].get("user_path")
            if user_path:
                self.file_path = user_path
                self.file_path_set = True
                self.path_var.set(self.file_path)

    def save_config(self):
        # Save the user-specified path to the configuration file
        self.config["Settings"] = {"user_path": self.file_path}
        with open(self.config_file_path, "w") as configfile:
            self.config.write(configfile)

    def select_directory(self):
        # Open a file dialog to select a directory
        chosen_directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Directory")

        if chosen_directory:
            self.file_path = os.path.join(chosen_directory, "countdown_log.txt")
            self.path_var.set(self.file_path)
            self.file_path_set = True
            self.save_config()


def main():
    root = tk.Tk()
    root.resizable(False, False)
    app = CountdownTimerApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()