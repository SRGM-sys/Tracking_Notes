import pygame
import sys
import os
import json
import random
import math

from config import *

class LevelSelector:
    def __init__(self, screen_info):
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Selector de Niveles")
        self.clock = pygame.time.Clock()
        
        self.bg_surface = self.create_gradient_bg()
        
        self.title_font = self.get_font(60)
        self.main_font = self.get_font(35)
        self.sub_font = self.get_font(22)
        self.detail_font = self.get_font(28)
        self.play_font = self.get_font(50) 
        
        self.left_w = int(self.screen_width * 0.70)
        self.right_w = self.screen_width - self.left_w
        self.right_top_h = int(self.screen_height * 0.65) 
        self.right_bottom_h = self.screen_height - self.right_top_h
        
        self.card_w = self.left_w - 100
        self.card_h = 120
        self.big_cover_size = int(self.right_w * 0.7)
        self.play_button_radius = 95 
        self.play_center = (self.left_w + (self.right_w // 2), self.right_top_h + (self.right_bottom_h // 2))
        
        self.levels = self.load_available_levels()
        self.selected_index = 0 if self.levels else -1
        
        self.scroll_y = 0
        self.is_dragging = False
        self.mouse_y_start = 0
        
        self.menu_song = os.path.join(MUSIC_DIR, "SelectorSong.wav")
        self.is_previewing = False
        self.preview_start_time = 0

        self.particle_surf = pygame.Surface((self.left_w, self.screen_height), pygame.SRCALPHA)
        self.right_panel_surf = pygame.Surface((self.right_w, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(self.right_panel_surf, PANEL_BG, self.right_panel_surf.get_rect())
        
        self.btn_surf = pygame.Surface((int(self.play_button_radius * 2.5), int(self.play_button_radius * 2.5)), pygame.SRCALPHA)
        self.play_text_normal = self.play_font.render("PLAY", True, TEXT_COLOR)
        self.play_text_hover = self.play_font.render("PLAY", True, (100, 255, 150))
        
        self.card_bg_normal = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
        pygame.draw.rect(self.card_bg_normal, (255, 255, 255, 180), self.card_bg_normal.get_rect(), width=2, border_radius=15)
        
        self.card_bg_hover = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
        pygame.draw.rect(self.card_bg_hover, (255, 255, 255, 15), self.card_bg_hover.get_rect(), border_radius=15)
        pygame.draw.rect(self.card_bg_hover, (255, 255, 255, 180), self.card_bg_hover.get_rect(), width=2, border_radius=15)
        
        self.card_bg_selected = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
        pygame.draw.rect(self.card_bg_selected, (255, 255, 255, 40), self.card_bg_selected.get_rect(), border_radius=15)
        pygame.draw.rect(self.card_bg_selected, (255, 255, 255, 180), self.card_bg_selected.get_rect(), width=2, border_radius=15)

        self.particles = []
        self.init_particles(60)

    def get_font(self, size):
        font_path = os.path.join(FONT_DIR, "pixel.ttf")
        return pygame.font.Font(font_path, size) if os.path.exists(font_path) else pygame.font.Font(None, size)

    def create_gradient_bg(self):
        gradient = pygame.Surface((1, 3))
        gradient.set_at((0, 0), GRADIENT_TOP)
        gradient.set_at((0, 1), GRADIENT_MID)
        gradient.set_at((0, 2), GRADIENT_BOTTOM)
        return pygame.transform.smoothscale(gradient, (self.screen_width, self.screen_height))

    def init_particles(self, count):
        for _ in range(count):
            size = random.randint(2, 6)
            self.particles.append({
                "x": random.uniform(0, self.left_w),
                "y": random.uniform(0, self.screen_height),
                "vx": 0, "vy": random.uniform(2.0, 5.0) + (size * 0.2), 
                "size": size,
                "color": random.choice(PARTICLE_COLORS), 
                "alpha": random.randint(80, 200) 
            })

    def update_and_draw_particles(self):
        self.particle_surf.fill((0, 0, 0, 0))
        for p in self.particles:
            p["y"] += p["vy"]
            if p["y"] > self.screen_height + 10:
                p["y"] = -10
                p["x"] = random.uniform(0, self.left_w)
            
            color_with_alpha = (p["color"][0], p["color"][1], p["color"][2], p["alpha"])
            rect = pygame.Rect(int(p["x"]), int(p["y"]), p["size"], int(p["size"] * 1.5))
            pygame.draw.ellipse(self.particle_surf, color_with_alpha, rect)
            
        self.screen.blit(self.particle_surf, (0, 0))

    def create_rounded_cover(self, cover_img, size, radius):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        if cover_img:
            img = pygame.transform.smoothscale(cover_img, (size, size))
            pygame.draw.rect(surf, (255, 255, 255, 255), surf.get_rect(), border_radius=radius)
            surf.blit(img, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        else:
            pygame.draw.rect(surf, (100, 100, 120), surf.get_rect(), border_radius=radius)
            pygame.draw.rect(surf, (200, 200, 200), surf.get_rect(), width=2, border_radius=radius)
        return surf

    def load_available_levels(self):
        levels = []
        if not os.path.exists(LEVELS_DIR):
            return levels
            
        for filename in os.listdir(LEVELS_DIR):
            if filename.endswith(".json"):
                json_path = os.path.join(LEVELS_DIR, filename)
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    
                    song_file = data.get("song", "")
                    song_path = os.path.join(MUSIC_DIR, song_file)
                    
                    if os.path.exists(song_path):
                        sound = pygame.mixer.Sound(song_path)
                        duration_sec = int(sound.get_length())
                        mins, secs = divmod(duration_sec, 60)
                        
                        cover_file = data.get("cover", "cover.png")
                        cover_path = os.path.join(IMG_DIR, cover_file)
                        
                        cover_img = pygame.image.load(cover_path).convert_alpha() if os.path.exists(cover_path) else None
                        
                        levels.append({
                            "json_path": json_path,
                            "song_path": song_path,
                            "title": data.get("title", filename.replace(".json", "")),
                            "artist": data.get("artist", "Unknown Artist"),
                            "preview_start": data.get("preview_start", 0.0),
                            "preview_end": data.get("preview_end", 10.0),
                            "small_cover": self.create_rounded_cover(cover_img, 90, 10),
                            "big_cover": self.create_rounded_cover(cover_img, self.big_cover_size, 20),
                            "notes_count": len(data.get("notes", [])),
                            "duration": f"{mins}:{secs:02d}"
                        })
                except Exception as e:
                    print(f"Error cargando {filename}: {e}")
                    
        return levels

    def draw_text_with_offset_shadow(self, text, font, text_color, shadow_color, center_pos, offset=4):
        title_surf = font.render(text, True, text_color)
        title_rect = title_surf.get_rect(center=center_pos)
        
        shadow_surf = font.render(text, True, shadow_color)
        for i in range(1, offset + 1):
            self.screen.blit(shadow_surf, (title_rect.x + i, title_rect.y + i))
                
        self.screen.blit(title_surf, title_rect)

    def play_menu_song(self):
        if os.path.exists(self.menu_song):
            pygame.mixer.music.load(self.menu_song)
            pygame.mixer.music.play(-1)
            self.is_previewing = False

    def run(self):
        pygame.mixer.init()
        self.play_menu_song()

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            
            if self.is_previewing and self.selected_index != -1:
                sel_level = self.levels[self.selected_index]
                preview_duration_ms = (sel_level["preview_end"] - sel_level["preview_start"]) * 1000
                
                if current_time - self.preview_start_time > preview_duration_ms:
                    pygame.mixer.music.stop()
                    self.play_menu_song()
            
            clicked = False
            max_scroll = -max(0, (len(self.levels) * 140) - self.screen_height + 150)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.is_dragging = True
                        self.mouse_y_start = event.pos[1]
                    elif event.button == 4: 
                        self.scroll_y = min(self.scroll_y + 40, 0)
                    elif event.button == 5:
                        self.scroll_y = max(self.scroll_y - 40, max_scroll)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False
                        if abs(event.pos[1] - self.mouse_y_start) < 5:
                            clicked = True
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging:
                        delta_y = event.pos[1] - self.mouse_y_start
                        self.scroll_y += delta_y
                        self.mouse_y_start = event.pos[1] 
                        self.scroll_y = max(min(self.scroll_y, 0), max_scroll)

            self.screen.blit(self.bg_surface, (0, 0))
            self.update_and_draw_particles()

            # --- ZONA IZQUIERDA (Recorte de Tarjetas) ---
            clip_rect = pygame.Rect(0, 130, self.left_w, self.screen_height - 130)
            self.screen.set_clip(clip_rect)
            
            list_start_y = 150 + self.scroll_y
            
            for i, level in enumerate(self.levels):
                card_y = list_start_y + (i * (self.card_h + 20))
                card_rect = pygame.Rect(50, card_y, self.card_w, self.card_h)
                
                is_hover = card_rect.collidepoint(mouse_pos)
                is_selected = (i == self.selected_index)
                
                if clicked and is_hover:
                    self.selected_index = i
                    try:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(level["song_path"])
                        pygame.mixer.music.play(start=level["preview_start"]) 
                        self.preview_start_time = pygame.time.get_ticks()
                        self.is_previewing = True
                    except Exception as e:
                        print("Error al reproducir audio:", e)
                
                if is_selected:
                    self.screen.blit(self.card_bg_selected, card_rect.topleft)
                elif is_hover:
                    self.screen.blit(self.card_bg_hover, card_rect.topleft)
                else:
                    self.screen.blit(self.card_bg_normal, card_rect.topleft)
                
                self.screen.blit(level["small_cover"], (card_rect.x + 15, card_rect.y + 15))
                
                song_title = self.main_font.render(level["title"], True, TEXT_COLOR)
                artist_name = self.sub_font.render(level["artist"], True, (200, 200, 220))
                
                self.screen.blit(song_title, (card_rect.x + 125, card_rect.y + 25))
                self.screen.blit(artist_name, (card_rect.x + 125, card_rect.y + 70))

            self.screen.set_clip(None)

            self.draw_text_with_offset_shadow(
                "SELECCIONA UN NIVEL", self.title_font, TEXT_COLOR, (20, 5, 35), (self.left_w // 2, 70)
            )

            # --- ZONA DERECHA PRINCIPAL ---
            self.screen.blit(self.right_panel_surf, (self.left_w, 0))
            pygame.draw.line(self.screen, (255, 255, 255, 50), (self.left_w, 0), (self.left_w, self.screen_height), 2)

            if self.selected_index != -1 and self.levels:
                sel_level = self.levels[self.selected_index]
                
                big_cover_x = self.left_w + (self.right_w // 2) - (self.big_cover_size // 2)
                self.screen.blit(sel_level["big_cover"], (big_cover_x, 80))
                
                info_y = 80 + self.big_cover_size + 30
                
                t_title = self.main_font.render(sel_level["title"], True, TEXT_COLOR)
                t_artist = self.detail_font.render(sel_level["artist"], True, (200, 180, 255))
                t_dur = self.sub_font.render(f"Duración: {sel_level['duration']}", True, (200, 200, 200))
                t_notes = self.sub_font.render(f"Teclas: {sel_level['notes_count']}", True, (200, 200, 200))
                
                def blit_centered(surf, y_pos):
                    rect = surf.get_rect(center=(self.left_w + (self.right_w // 2), y_pos))
                    self.screen.blit(surf, rect)
                    return y_pos + surf.get_height() + 15
                
                info_y = blit_centered(t_title, info_y)
                info_y = blit_centered(t_artist, info_y)
                info_y += 10 
                info_y = blit_centered(t_dur, info_y)
                info_y = blit_centered(t_notes, info_y)

                # --- BOTÓN PLAY DINÁMICO ---
                dist = math.hypot(mouse_pos[0] - self.play_center[0], mouse_pos[1] - self.play_center[1])
                play_hover = dist <= self.play_button_radius
                
                if clicked and play_hover:
                    pygame.mixer.music.stop()
                    return sel_level["json_path"] 
                
                btn_color = (100, 255, 150) if play_hover else (255, 255, 255)
                bg_alpha = 100 if play_hover else 30
                
                self.btn_surf.fill((0, 0, 0, 0)) 
                local_center = (self.btn_surf.get_width() // 2, self.btn_surf.get_height() // 2)
                
                pygame.draw.circle(self.btn_surf, (255, 255, 255, bg_alpha), local_center, self.play_button_radius)
                pygame.draw.circle(self.btn_surf, btn_color, local_center, self.play_button_radius, width=4)
                
                self.screen.blit(self.btn_surf, (self.play_center[0] - local_center[0], self.play_center[1] - local_center[1]))
                
                base_text = self.play_text_hover if play_hover else self.play_text_normal
                play_rect = base_text.get_rect(center=self.play_center)
                self.screen.blit(base_text, play_rect)

            pygame.display.flip()
            self.clock.tick(FPS)