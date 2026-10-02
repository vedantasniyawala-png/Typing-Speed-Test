"""
Typing Speed Test
-----------------
A university-level Python project demonstrating:
  * Strings   - comparing typed text with a target sentence, character by character
  * Functions - small, reusable, testable pieces of logic (no GUI code inside them)
  * GUI       - a Tkinter window with live colour feedback, timer and results

Run:  python typing_speed_test.py
"""

import random
import time
import tkinter as tk

# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice makes a person perfect, so keep typing every day.",
    "Python is an easy language to learn and a powerful one to master.",
    "A journey of a thousand miles begins with a single step.",
    "Good programmers write code that humans can easily understand.",
    "Coffee, curiosity and consistency are the keys to learning fast.",
    "Every expert was once a beginner who refused to give up.",
]


MIN_ACCURACY = 60  # % of characters that must be correct for a valid result


# ----------------------------------------------------------------------------
# LOGIC FUNCTIONS (pure string / maths logic, no GUI)
# ----------------------------------------------------------------------------
def pick_sentence(previous=None):
    """Return a random sentence, avoiding an immediate repeat."""
    choices = [s for s in SENTENCES if s != previous]
    return random.choice(choices)


def count_correct_chars(target, typed):
    """Count characters in `typed` that match `target` at the same position."""
    correct = 0
    for i, ch in enumerate(typed):
        if i < len(target) and ch == target[i]:
            correct += 1
    return correct


def calculate_accuracy(target, typed):
    """Accuracy as a percentage of typed characters that were correct."""
    if len(typed) == 0:
        return 0.0
    return count_correct_chars(target, typed) / len(typed) * 100


def calculate_wpm(target, typed, seconds):
    """
    NET words per minute using the standard rule: 1 word = 5 characters.
    Only CORRECT characters count, so random key-mashing scores near zero.
    """
    if seconds <= 0:
        return 0.0
    words = count_correct_chars(target, typed) / 5
    minutes = seconds / 60
    return words / minutes


def get_rating(wpm):
    """Turn a WPM number into a friendly label."""
    if wpm < 20:
        return "Beginner"
    elif wpm < 40:
        return "Average"
    elif wpm < 60:
        return "Good"
    elif wpm < 80:
        return "Fast"
    return "Expert"


# ----------------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------------
class TypingTestApp:
    BG = "#1e1e2e"
    FG = "#cdd6f4"
    GOOD = "#a6e3a1"
    BAD = "#f38ba8"
    DIM = "#6c7086"
    ACCENT = "#89b4fa"

    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.configure(bg=self.BG, padx=30, pady=25)
        self.root.resizable(False, False)

        self.target = ""
        self.start_time = None
        self.finished = False
        self.best_wpm = 0.0

        self.build_widgets()
        self.new_test()

    # ---- building the interface -------------------------------------------
    def build_widgets(self):
        tk.Label(
            self.root, text="Typing Speed Test", font=("Segoe UI", 22, "bold"),
            bg=self.BG, fg=self.ACCENT,
        ).pack(pady=(0, 5))

        tk.Label(
            self.root, text="Start typing the sentence below. The timer begins on your first key.",
            font=("Segoe UI", 10), bg=self.BG, fg=self.DIM,
        ).pack(pady=(0, 15))

        # Text widget lets us colour each character individually using tags
        self.display = tk.Text(
            self.root, height=3, width=52, wrap="word", font=("Consolas", 16),
            bg=self.BG, fg=self.DIM, bd=0, highlightthickness=0, state="disabled",
        )
        self.display.tag_configure("pending", foreground=self.DIM)
        self.display.tag_configure("correct", foreground=self.GOOD)
        self.display.tag_configure("wrong", foreground=self.BAD, underline=True)
        self.display.pack(pady=10)

        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_type)
        self.entry = tk.Entry(
            self.root, textvariable=self.entry_var, width=52, font=("Consolas", 16),
            bg="#313244", fg=self.FG, insertbackground=self.FG, bd=0, relief="flat",
        )
        self.entry.pack(pady=10, ipady=8)

        self.timer_label = tk.Label(
            self.root, text="Time: 0.0 s", font=("Segoe UI", 12),
            bg=self.BG, fg=self.FG,
        )
        self.timer_label.pack(pady=(10, 0))

        self.result_label = tk.Label(
            self.root, text="", font=("Segoe UI", 13, "bold"),
            bg=self.BG, fg=self.FG, justify="center",
        )
        self.result_label.pack(pady=10)

        self.best_label = tk.Label(
            self.root, text="Best: -", font=("Segoe UI", 10),
            bg=self.BG, fg=self.DIM,
        )
        self.best_label.pack()

        tk.Button(
            self.root, text="New Test", command=self.new_test,
            font=("Segoe UI", 11, "bold"), bg=self.ACCENT, fg=self.BG,
            activebackground=self.FG, bd=0, padx=20, pady=6, cursor="hand2",
        ).pack(pady=(12, 0))

    # ---- test lifecycle ---------------------------------------------------
    def new_test(self):
        """Reset everything and load a fresh sentence."""
        self.target = pick_sentence(self.target)
        self.start_time = None
        self.finished = False

        self.entry.config(state="normal")
        self.entry_var.set("")
        self.entry.focus_set()

        self.timer_label.config(text="Time: 0.0 s")
        self.result_label.config(text="")
        self.update_display("")

    def on_type(self, *_):
        """Called every time the entry text changes."""
        if self.finished:
            return

        typed = self.entry_var.get()

        # start the clock on the very first character
        if self.start_time is None and typed:
            self.start_time = time.time()
            self.tick()

        self.update_display(typed)

        # test ends when the user has typed as many characters as the sentence
        if len(typed) >= len(self.target):
            self.finish(typed)

    def update_display(self, typed):
        """Colour each character: green = correct, red = wrong, grey = not typed yet."""
        self.display.config(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0", self.target)

        for i in range(len(self.target)):
            if i < len(typed):
                tag = "correct" if typed[i] == self.target[i] else "wrong"
            else:
                tag = "pending"
            self.display.tag_add(tag, f"1.{i}", f"1.{i + 1}")

        self.display.config(state="disabled")

    def tick(self):
        """Refresh the live timer roughly 10 times a second."""
        if self.start_time is None or self.finished:
            return
        elapsed = time.time() - self.start_time
        self.timer_label.config(text=f"Time: {elapsed:.1f} s")
        self.root.after(100, self.tick)

    def finish(self, typed):
        """Stop the test, calculate the scores and show them."""
        self.finished = True
        elapsed = time.time() - self.start_time

        wpm = calculate_wpm(self.target, typed, elapsed)
        accuracy = calculate_accuracy(self.target, typed)

        self.entry.config(state="disabled")
        self.timer_label.config(text=f"Time: {elapsed:.1f} s")

        # too many mistakes: no rating and no chance at a best score
        if accuracy < MIN_ACCURACY:
            self.result_label.config(
                text=f"{wpm:.1f} WPM   |   {accuracy:.1f}% accuracy\n"
                     f"Too many mistakes (need {MIN_ACCURACY}%+). Try again!"
            )
            return

        self.result_label.config(
            text=f"{wpm:.1f} WPM   |   {accuracy:.1f}% accuracy   |   {get_rating(wpm)}"
        )

        if wpm > self.best_wpm:
            self.best_wpm = wpm
            self.best_label.config(text=f"Best: {self.best_wpm:.1f} WPM")


# ----------------------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------------------
def main():
    root = tk.Tk()
    TypingTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
