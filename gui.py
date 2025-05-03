# gui.py
import os
import sqlite3
import threading
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox
from bot import ChatBot

# — Logging setup (show only ERROR and above) —
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# — Database setup: UTF‑8 by default  —
DB_PATH = os.path.join(os.getcwd(), "data", "chat.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        sender  TEXT    NOT NULL,
        message TEXT    NOT NULL
    );
""")
conn.commit()

# — API key from env or placeholder —
# You have to paste your HuggingFace API key here.
# You can get your API key from https://huggingface.co/settings/tokens
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR API KEY HERE FROM HUGGINGFACE DELETE THIS SENTENCE AND PASTE YOUR KEY HERE")

class ChatApp:
    def __init__(self, root):
        self.bot = ChatBot(hf_token=HF_TOKEN)
        root.title("Basit Chatbot")
        root.geometry("600x500")

        # — Menu Bar for model switching :contentReference[oaicite:1]{index=1} —
        menubar = tk.Menu(root)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label="Model Değiştir…", command=self.change_model)
        settings.add_separator()
        settings.add_command(label="Çıkış", command=root.destroy)
        menubar.add_cascade(label="Ayarlar", menu=settings)
        root.config(menu=menubar)

        # — Chat display —
        self.chat_window = tk.Text(root, state='disabled', wrap='word')
        self.chat_window.pack(padx=10, pady=10, expand=True, fill='both')

        # — Entry + Send button —
        frame = tk.Frame(root)
        frame.pack(fill='x', padx=10, pady=(0,10))
        self.entry = tk.Entry(frame)
        self.entry.pack(side='left', fill='x', expand=True)
        self.entry.bind("<Return>", lambda e: self.send_message())
        tk.Button(frame, text="Gönder", command=self.send_message).pack(side='right')

        # — Status bar at bottom  —
        self.status_var = tk.StringVar(value="Hazır")
        status = tk.Label(root, textvariable=self.status_var,
                          bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side='bottom', fill='x')

        # — Load history from SQLite —
        self.load_history()

    def change_model(self):
        new_model = simpledialog.askstring("Model Değiştir",
                                           "HuggingFace model adı:")
        if new_model:
            self.bot = ChatBot(hf_token=HF_TOKEN, model=new_model)
            self._insert_message("Sistem", f"Model → {new_model}")

    def load_history(self):
        cursor.execute("SELECT sender, message FROM messages ORDER BY id")
        for sender, message in cursor.fetchall():
            self._insert_message(sender, message)

    def save_message(self, sender, message):
        cursor.execute(
            "INSERT INTO messages (sender, message) VALUES (?, ?)",
            (sender, message)
        )
        conn.commit()

    def _insert_message(self, sender, msg):
        # Ensure Unicode is displayed correctly 
        text = f"{sender}: {msg}\n"
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, text)
        self.chat_window.config(state='disabled')
        self.chat_window.see(tk.END)

    def send_message(self):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return

        # Insert & save user message
        self._insert_message("Siz", user_msg)
        self.save_message("Siz", user_msg)
        self.entry.delete(0, tk.END)

        # Update status and call API in background
        self.status_var.set("Gönderiliyor…")
        threading.Thread(target=self._fetch_bot_response,
                         args=(user_msg,), daemon=True).start()

    def _fetch_bot_response(self, user_msg):
        try:
            bot_msg = self.bot.get_response(user_msg)
        except Exception as e:
            bot_msg = f"[Hata] {e}"
        # Back on the main thread, update UI
        self.chat_window.after(0, lambda: self._insert_and_save(bot_msg))

    def _insert_and_save(self, bot_msg):
        self._insert_message("Bot", bot_msg)
        self.save_message("Bot", bot_msg)
        self.status_var.set("Hazır")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
