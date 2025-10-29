import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from Screen import Screen
from ResultScreen import ResultScreen
from ProverbList import normalize_proverb

class GameScreen(Screen):
    def __init__(self, app):
        self.app = app
        self.answer_raw  = app.context["answer_raw"]
        self.answer_norm = app.context["answer"]
        self.rows        = app.context["max_attempts"]
        self.emoji_hint  = app.context.get("emoji_hint", "")
        self.cols        = len(self.answer_norm)
        self.input_text  = ""
        self.message   = ""    
        self.cur_row   = 0

        # Local dictionary (optional)
        self.proverb_set = getattr(app, "proverbs_norm_set", set())

        print("Answer:", self.answer_norm)
        print("Emoji hint:", self.emoji_hint)

        # Pygame
        pygame.init()
        pygame.key.start_text_input()
        self.W, self.H = 1200, 800
        self.surface = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("Proverble")

        # Theme 
        self.background  = (18, 18, 19)
        self.grid_empty  = (58, 58, 60)
        self.text_color  = (232, 232, 232)
        self.clr_green   = (83, 141, 78)
        self.clr_yellow  = (181, 159, 59)
        self.clr_gray    = (58, 58, 60)
        self.clr_red     = (220, 80, 80)
        self.clr_keycap  = (129, 131, 132)
        self.clr_keytext = (255, 255, 255)

        # Fonts
        FONT_PATH = "GamepauseddemoRegular.otf"
        self.font_cell  = pygame.font.Font(FONT_PATH, 64)
        self.font_key   = pygame.font.Font(FONT_PATH, 40)
        self.font_msg   = pygame.font.Font(FONT_PATH, 32)
        self.font_title = pygame.font.Font(FONT_PATH, 80)
        self.font_input = pygame.font.Font(FONT_PATH, 30)
        self.font_emoji = self._get_emoji_font(size=36)

        # Keyboard layout
        self.kb_top    = 480
        self.kb_rows   = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        self.key_rects = []
        self._build_keyboard_layout()

    def _get_emoji_font(self, size: int) -> pygame.font.Font:
        try_order = [
            "Segoe UI Emoji", "Segoe UI Symbol",
            "Noto Color Emoji", "Noto Emoji",
            "Apple Color Emoji",
        ]
        for fname in try_order:
            try:
                f = pygame.font.SysFont(fname, size)
                _ = f.render("🙂", True, (255, 255, 255))
                return f
            except Exception:
                pass
        return pygame.font.Font(None, size)

    # -------------- Check Valid Proverb --------------
    def _is_valid_proverb(self, proverb: str) -> bool:
        return (not self.proverb_set) or (proverb in self.proverb_set)

    # ---------------- Keyboard Layout ----------------
    def _build_keyboard_layout(self):
        key_w, key_h = 48, 58
        gap = 8
        margin_x = 24

        self.key_rects.clear()

        # Row 0
        row0 = "QWERTYUIOP"
        row0_width = len(row0) * key_w + (len(row0) - 1) * gap
        x = (self.W - row0_width) // 2
        y = self.kb_top + 0 * (key_h + 10)
        for i, ch in enumerate(row0):
            self.key_rects.append((pygame.Rect(x + i * (key_w + gap), y, key_w, key_h), ch))

        # Row 1
        row1 = "ASDFGHJKL"
        row1_width = len(row1) * key_w + (len(row1) - 1) * gap
        x = (self.W - row1_width) // 2
        y = self.kb_top + 1 * (key_h + 10)
        for i, ch in enumerate(row1):
            self.key_rects.append((pygame.Rect(x + i * (key_w + gap), y, key_w, key_h), ch))

        # Row 2: ENTER + letters + BACKSPACE
        row2_letters = "ZXCVBNM"
        enter_w = key_w + 80
        bksp_w  = key_w + 170
        row2_width = enter_w + gap + len(row2_letters)*key_w + (len(row2_letters)-1)*gap + gap + bksp_w

        max_width = self.W - 2 * margin_x
        if row2_width > max_width:
            scale   = max_width / row2_width
            key_w   = int(key_w * scale)
            key_h   = int(key_h * scale)
            enter_w = int(enter_w * scale)
            bksp_w  = int(bksp_w * scale)

            row0_width = len(row0) * key_w + (len(row0) - 1) * gap
            row1_width = len(row1) * key_w + (len(row1) - 1) * gap

            self.key_rects = []
            x = (self.W - row0_width) // 2
            y = self.kb_top + 0 * (key_h + 10)
            for i, ch in enumerate(row0):
                self.key_rects.append((pygame.Rect(x + i * (key_w + gap), y, key_w, key_h), ch))

            x = (self.W - row1_width) // 2
            y = self.kb_top + 1 * (key_h + 10)
            for i, ch in enumerate(row1):
                self.key_rects.append((pygame.Rect(x + i * (key_w + gap), y, key_w, key_h), ch))

            row2_width = enter_w + gap + len(row2_letters)*key_w + (len(row2_letters)-1)*gap + gap + bksp_w

        y = self.kb_top + 2 * (key_h + 10)
        x = (self.W - row2_width) // 2

        rect_enter = pygame.Rect(x, y, enter_w, key_h)
        self.key_rects.append((rect_enter, "ENTER"))

        x = rect_enter.right + gap
        for i, ch in enumerate(row2_letters):
            self.key_rects.append((pygame.Rect(x + i * (key_w + gap), y, key_w, key_h), ch))

        x = self.key_rects[-1][0].right + gap
        rect_bk = pygame.Rect(x, y, bksp_w, key_h)
        self.key_rects.append((rect_bk, "BACKSPACE"))

        y = self.kb_top + 3 * (key_h + 10)
        space_w = int(key_w * 3)
        x = (self.W - space_w) // 2
        rect_space = pygame.Rect(x, y, space_w, key_h)
        self.key_rects.append((rect_space, "SPACE"))

    # ---------------- Events ----------------
    def handle(self, event):
        if event is None:
            return

        if event.type == pygame.QUIT:
            self.app.set_screen(None)
            return

        if event.type == pygame.VIDEORESIZE:
            self.W, self.H = event.w, event.h
            self.surface = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
            self._build_keyboard_layout()
            return

        if event.type == pygame.TEXTINPUT:
            self._push_text(event.text); return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._backspace()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._submit_guess()
            elif event.key == pygame.K_SPACE:
                self._push_text(" ")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, label in self.key_rects:
                if rect.collidepoint(event.pos):
                    if label == "ENTER":
                        self._submit_guess()
                    elif label in ("BKSP", "BACKSPACE"):
                        self._backspace()
                    elif label == "SPACE":
                        self._push_text(" ")
                    else:
                        self._push_text(label)
                    break

    def _push_text(self, text: str):
        if len(self.input_text) + len(text) > 200:
            return
        self.input_text += text.upper()
        if self.message:
            self._set_message("")

    def _backspace(self):
        if self.input_text:
            self.input_text = self.input_text[:-1]
        if self.message:
            self._set_message("")

    # ---------------- Input ops ----------------
    def _submit_guess(self):
        guess_raw = self.input_text
        guess = normalize_proverb(guess_raw)

        if not guess:
            self._set_message("Type something first!")
            return

        if self.proverb_set and guess not in self.proverb_set:
            self._set_message("Not in proverb list.")
            return

        if guess == self.answer_norm:
            self._set_message("")
            self.app.context["result_type"] = "victory"
            self.app.set_screen(ResultScreen(self.app, "victory", self.answer_raw))
            self.input_text = ""
            return

        self.cur_row += 1
        if self.cur_row >= self.rows:
            self.app.context["result_type"] = "defeat"
            self.app.set_screen(ResultScreen(self.app, "defeat", self.answer_raw))
        else:
            self._set_message("Wrong answer")
        self.input_text = ""

    def _set_message(self, msg: str):
        self.message = msg

    # ---------------- Update ----------------
    def update(self):
        pass

    # ---------------- Render ----------------
    def render(self):
        self.surface.fill(self.background)
        self._draw_game_title()
        self._draw_input_line()
        self._draw_message()
        self._draw_keyboard()
        pygame.display.flip()

    def _draw_input_line(self):
        text = self.input_text
        surf = self.font_input.render(text, True, (255, 255, 255))
        base_y = self.H // 2 + 40
        rect = surf.get_rect(midbottom=(self.W // 2, base_y - 5))
        self.surface.blit(surf, rect)

        start_x = self.W * 0.2
        end_x   = self.W * 0.8
        pygame.draw.line(self.surface, (255, 255, 255), (start_x, base_y), (end_x, base_y), 3)

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = rect.right + 5
            pygame.draw.rect(self.surface, (255, 255, 255), (cursor_x, rect.top + 5, 3, rect.height - 5))

    def _draw_keyboard(self):
        for rect, label in self.key_rects:
            pygame.draw.rect(self.surface, self.clr_keycap, rect, border_radius=8)
            draw_label = "ENTER" if label == "ENTER" else ("BACKSPACE" if label == "BACKSPACE" else ("SPACE" if label == "SPACE" else label))
            txt = self.font_key.render(draw_label, True, self.clr_keytext)
            self.surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_message(self):
        center_x = self.W // 2
        base_y   = 180
        y_cursor = base_y

        if self.message:
            surf = self.font_msg.render(self.message, True, self.clr_red)
            rect = surf.get_rect(center=(center_x, y_cursor))
            self.surface.blit(surf, rect)
            y_cursor = rect.bottom + 10

        if self.emoji_hint:
            surf_emoji = self.font_emoji.render(self.emoji_hint, True, (255, 255, 255))
            rect_emoji = surf_emoji.get_rect(center=(center_x, y_cursor + 30))
            self.surface.blit(surf_emoji, rect_emoji)

    def _draw_game_title(self):
        surf = self.font_title.render("PROVERBLE", True, (255, 153, 255))
        rect = surf.get_rect(center=(self.W // 2, 100))
        self.surface.blit(surf, rect)
