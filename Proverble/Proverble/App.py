from typing import Optional
from Screen import Screen
from GameScreen import GameScreen
from ProverbList import load_proverbs_with_hints, choose_random_proverb, normalize_proverb

class App:
    def __init__(self):
        # Load proverbs & emoji hints
        self.proverbs_raw, self.emoji_map = load_proverbs_with_hints("ProverbList.txt")
        self.proverbs_norm_set = { normalize_proverb(p) for p in self.proverbs_raw }

        # Pick answer
        answer_raw = choose_random_proverb(self.proverbs_raw)
        answer_norm = normalize_proverb(answer_raw)
        emoji_hint = self.emoji_map.get(answer_norm, "")

        # Shared context
        self.context = {
            "answer_raw": answer_raw,             
            "answer": answer_norm,               
            "emoji_hint":  self.emoji_map.get(answer_norm, ""), 
            "attempts": [],                       
            "max_attempts": 6,                   
            "result_type": None,                 
        }

        # Set the initial screen to the main game screen
        # Optional[Screen] means it can be either a Screen or None
        self.current: Optional[Screen] = GameScreen(self)   

    # Change to another screen (or None to end the game)
    def set_screen(self, screen: Optional[Screen]):         
        self.current = screen

    # Restart
    def new_game(self): 
        from ProverbList import choose_random_proverb, normalize_proverb

        #Choose answer
        answer_raw = choose_random_proverb(self.proverbs_raw)
        answer_norm = normalize_proverb(answer_raw)

        # Reset context
        self.context["answer_raw"] = answer_raw
        self.context["answer"] = answer_norm
        self.context["emoji_hint"] = self.emoji_map.get(answer_norm, "")
        self.context["attempts"].clear()
        self.context["result_type"] = None

        self.set_screen(GameScreen(self))
        
    # Run game
    def run(self):
        import pygame

        clock = None
        while self.current is not None:
            if clock is None:
                clock = pygame.time.Clock()

            self.current.render()

            for e in pygame.event.get():
                self.current.handle(e)
                if self.current is None:
                        break

            if self.current is None:
                break

            self.current.update()
            clock.tick(60)
            

