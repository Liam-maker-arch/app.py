import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import json
import random
import os
from spiel import starte_spiel  # Stelle sicher, dass spiel.py existiert

data = lade_daten()
print(data)
# -------------------------------
# 💾 JSON laden oder neu anlegen
# -------------------------------
def lade_daten():
    if os.path.exists("data.json") and os.path.getsize("data.json") > 0:
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            messagebox.showwarning("Warnung", "Fehlerhafte JSON-Datei. Neue wird erstellt.")
            return {"keywords": {}, "antworten": {}}
    else:
        return {"keywords": {}, "antworten": {}}

def speichere_daten(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# -------------------------------
# 👤 Login
# -------------------------------
def login():
    user = "liam"
    password = "1234"
    while True:
        eingabe_user = simpledialog.askstring("Login", "Benutzername:").strip().lower()
        eingabe_pass = simpledialog.askstring("Login", "Passwort:", show="*").strip()
        if eingabe_user == user and eingabe_pass == password:
            messagebox.showinfo("Login", "✅ Anmeldung erfolgreich!")
            return "user"
        else:
            messagebox.showerror("Login", "❌ Falscher Benutzername oder Passwort!")

# -------------------------------
# 💬 Chatbot GUI
# -------------------------------
class ChatbotGUI:
    def __init__(self, root, status):
        self.status = status
        self.data = lade_daten()

        root.title("💬 Chatbot GUI")
        root.geometry("600x500")
        root.configure(bg="#f0f0f0")

        # Chatbereich als Canvas + Scrollbar für flexibles Layout
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#ffffff", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Eingabefeld + Button
        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.entry = tk.Entry(frame, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5), ipady=5)
        self.entry.bind("<Return>", self.sende_nachricht)
        senden_btn = tk.Button(frame, text="Senden", command=self.sende_nachricht, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        senden_btn.pack(side=tk.RIGHT, ipadx=10, ipady=5)

        # Oben: Buttons für Spiel und Admin
        top_frame = tk.Frame(root, bg="#f0f0f0")
        top_frame.pack(pady=(5,0))
        spiel_btn = tk.Button(top_frame, text="🎮 Spiel starten", command=self.spiel_starten, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        spiel_btn.pack(side=tk.LEFT, padx=5)
        admin_btn = tk.Button(top_frame, text="🛠️ Admin Login", command=self.admin_login, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        admin_btn.pack(side=tk.LEFT, padx=5)

    # ---- Nachricht senden ----
    def sende_nachricht(self, event=None):
        eingabe = self.entry.get().strip()
        if not eingabe:
            return
        self._zeige_user(eingabe)
        self.entry.delete(0, tk.END)
        eingabe_lower = eingabe.lower()

        # ---- Beenden ----
        if eingabe_lower == "exit":
            self._zeige_bot("Bis bald!", "Info")
            return

        # ---- Keyword-Suche ----
        gefunden = False
        for kat, liste in self.data["keywords"].items():
            if eingabe_lower in liste:
                antworten = self.data["antworten"].get(kat, [])
                antwort = random.choice(antworten) if antworten else "Ich weiß dazu nichts."
                self._zeige_bot(antwort, kat)
                gefunden = True
                break

        if not gefunden:
            self._zeige_bot("Das kenne ich noch nicht.", "Info")
            speichern = messagebox.askyesno("Speichern?", "Möchtest du es speichern?")
            if speichern:
                kategorie = simpledialog.askstring("Kategorie", "Kategorie:").strip().lower()
                if kategorie not in self.data["keywords"]:
                    frage = messagebox.askyesno("Neue Kategorie?", f"Die Kategorie '{kategorie}' existiert nicht. Erstellen?")
                    if not frage:
                        self._zeige_bot("Speichern abgebrochen.", "Info")
                        return
                    self.data["keywords"][kategorie] = []
                    self.data["antworten"][kategorie] = []
                    self._zeige_bot(f"Neue Kategorie '{kategorie}' erstellt.", "Info")
                self.data["keywords"][kategorie].append(eingabe_lower)
                antwort = simpledialog.askstring("Antwort", "Wie soll ich darauf antworten?").strip()
                self.data["antworten"][kategorie].append(antwort)
                speichere_daten(self.data)
                self._zeige_bot(f"'{eingabe}' wurde unter '{kategorie}' gespeichert.", "Info")

    # ---- Anzeige User ----
    def _zeige_user(self, msg):
        bubble = tk.Label(self.scrollable_frame, text=msg, bg="#DCF8C6", fg="#000000",
                          font=("Arial", 12), wraplength=400, justify="left", anchor="w", padx=10, pady=5)
        bubble.pack(anchor="e", pady=5, padx=10)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ---- Anzeige Bot ----
    def _zeige_bot(self, msg, kategorie="Chatbot"):
        bubble = tk.Label(self.scrollable_frame, text=f"{msg}", bg="#E8E8E8", fg="#000000",
                          font=("Arial", 12), wraplength=400, justify="left", anchor="w", padx=10, pady=5)
        bubble.pack(anchor="w", pady=5, padx=10)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ---- Spiel starten ----
    def spiel_starten(self):
        self._zeige_bot("🎮 Starte das Spiel ...", "Spiel")
        starte_spiel()

    # ---- Admin Login ----
    def admin_login(self):
        admin_user = simpledialog.askstring("Admin Login", "Benutzername:")
        admin_pass = simpledialog.askstring("Admin Login", "Passwort:", show="*")
        if admin_user.lower() == "admin" and admin_pass == "admin123":
            messagebox.showinfo("Admin", "✅ Admin Login erfolgreich!")
            self.status = "admin"
        else:
            messagebox.showerror("Admin", "❌ Falscher Admin Benutzername oder Passwort.")

# -------------------------------
# 🏁 Start
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    status = login()
    app = ChatbotGUI(root, status)
    root.mainloop()
