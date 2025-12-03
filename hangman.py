import tkinter as tk
from tkinter import messagebox
import random


# === FÄRGKONSTANTER ===
# Bakgrundsfärger
BG_CANVAS = "white"
BG_FEEDBACK = "#d3a0a0"
BG_BUTTON_START = "pink"
BG_BUTTON_NEW_GAME = "pink"

# Textfärger
COLOR_TITLE = "darkgreen"
COLOR_INFO = "darkgreen"
COLOR_WORD_DEFAULT = "darkgreen"
COLOR_WORD_WON = "green"
COLOR_WORD_LOST = "red"

# Feedback-färger
COLOR_FEEDBACK_INFO = "#c36bde"
COLOR_FEEDBACK_CORRECT = "green"
COLOR_FEEDBACK_WRONG = "red"
COLOR_FEEDBACK_WARNING = "#ebb62f"

# Canvas-färger
COLOR_GALLOWS = "darkgray"
COLOR_HANGMAN = "black"
COLOR_CANVAS_BORDER = "black"


class WordManager:
    """Hanterar ordlistan och ordval"""
    
    # Default ordlista
    DEFAULT_WORDS = [
        "PYTHON", "PROGRAMMERING", "DATOR", "TANGENTBORD", "SKÄRM",
        "MUS", "INTERNET", "WEBB", "ALGORITM", "FUNKTION",
        "VARIABEL", "DATABAS", "NÄTVERK", "SERVER", "KLIENT"
    ]
    
    def __init__(self, word_list=None):
        self.word_list = word_list if word_list is not None else self.DEFAULT_WORDS
    
    def get_random_word(self):
        """Returnera ett slumpmässigt ord från listan"""
        return random.choice(self.word_list)


class GameState:
    """Hanterar spelets tillstånd och regler"""
    
    def __init__(self, secret_word, max_attempts=6):
        self.secret_word = secret_word.upper()
        self.max_attempts = max_attempts
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.game_over = False
    
    def guess_letter(self, letter):
        """
        Processera en bokstavsgissning
        Returnerar: (status, message)
        """
        letter = letter.upper().strip()
        
        if letter in self.guessed_letters:
            return 'already_guessed', f"Du har redan gissat på '{letter}'!"
        
        self.guessed_letters.add(letter)
        
        if letter in self.secret_word:
            if self.is_won():
                self.game_over = True
                return 'won', f"Du vann! Ordet var: {self.secret_word}"
            return 'correct', f"Bra! Bokstaven '{letter}' finns i ordet!"
        else:
            self.wrong_guesses += 1
            if self.is_lost():
                self.game_over = True
                return 'lost', f"Du förlorade! Ordet var: {self.secret_word}"
            return 'wrong', f"Tyvärr, bokstaven '{letter}' finns inte i ordet."
    
    def is_won(self):
        """Kontrollera om spelaren har vunnit"""
        return all(letter in self.guessed_letters for letter in self.secret_word)
    
    def is_lost(self):
        """Kontrollera om spelaren har förlorat"""
        return self.wrong_guesses >= self.max_attempts
    
    def get_displayed_word(self):
        """Returnera ordet med understreck för ogissade bokstäver"""
        return " ".join([letter if letter in self.guessed_letters else "_" 
                        for letter in self.secret_word])
    
    def get_remaining_attempts(self):
        """Returnera antal återstående försök"""
        return self.max_attempts - self.wrong_guesses
    
    def get_guessed_letters_sorted(self):
        """Returnera sorterad lista av gissade bokstäver"""
        return sorted(list(self.guessed_letters))


class HangmanGameController:
    """Kontroller som kopplar ihop spellogik och GUI"""
    
    def __init__(self, word_manager, max_attempts=6):
        self.word_manager = word_manager
        self.max_attempts = max_attempts
        self.game_state = None
        self.start_new_game()
    
    def start_new_game(self):
        """Starta ett nytt spel"""
        secret_word = self.word_manager.get_random_word()
        self.game_state = GameState(secret_word, self.max_attempts)
    
    def process_guess(self, letter):
        """Processera en gissning"""
        return self.game_state.guess_letter(letter)
    
    def get_game_state(self):
        """Returnera nuvarande speltillstånd"""
        return self.game_state


class HangmanCanvas:
    """Hanterar ritning av hangman-gubben"""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def draw(self, wrong_guesses):
        """Rita gubben baserat på antal felaktiga gissningar"""
        self.canvas.delete("all")
        
        # Galge (ritas alltid)
        self.canvas.create_line(50, 230, 150, 230, width=3, fill=COLOR_GALLOWS)  # Bas
        self.canvas.create_line(100, 230, 100, 50, width=3, fill=COLOR_GALLOWS)  # Stolpe
        self.canvas.create_line(100, 50, 150, 50, width=3, fill=COLOR_GALLOWS)   # Överst
        self.canvas.create_line(150, 50, 150, 80, width=3, fill=COLOR_GALLOWS)   # Rep
        
        if wrong_guesses >= 1:
            # Huvud
            self.canvas.create_oval(135, 80, 165, 110, width=2, outline=COLOR_HANGMAN)
        if wrong_guesses >= 2:
            # Kropp
            self.canvas.create_line(150, 110, 150, 160, width=2, fill=COLOR_HANGMAN)
        if wrong_guesses >= 3:
            # Vänster arm
            self.canvas.create_line(150, 125, 130, 140, width=2, fill=COLOR_HANGMAN)
        if wrong_guesses >= 4:
            # Höger arm
            self.canvas.create_line(150, 125, 170, 140, width=2, fill=COLOR_HANGMAN)
        if wrong_guesses >= 5:
            # Vänster ben
            self.canvas.create_line(150, 160, 130, 190, width=2, fill=COLOR_HANGMAN)
        if wrong_guesses >= 6:
            # Höger ben
            self.canvas.create_line(150, 160, 170, 190, width=2, fill=COLOR_HANGMAN)


class HangmanGUI:
    """Hanterar GUI:t för Hangman"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman")
        self.root.geometry("550x750")
        
        # Skapa ordhanterare med default ordlista
        word_manager = WordManager()
        
        # Skapa spelkontroller
        self.game_controller = HangmanGameController(word_manager, max_attempts=6)
        self.game_started = False
        
        self.create_widgets()
        
    def create_widgets(self):
        """Skapa GUI-komponenter"""
        # Titel
        self.title_label = tk.Label(self.root, text="HANGMAN", font=("Arial", 24, "bold"), fg=COLOR_TITLE)
        self.title_label.pack(pady=20)
        
        # Canvas för att rita gubben (visas från start)
        self.canvas = tk.Canvas(self.root, width=200, height=250, bg=BG_CANVAS, 
                                highlightthickness=2, highlightbackground=COLOR_CANVAS_BORDER)
        self.canvas.pack(pady=10)
        
        # Skapa rithanterare
        self.hangman_canvas = HangmanCanvas(self.canvas)
        # Rita tom galge från start
        self.hangman_canvas.draw(0)
        
        # Label för att visa ordet
        self.word_label = tk.Label(self.root, text="", font=("Courier", 28, "bold"), fg=COLOR_WORD_DEFAULT)
        self.word_label.pack(pady=20)
        
        # Label för återstående försök
        self.attempts_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.attempts_label.pack(pady=5)
        
        # Label för gissade bokstäver
        self.guessed_label = tk.Label(self.root, text="Gissade bokstäver: ", font=("Arial", 12))
        self.guessed_label.pack(pady=5)
        
        # Feedback label (för att visa meddelanden)
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 13, "bold"), 
                                       fg=COLOR_FEEDBACK_INFO, bg=BG_FEEDBACK, height=2, relief=tk.RIDGE)
        self.feedback_label.pack(pady=10, padx=20, fill=tk.X)
        
        # Info text
        self.info_label = tk.Label(self.root, text="Klicka på 'Starta spel' för att börja!", 
                             font=("Arial", 12), fg=COLOR_INFO)
        self.info_label.pack(pady=10)
        
        # Start knapp
        self.start_button = tk.Button(self.root, text="Starta spel", command=self.start_game,
                                      font=("Arial", 14, "bold"), bg=BG_BUTTON_START, width=15)
        self.start_button.pack(pady=10)
        
        # Ny omgång knapp (dold initialt)
        self.new_game_button = tk.Button(self.root, text="Nytt spel", command=self.new_game,
                                         font=("Arial", 14, "bold"), bg=BG_BUTTON_START, width=15)
        self.new_game_button.pack(pady=10)
        self.new_game_button.pack_forget()  # Dölj knappen initialt
        
        # Bind tangentbordstryckningar
        self.root.bind("<Key>", self.on_key_press)
        
        # Dölj spelelement tills spelet startar
        self.hide_game_elements()
    
    def hide_game_elements(self):
        """Dölj spelelement innan spelet startas"""
        self.word_label.pack_forget()
        self.attempts_label.pack_forget()
        self.guessed_label.pack_forget()
        self.feedback_label.pack_forget()
    
    def show_game_elements(self):
        """Visa spelelement när spelet startar"""
        # Canvas är redan synlig, packa bara övriga element
        self.word_label.pack(after=self.canvas, pady=20)
        self.attempts_label.pack(pady=5)
        self.guessed_label.pack(pady=5)
        self.feedback_label.pack(pady=10, padx=20, fill=tk.X)
    
    def start_game(self):
        """Starta spelet första gången"""
        self.game_started = True
        self.start_button.pack_forget()
        self.new_game_button.pack(pady=10)
        self.show_game_elements()
        self.info_label.config(text="Tryck på en bokstav på tangentbordet för att gissa")
        self.new_game()
        self.show_feedback("Lycka till! Gissa en bokstav.", COLOR_FEEDBACK_INFO)
    
    def update_display(self):
        """Uppdatera alla labels och canvas"""
        game_state = self.game_controller.get_game_state()
        
        self.word_label.config(text=game_state.get_displayed_word())
        self.attempts_label.config(text=f"Återstående försök: {game_state.get_remaining_attempts()}")
        
        guessed_letters = game_state.get_guessed_letters_sorted()
        if guessed_letters:
            self.guessed_label.config(text=f"Gissade bokstäver: {', '.join(guessed_letters)}")
        else:
            self.guessed_label.config(text="Gissade bokstäver: ")
        
        self.hangman_canvas.draw(game_state.wrong_guesses)
    
    def on_key_press(self, event):
        """Hantera tangenttryckningar"""
        if not self.game_started:
            return
            
        letter = event.char.upper()
        
        # Validera att det är en bokstav
        if letter.isalpha() and len(letter) == 1:
            self.guess_letter(letter)
    
    def show_feedback(self, message, color="blue"):
        """Visa feedback-meddelande i huvudfönstret"""
        self.feedback_label.config(text=message, fg=color)
    
    def guess_letter(self, letter):
        """Hantera en bokstavsgissning via GUI"""
        game_state = self.game_controller.get_game_state()
        
        if game_state.game_over:
            self.show_feedback("Spelet är slut! Tryck på 'Nytt spel' för att börja om.", COLOR_FEEDBACK_WARNING)
            return
        
        # Anropa spelkontrollern
        status, message = self.game_controller.process_guess(letter)
        
        # Uppdatera display
        self.update_display()
        
        # Visa feedback baserat på status
        if status == 'already_guessed':
            self.show_feedback(f"{message}", COLOR_FEEDBACK_WARNING)
        elif status == 'correct':
            self.show_feedback(f"{message}", COLOR_FEEDBACK_CORRECT)
        elif status == 'wrong':
            self.show_feedback(f"{message}", COLOR_FEEDBACK_WRONG)
        elif status == 'won':
            self.show_feedback(f"{message}", COLOR_FEEDBACK_CORRECT)
            self.word_label.config(fg=COLOR_WORD_WON)
        elif status == 'lost':
            self.show_feedback(f"{message}", COLOR_FEEDBACK_WRONG)
            self.word_label.config(text=game_state.secret_word, fg=COLOR_WORD_LOST)
    
    def new_game(self):
        """Starta ett nytt spel"""
        self.game_controller.start_new_game()
        self.word_label.config(fg=COLOR_WORD_DEFAULT)
        self.show_feedback("Nytt spel startat! Gissa en bokstav.", COLOR_FEEDBACK_INFO)
        self.update_display()


# Skapa huvudfönstret och starta spelet
if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGUI(root)
    root.mainloop()
