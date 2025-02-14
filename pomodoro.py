import time
import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

def lock_screen():
    # Fonction pour verrouiller l'écran (fonctionne sur Windows uniquement)
    ctypes.windll.user32.LockWorkStation()

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x500")
        self.root.configure(bg="#f2f2f2")

        # Variables de configuration
        self.is_work_time = True
        self.time_remaining = 0
        self.total_elapsed_time = 0
        self.is_paused = False
        self.global_time_remaining = 0

        # Champs d'entrée pour les durées
        self.create_duration_selectors()

        # Bouton de démarrage
        self.start_button = tk.Button(root, text="Démarrer", font=("Helvetica", 14), command=self.start_cycle, width=10, height=2)
        self.start_button.pack(pady=20)

        # Bouton de pause/reprise (caché au début)
        self.pause_button = tk.Button(root, text="Pause", font=("Helvetica", 12), command=self.toggle_pause, state=tk.DISABLED)
        
        # Timer pour le cycle actuel (travail/pause)
        self.label = tk.Label(root, text="", font=("Helvetica", 16), bg="#f2f2f2")
        
        self.timer_label = tk.Label(root, text="", font=("Helvetica", 48), bg="#f2f2f2")
        
        # Minuteur global en bas de l'interface pour le rendre plus visible
        self.global_timer_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"), fg="blue", bg="#f2f2f2")

    def create_duration_selectors(self):
        # Section Durée de travail
        self.work_frame = tk.Frame(self.root, bg="#f2f2f2")
        self.work_frame.pack(pady=10)
        tk.Label(self.work_frame, text="Durée de travail:", bg="#f2f2f2").grid(row=0, column=0, sticky="w")

        self.work_hours = ttk.Combobox(self.work_frame, values=[str(i) for i in range(10)], width=3)
        self.work_hours.set("0")
        self.work_hours.grid(row=0, column=1, padx=(10, 2))
        tk.Label(self.work_frame, text="h", bg="#f2f2f2").grid(row=0, column=2)

        self.work_minutes = ttk.Combobox(self.work_frame, values=[str(i * 5) for i in range(12)], width=3)
        self.work_minutes.set("25")
        self.work_minutes.grid(row=0, column=3, padx=(10, 2))
        tk.Label(self.work_frame, text="min", bg="#f2f2f2").grid(row=0, column=4)

        # Section Durée de pause
        self.break_frame = tk.Frame(self.root, bg="#f2f2f2")
        self.break_frame.pack(pady=10)
        tk.Label(self.break_frame, text="Durée de pause:", bg="#f2f2f2").grid(row=0, column=0, sticky="w")

        self.break_hours = ttk.Combobox(self.break_frame, values=[str(i) for i in range(10)], width=3)
        self.break_hours.set("0")
        self.break_hours.grid(row=0, column=1, padx=(10, 2))
        tk.Label(self.break_frame, text="h", bg="#f2f2f2").grid(row=0, column=2)

        self.break_minutes = ttk.Combobox(self.break_frame, values=[str(i * 5) for i in range(12)], width=3)
        self.break_minutes.set("5")
        self.break_minutes.grid(row=0, column=3, padx=(10, 2))
        tk.Label(self.break_frame, text="min", bg="#f2f2f2").grid(row=0, column=4)

        # Section Durée totale de travail
        self.total_frame = tk.Frame(self.root, bg="#f2f2f2")
        self.total_frame.pack(pady=10)
        tk.Label(self.total_frame, text="Durée totale de travail:", bg="#f2f2f2").grid(row=0, column=0, sticky="w")

        self.total_hours = ttk.Combobox(self.total_frame, values=[str(i) for i in range(10)], width=3)
        self.total_hours.set("3")
        self.total_hours.grid(row=0, column=1, padx=(10, 2))
        tk.Label(self.total_frame, text="h", bg="#f2f2f2").grid(row=0, column=2)

        self.total_minutes = ttk.Combobox(self.total_frame, values=[str(i * 5) for i in range(12)], width=3)
        self.total_minutes.set("0")
        self.total_minutes.grid(row=0, column=3, padx=(10, 2))
        tk.Label(self.total_frame, text="min", bg="#f2f2f2").grid(row=0, column=4)

    def convert_to_seconds(self, hours, minutes):
        return int(hours) * 3600 + int(minutes) * 60

    def start_cycle(self):
        try:
            # Récupérer et convertir les durées sélectionnées
            work_duration = self.convert_to_seconds(self.work_hours.get(), self.work_minutes.get())
            break_duration = self.convert_to_seconds(self.break_hours.get(), self.break_minutes.get())
            total_duration = self.convert_to_seconds(self.total_hours.get(), self.total_minutes.get())

            # Vérifier que toutes les durées sont valides
            if work_duration <= 0 or break_duration <= 0 or total_duration <= 0:
                raise ValueError

            # Initialiser les timers
            self.time_remaining = work_duration
            self.global_time_remaining = total_duration
            self.is_work_time = True

            # Masquer les éléments d'entrée et le bouton "Démarrer"
            self.start_button.pack_forget()
            self.work_frame.pack_forget()
            self.break_frame.pack_forget()
            self.total_frame.pack_forget()

            # Afficher les éléments du timer
            self.label.pack(pady=10)
            self.timer_label.pack(pady=20)
            self.global_timer_label.pack(pady=10)
            self.pause_button.pack(pady=5)

            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)

            # Démarrer les minuteurs
            self.update_global_timer()
            self.update_timer()
            self.label.config(text="Session de Travail")

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des durées valides.")

    def update_global_timer(self):
        # Mise à jour du minuteur global pour afficher le temps de travail total restant
        mins, secs = divmod(self.global_time_remaining, 60)
        hours, mins = divmod(mins, 60)
        self.global_timer_label.config(text=f"Total Restant: {hours:02d}:{mins:02d}:{secs:02d}")

        if self.global_time_remaining > 0:
            # Met à jour le timer global toutes les secondes
            self.global_time_remaining -= 1
            self.root.after(1000, self.update_global_timer)
        else:
            # Si le temps total est écoulé, arrêtez le script
            messagebox.showinfo("Pomodoro", "Temps de travail total atteint, fin de la session.")
            self.root.quit()

    def update_timer(self):
        if not self.is_paused and self.global_time_remaining > 0:
            # Calcul du temps restant en minutes et secondes pour le cycle actuel
            mins, secs = divmod(self.time_remaining, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

            if self.time_remaining > 0:
                # Met à jour le timer toutes les secondes
                self.time_remaining -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.switch_mode()

    def switch_mode(self):
        # Passage de la session de travail à la pause et inversement
        if self.is_work_time:
            self.label.config(text="Pause")
            self.time_remaining = self.convert_to_seconds(self.break_hours.get(), self.break_minutes.get())
            self.is_work_time = False
            self.update_timer()
            self.show_countdown(5)  # Affiche un décompte de 5 secondes avant de verrouiller l'écran
        else:
            # Retour au travail après la pause
            self.label.config(text="Session de Travail")
            self.time_remaining = self.convert_to_seconds(self.work_hours.get(), self.work_minutes.get())
            self.is_work_time = True
            self.update_timer()

    def show_countdown(self, duration):
        # Affiche un compte à rebours en plein écran avant le verrouillage
        fullscreen = tk.Toplevel(self.root)
        fullscreen.attributes('-fullscreen', True)
        fullscreen.configure(bg="black")

        label = tk.Label(fullscreen, text="", font=("Helvetica", 72), fg="white", bg="black")
        label.pack(expand=True)

        def countdown(time_left):
            mins, secs = divmod(time_left, 60)
            label.config(text=f"{mins:02d}:{secs:02d}")
            if time_left > 0:
                fullscreen.after(1000, countdown, time_left - 1)
            else:
                fullscreen.destroy()
                lock_screen()

        countdown(duration)

    def toggle_pause(self):
        # Bascule entre pause et reprise
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.update_timer()
        else:
            self.is_paused = True
            self.pause_button.config(text="Reprendre")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
