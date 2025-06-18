import tkinter as tk
from tkinter import messagebox, ttk
import random
import threading
import time
import pygame
import os
from datetime import datetime

class AlienEscapeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Uzaylıdan Kaçış - Şifreli Mesaj")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        self.timer_stop_event = threading.Event()
        self.countdown_thread = None
        self.timer_lock = threading.Lock()

        
        # Initialize pygame mixer for sound
        pygame.mixer.init()
        
        # Game variables
        self.secret_phrases = [
            "rocket launch", "solar panel", "space mission", "alien invasion",
            "time travel", "black hole", "warp drive", "star gate",
            "plasma cannon", "robot army", "cyber world", "quantum leap",
            "nano tech", "fusion core", "laser beam", "force field"
        ]
        
        self.current_phrase = ""
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.max_wrong = 6
        self.time_limit = 10  # seconds per guess
        self.timer_stop_event.set()
        self.game_over = False
        self.hint_used = False
        self.start_time = None
        self.trap_letters = ['x', 'z', 'j', 'q']
        
        # Create GUI
        self.create_widgets()
        self.start_new_game()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="🚀 UZAYLIDAN KAÇIŞ 👽", 
                              font=("Arial", 24, "bold"), 
                              fg='#00ff00', bg='#1a1a2e')
        title_label.pack(pady=10)
        
        # Alien position display
        self.alien_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.alien_frame.pack(pady=10)
        
        self.alien_label = tk.Label(self.alien_frame, text="🚀------👽", 
                                   font=("Courier", 20, "bold"), 
                                   fg='#ff4757', bg='#1a1a2e')
        self.alien_label.pack()
        
        # Secret phrase display
        self.phrase_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.phrase_frame.pack(pady=20)
        
        self.phrase_label = tk.Label(self.phrase_frame, text="", 
                                    font=("Arial", 18, "bold"), 
                                    fg='#ffffff', bg='#1a1a2e')
        self.phrase_label.pack()
        
        # Timer display
        self.timer_label = tk.Label(self.root, text="Süre: 10", 
                                   font=("Arial", 16, "bold"), 
                                   fg='#ffa502', bg='#1a1a2e')
        self.timer_label.pack(pady=5)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#1a1a2e')
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Harf Tahmin Et:", 
                font=("Arial", 14), fg='#ffffff', bg='#1a1a2e').pack()
        
        self.guess_entry = tk.Entry(input_frame, font=("Arial", 14), 
                                   width=5, justify='center')
        self.guess_entry.pack(pady=5)
        self.guess_entry.bind('<Return>', self.make_guess)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#1a1a2e')
        button_frame.pack(pady=10)
        
        self.guess_button = tk.Button(button_frame, text="Tahmin Et", 
                                     command=self.make_guess, 
                                     font=("Arial", 12, "bold"),
                                     bg='#3742fa', fg='white',
                                     width=10)
        self.guess_button.pack(side=tk.LEFT, padx=5)
        
        self.hint_button = tk.Button(button_frame, text="İpucu", 
                                    command=self.use_hint, 
                                    font=("Arial", 12, "bold"),
                                    bg='#f39c12', fg='white',
                                    width=10)
        self.hint_button.pack(side=tk.LEFT, padx=5)
        
        self.new_game_button = tk.Button(button_frame, text="Yeni Oyun", 
                                        command=self.start_new_game, 
                                        font=("Arial", 12, "bold"),
                                        bg='#27ae60', fg='white',
                                        width=10)
        self.new_game_button.pack(side=tk.LEFT, padx=5)
        
        # Game info
        self.info_label = tk.Label(self.root, text="", 
                                  font=("Arial", 12), 
                                  fg='#ffffff', bg='#1a1a2e')
        self.info_label.pack(pady=10)
        
        # Guessed letters display
        self.guessed_label = tk.Label(self.root, text="Tahmin Edilen Harfler: ", 
                                     font=("Arial", 10), 
                                     fg='#95a5a6', bg='#1a1a2e')
        self.guessed_label.pack(pady=5)
        
    def start_new_game(self):
        self.current_phrase = random.choice(self.secret_phrases).upper()
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.game_over = False
        self.hint_used = False
        self.start_time = time.time()
        
        self.update_phrase_display()
        self.update_alien_position()
        self.update_info()
        self.update_guessed_letters()
        
        self.guess_entry.config(state='normal')
        self.guess_button.config(state='normal')
        self.hint_button.config(state='normal')
        
        self.start_timer()
        
    def update_phrase_display(self):
        display_text = ""
        for char in self.current_phrase:
            if char == ' ':
                display_text += "  "
            elif char in self.guessed_letters:
                display_text += char + " "
            else:
                display_text += "_ "
        self.phrase_label.config(text=display_text.strip())
        
    def update_alien_position(self):
        positions = [
            "🚀------👽",
            "🚀-----👽",
            "🚀----👽",
            "🚀---👽",
            "🚀--👽",
            "🚀-👽",
            "🚀👽"
        ]
        if self.wrong_guesses < len(positions):
            self.alien_label.config(text=positions[self.wrong_guesses])
        
    def update_info(self):
        info_text = f"Yanlış Tahmin: {self.wrong_guesses}/{self.max_wrong}"
        if self.hint_used:
            info_text += " | İpucu Kullanıldı"
        self.info_label.config(text=info_text)
        
    def update_guessed_letters(self):
        guessed_text = "Tahmin Edilen Harfler: " + ", ".join(sorted(self.guessed_letters))
        self.guessed_label.config(text=guessed_text)
        
    def start_timer(self):
        if self.game_over:
            return

        # Stop previous timer thread
        if self.countdown_thread and self.countdown_thread.is_alive():
            self.timer_stop_event.set()
            self.countdown_thread.join()

        # Prepare and start a new timer
        self.timer_stop_event.clear()
        self.countdown_thread = threading.Thread(target=self.countdown)
        self.countdown_thread.daemon = True
        self.countdown_thread.start()
            
    def countdown(self):
        for i in range(self.time_limit, 0, -1):
            if self.timer_stop_event.is_set() or self.game_over:
                return
            self.timer_label.config(text=f"Süre: {i}")
            time.sleep(1)

        if not self.timer_stop_event.is_set() and not self.game_over:
            self.root.after(0, self.time_up)
            
    def time_up(self):
        self.timer_stop_event.set()
        self.wrong_guesses += 1
        self.play_sound("wrong")
        self.update_alien_position()
        self.update_info()
        messagebox.showwarning("Süre Doldu!", "Süre doldu! Uzaylı yaklaştı!")
        
        if self.wrong_guesses >= self.max_wrong:
            self.game_over_lose()
        else:
            self.start_timer()
            
    def make_guess(self, event=None):
        if self.game_over:
            return

        guess = self.guess_entry.get().upper().strip()
        self.guess_entry.delete(0, tk.END)

        if not guess or len(guess) != 1 or not guess.isalpha():
            messagebox.showerror("Hata", "Lütfen tek bir harf girin!")
            return

        if guess in self.guessed_letters:
            messagebox.showwarning("Uyarı", "Bu harfi zaten tahmin ettiniz!")
            return

        self.timer_stop_event.set()  # Stop the current timer
        self.guessed_letters.append(guess)

        if guess in self.current_phrase:
            self.play_sound("correct")
            self.update_phrase_display()

            if self.check_win():
                self.game_over_win()
                return
            else:
                self.update_info()
                self.update_guessed_letters()
                self.start_timer()  # <-- Start timer again on correct guess
        else:
            self.play_sound("wrong")

            if guess in self.trap_letters:
                self.wrong_guesses += 2
                messagebox.showwarning("Tuzak Harf!", f"'{guess}' tuzak harf! Uzaylı 2 adım yaklaştı!")
            else:
                self.wrong_guesses += 1

            self.update_alien_position()
            self.update_info()
            self.update_guessed_letters()

            if self.wrong_guesses >= self.max_wrong:
                self.game_over_lose()
            else:
                self.start_timer()  # Timer restart on wrong guess too


    def use_hint(self):
        if self.hint_used or self.game_over:
            return
            
        self.hint_used = True
        self.wrong_guesses += 1
        
        # Find first letter that hasn't been guessed
        for char in self.current_phrase:
            if char.isalpha() and char not in self.guessed_letters:
                self.guessed_letters.append(char)
                break
                
        self.update_phrase_display()
        self.update_alien_position()
        self.update_info()
        self.update_guessed_letters()
        
        self.hint_button.config(state='disabled')
        
        if self.check_win():
            self.game_over_win()
        elif self.wrong_guesses >= self.max_wrong:
            self.game_over_lose()
            
    def check_win(self):
        for char in self.current_phrase:
            if char.isalpha() and char not in self.guessed_letters:
                return False
        return True
        
    def game_over_win(self):
        self.game_over = True
        self.timer_stop_event.set()
        self.play_sound("win")
        
        elapsed_time = int(time.time() - self.start_time)
        self.save_score("KAZANDI", elapsed_time)
        
        messagebox.showinfo("Tebrikler!", f"Oyunu kazandınız!\nKelime: {self.current_phrase}\nSüre: {elapsed_time} saniye")
        
        self.guess_entry.config(state='disabled')
        self.guess_button.config(state='disabled')
        self.hint_button.config(state='disabled')
        
    def game_over_lose(self):
        self.game_over = True
        self.timer_stop_event.set()
        self.play_sound("lose")
        
        elapsed_time = int(time.time() - self.start_time)
        self.save_score("KAYBETTİ", elapsed_time)
        
        messagebox.showinfo("Oyun Bitti!", f"Uzaylı sizi yakaladı!\nKelime: {self.current_phrase}\nSüre: {elapsed_time} saniye")
        
        self.guess_entry.config(state='disabled')
        self.guess_button.config(state='disabled')
        self.hint_button.config(state='disabled')
        
    def save_score(self, result, elapsed_time):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            score_line = f"{timestamp} | {result} | {self.current_phrase.lower()} | {elapsed_time} saniye\n"
            
            with open("scores.txt", "a", encoding="utf-8") as f:
                f.write(score_line)
        except Exception as e:
            print(f"Skor kaydedilirken hata: {e}")
            
    def play_sound(self, sound_type):
        try:
            sound_files = {
                "correct": "correct.mp3",
                "wrong": "wrong.mp3",
                "win": "win.mp3",
                "lose": "lose.mp3"
            }
            
            sound_file = sound_files.get(sound_type)
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Ses çalınırken hata: {e}")
            
    def run(self):
        self.root.mainloop()

# Test için basit ses dosyaları oluşturma fonksiyonu
def create_test_sounds():
    """Test için boş ses dosyaları oluşturur"""
    sound_files = ["correct.mp3", "wrong.mp3", "win.mp3", "lose.mp3"]
    for sound_file in sound_files:
        if not os.path.exists(sound_file):
            try:
                # Boş MP3 dosyası oluştur (gerçek ses dosyası değil, sadece test için)
                with open(sound_file, "w") as f:
                    f.write("")
                print(f"{sound_file} test dosyası oluşturuldu")
            except:
                pass

if __name__ == "__main__":
    # Gerekli ses dosyalarını kontrol et
    create_test_sounds()
    
    # Oyunu başlat
    game = AlienEscapeGame()
    game.run()