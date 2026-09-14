import pygame
import sys
import json
import os
import random
import numpy as np

from config import *
from gif_loader import AnimatedGif

class RhythmGame:
    def __init__(self, data_queue, screen_info, level_json_path):
        # 1. Configuración de Pantalla
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("NIoT Ritmo")
        self.clock = pygame.time.Clock()
        self.data_queue = data_queue
        
        # 2. Geometría y Layout
        self.game_w = int(self.screen_width * 0.60)
        self.game_h = self.screen_height
        self.right_panel_w = self.screen_width - self.game_w
        self.cam_h = int(self.screen_height * 0.40)
        self.info_h = self.screen_height - self.cam_h
        
        self.lanes_count = 6
        self.lane_width = self.game_w / self.lanes_count
        self.note_height = int(self.lane_width * 1.6) 
        
        self.catcher_width = int(self.game_w / 5)
        self.catcher_height = 20
        self.target_x = float(self.game_w // 2)
        self.catcher_x_float = self.target_x
        self.catcher_y = self.game_h - 60
        
        # 3. Variables de Estado del Juego
        self.latest_frame = None
        self.music_started = False
        self.level_finished = False
        self.level_finish_time = 0
        self.score = 0
        self.notes_hit = 0  
        self.total_notes_in_level = 0 
        self.song_length_ms = 0 
        
        # 4. Efectos Visuales (VFX)
        self.particles = []
        self.glow_alpha = 0 
        self.hit_feedback = ""
        self.hit_color = (255, 255, 255)
        self.hit_timer = 0
        self.pulse_scale = 1.0 
        self.record_angle = 0
        
        # 5. Carga de Recursos (Assets)
        self.bg_surface = self.create_gradient_bg()
        self.niot_logo = self.load_image("niot.png", scale_width=int(self.right_panel_w * 0.42))
        self.dance_gif = AnimatedGif(os.path.join(IMG_DIR, "dance.gif"))
        
        self.load_level(level_json_path)
        self.record_surface = self.create_record_surface()

    # ==========================================
    # FUNCIONES DE CARGA Y RENDERIZADO INICIAL
    # ==========================================
    def get_font(self, size):
        font_path = os.path.join(FONT_DIR, "pixel.ttf")
        return pygame.font.Font(font_path, size) if os.path.exists(font_path) else pygame.font.Font(None, size)

    def load_image(self, filename, scale_width=None):
        path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(path): 
            return None
        
        img = pygame.image.load(path).convert_alpha()
        if scale_width:
            aspect_ratio = img.get_height() / img.get_width()
            new_height = int(scale_width * aspect_ratio)
            img = pygame.transform.smoothscale(img, (scale_width, new_height))
        return img

    def create_gradient_bg(self):
        gradient = pygame.Surface((1, 3))
        gradient.set_at((0, 0), GRADIENT_TOP)
        gradient.set_at((0, 1), GRADIENT_MID)
        gradient.set_at((0, 2), GRADIENT_BOTTOM)
        return pygame.transform.smoothscale(gradient, (self.game_w, self.game_h))

    def create_record_surface(self):
        radius = int(self.right_panel_w * 0.18)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        # Base del vinilo
        pygame.draw.circle(surf, (15, 15, 15), (radius, radius), radius)
        for r in range(int(radius * 0.85), radius - 2, 8):
            pygame.draw.circle(surf, (35, 35, 35), (radius, radius), r, 2)
        
        # Etiqueta central (Portada)
        label_radius = int(radius * 0.80)
        if hasattr(self, 'cover_path') and os.path.exists(self.cover_path):
            cover_img = pygame.image.load(self.cover_path).convert_alpha()
            cover_img = pygame.transform.smoothscale(cover_img, (label_radius * 2, label_radius * 2))
            
            mask = pygame.Surface((label_radius * 2, label_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (label_radius, label_radius), label_radius)
            mask.blit(cover_img, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(mask, (radius - label_radius, radius - label_radius))
        else:
            pygame.draw.circle(surf, (200, 50, 50), (radius, radius), label_radius)

        pygame.draw.circle(surf, (15, 15, 25), (radius, radius), 8)
        return surf

    def load_level(self, path):
        with open(path, 'r') as file:
            data = json.load(file)
            
        self.song_path = os.path.join(MUSIC_DIR, data["song"])
        self.cover_path = os.path.join(IMG_DIR, data.get("cover", "cover.png"))
        
        self.notes = sorted(data["notes"], key=lambda x: x["time"]) 
        self.total_notes_in_level = len(self.notes) 
        self.note_index = 0
        self.active_notes = []
        
        pygame.mixer.init()
        pygame.mixer.music.load(self.song_path)
        self.song_length_ms = int(pygame.mixer.Sound(self.song_path).get_length() * 1000)

    # ==========================================
    # SISTEMAS DE EFECTOS (VFX)
    # ==========================================
    def trigger_hit_effect(self, text, color, scale, sys_time, pos, is_perfect):
        self.hit_feedback = text
        self.hit_color = color
        self.pulse_scale = scale
        self.hit_timer = sys_time
        self.glow_alpha = 255
        
        colors = PARTICLE_COLORS if is_perfect else [(255, 200, 0), (255, 100, 0)]
        for _ in range(15):
            self.particles.append({
                "x": float(pos[0]), "y": float(pos[1]),
                "vx": random.uniform(-6, 6), "vy": random.uniform(-10, -3),
                "life": 1.0, "color": random.choice(colors), "size": random.randint(3, 7)
            })

    def update_particles(self):
        surviving = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.5   
            p["life"] -= 0.04 
            if p["life"] > 0: 
                surviving.append(p)
        self.particles = surviving

    def cleanup(self):
        pygame.mixer.music.stop()
        try: pygame.mixer.music.unload()
        except AttributeError: pass
        self.notes.clear()
        self.active_notes.clear()
        self.particles.clear()

    # ==========================================
    # LÓGICA PRINCIPAL DEL JUEGO
    # ==========================================
    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        self.cleanup()
                        return "SELECTOR" 
                    if event.key == pygame.K_SPACE and not self.music_started:
                        pygame.mixer.music.play()
                        self.music_started = True

            if not self.data_queue.empty():
                mapped_x, frame_rgb = self.data_queue.get()
                self.latest_frame = frame_rgb
                if mapped_x is not None:
                    # Limitar el movimiento dentro de la pantalla
                    min_x = 0
                    max_x = self.game_w - self.catcher_width
                    self.target_x = max(min_x, min(mapped_x - self.catcher_width // 2, max_x))

            self.catcher_x_float = (ALPHA * self.target_x) + ((1.0 - ALPHA) * self.catcher_x_float)

            if self.music_started:
                if pygame.mixer.music.get_busy():
                    music_pos = pygame.mixer.music.get_pos()
                    self.update_game_logic(music_pos, current_time)
                    self.record_angle = (self.record_angle - 1) % 360
                else:
                    if not self.level_finished:
                        self.level_finished = True
                        self.level_finish_time = current_time
                    if current_time - self.level_finish_time > 5000:
                        self.cleanup()
                        return "SELECTOR"
            
            self.pulse_scale += (1.0 - self.pulse_scale) * 0.1 
            self.update_particles()
            self.draw(current_time)
            self.clock.tick(FPS)

    def update_game_logic(self, music_pos, sys_time):
        while self.note_index < len(self.notes):
            next_note = self.notes[self.note_index]
            spawn_time = next_note["time"] - FALL_TIME_MS
            
            if music_pos >= spawn_time:
                self.active_notes.append({
                    "target_time": next_note["time"],
                    "center_x": int(next_note["x"] * self.game_w),
                    "y": -self.note_height 
                })
                self.note_index += 1
            else:
                break 

        surviving_notes = []
        catcher_rect = pygame.Rect(int(self.catcher_x_float), self.catcher_y, self.catcher_width, self.catcher_height)

        for note in self.active_notes:
            progress = (music_pos - (note["target_time"] - FALL_TIME_MS)) / FALL_TIME_MS 
            note["y"] = int(-self.note_height + ((self.catcher_y + self.note_height) * progress))
            
            note_rect = pygame.Rect(note["center_x"] - (self.lane_width / 2), note["y"], self.lane_width, self.note_height)

            if catcher_rect.colliderect(note_rect):
                # Lógica Corregida: Creamos un rectángulo de la mitad inferior de la nota
                bottom_half = pygame.Rect(
                    note_rect.x, 
                    note_rect.y + (self.note_height // 2), 
                    self.lane_width, 
                    self.note_height // 2
                )
                
                # Si el recolector toca la mitad inferior, es PERFECT
                if catcher_rect.colliderect(bottom_half):
                    self.score += 100
                    self.trigger_hit_effect("PERFECT", (255, 50, 150), 1.35, sys_time, note_rect.center, True)
                else:
                    self.score += 50
                    self.trigger_hit_effect("GOOD", (0, 255, 128), 1.15, sys_time, note_rect.center, False)
                    
                self.notes_hit += 1
                continue 
            
            if note["y"] > self.game_h:
                self.trigger_hit_effect("FAIL", (255, 50, 50), 0.75, sys_time, note_rect.center, False)
                continue 

            surviving_notes.append(note)

        self.active_notes = surviving_notes

    # ==========================================
    # RENDERIZADO VISUAL EN PANTALLA
    # ==========================================
    def draw(self, sys_time):
        self.screen.blit(self.bg_surface, (0, 0))
        
        lane_surface = pygame.Surface((self.game_w, self.game_h), pygame.SRCALPHA)
        for i in range(1, self.lanes_count):
            x_line = int(i * self.lane_width)
            pygame.draw.line(lane_surface, LANE_COLOR, (x_line, 0), (x_line, self.game_h), 1)
        self.screen.blit(lane_surface, (0, 0))

        for note in self.active_notes:
            rect = pygame.Rect(note["center_x"] - (self.lane_width / 2), note["y"], self.lane_width, self.note_height)
            pygame.draw.rect(self.screen, NOTE_COLOR, rect, border_radius=8)
            pygame.draw.rect(self.screen, TEXT_COLOR, rect, width=2, border_radius=8) 

        if self.glow_alpha > 0:
            glow_surf = pygame.Surface((self.catcher_width, 150), pygame.SRCALPHA)
            for y in range(150):
                alpha = int(self.glow_alpha * (1 - (y / 150)))
                pygame.draw.line(glow_surf, (200, 150, 255, alpha), (0, y), (self.catcher_width, y))
            self.screen.blit(glow_surf, (self.catcher_x_float, self.catcher_y + self.catcher_height))
            self.glow_alpha = max(0, self.glow_alpha - 15)

        catcher = pygame.Rect(int(self.catcher_x_float), self.catcher_y, self.catcher_width, self.catcher_height)
        pygame.draw.rect(self.screen, CATCHER_COLOR, catcher, border_radius=10)
        
        for p in self.particles:
            c = p["color"]
            color_fade = (int(c[0]*p["life"]), int(c[1]*p["life"]), int(c[2]*p["life"]))
            pygame.draw.circle(self.screen, color_fade, (int(p["x"]), int(p["y"])), p["size"])
        
        if self.latest_frame is not None:
            frame_surf = pygame.transform.scale(pygame.surfarray.make_surface(self.latest_frame.swapaxes(0, 1)), (self.right_panel_w, self.cam_h))
            self.screen.blit(frame_surf, (self.game_w, 0))
            
        pygame.draw.rect(self.screen, PANEL_COLOR_UI, (self.game_w, self.cam_h, self.right_panel_w, self.info_h))
        pygame.draw.line(self.screen, GRADIENT_BOTTOM, (self.game_w, 0), (self.game_w, self.screen_height), 4)

        self.draw_hud(sys_time)

        if not self.music_started:
            self.draw_overlay_message("Presiona ESPACIO para comenzar", 30)
        elif self.level_finished:
            self.draw_level_finished()

        pygame.display.flip()

    def draw_hud(self, sys_time):
        # Barra de progreso
        bar_w, bar_h = int(self.right_panel_w * 0.80), 10
        bar_x, bar_y = self.game_w + (self.right_panel_w // 2) - (bar_w // 2), self.cam_h + 30
        pygame.draw.rect(self.screen, (40, 30, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        
        if self.music_started and self.song_length_ms > 0:
            song_progress = min(max(pygame.mixer.music.get_pos() / self.song_length_ms, 0), 1)
            if song_progress > 0:
                pygame.draw.rect(self.screen, (240, 240, 255), (bar_x, bar_y, int(bar_w * song_progress), bar_h), border_radius=5)

        # Tocadiscos (Cristal)
        glass_w = self.record_surface.get_width() + 50
        glass_x = self.game_w + int(self.right_panel_w * 0.30) - (glass_w // 2)
        glass_y = bar_y + 40 
        
        glass_surf = pygame.Surface((glass_w, glass_w), pygame.SRCALPHA)
        pygame.draw.rect(glass_surf, GLASS_BG, glass_surf.get_rect(), border_radius=20) 
        pygame.draw.polygon(glass_surf, (255, 255, 255, 25), [(0, 0), (glass_w*0.6, 0), (0, glass_w*0.6)])
        pygame.draw.rect(glass_surf, GLASS_HIGHLIGHT, glass_surf.get_rect(), width=1, border_radius=20) 
        self.screen.blit(glass_surf, (glass_x, glass_y))

        rotated = pygame.transform.rotate(self.record_surface, self.record_angle)
        rect = rotated.get_rect(center=(glass_x + glass_w//2, glass_y + glass_w//2))
        self.screen.blit(rotated, rect.topleft)

        # Feedback Text y Logo
        text_center_x = self.game_w + int(self.right_panel_w * 0.77)
        if sys_time - self.hit_timer < 600: 
            feed_surf = self.get_font(35).render(self.hit_feedback, True, self.hit_color)
            feed_w, feed_h = int(feed_surf.get_width() * self.pulse_scale), int(feed_surf.get_height() * self.pulse_scale)
            scaled_feed = pygame.transform.smoothscale(feed_surf, (feed_w, feed_h))
            self.screen.blit(scaled_feed, scaled_feed.get_rect(center=(text_center_x, glass_y + 30)))

        if self.niot_logo:
            w, h = int(self.niot_logo.get_width() * self.pulse_scale), int(self.niot_logo.get_height() * self.pulse_scale)
            logo = pygame.transform.smoothscale(self.niot_logo, (w, h))
            self.screen.blit(logo, logo.get_rect(center=(text_center_x - 10, glass_y + 110)))

        # Puntaje Final
        score_t = self.get_font(36).render(f"PUNTOS: {self.score}", True, TEXT_COLOR)
        notes_c = (150, 255, 200) if self.notes_hit == self.total_notes_in_level and self.notes_hit > 0 else (200, 190, 220)
        notes_t = self.get_font(24).render(f"NOTAS: {self.notes_hit}/{self.total_notes_in_level}", True, notes_c)
        
        self.screen.blit(score_t, (glass_x, self.screen_height - 140))
        self.screen.blit(notes_t, (glass_x, self.screen_height - 80))

        # ANIMACIÓN DEL GIF
        self.dance_gif.update(sys_time) 
        gif_surface = self.dance_gif.get_surface()
        if gif_surface:
            target_w = int(self.right_panel_w * 0.43)
            aspect_ratio = gif_surface.get_height() / gif_surface.get_width()
            target_h = int(target_w * aspect_ratio)
            
            gif_img = pygame.transform.smoothscale(gif_surface, (target_w, target_h))
            self.screen.blit(gif_img, (self.screen_width - target_w, self.screen_height - target_h))

    def draw_overlay_message(self, message, font_size):
        overlay = pygame.Surface((self.game_w, 60), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 100), overlay.get_rect())
        self.screen.blit(overlay, (0, (self.game_h // 2) - 30))
        
        text = self.get_font(font_size).render(message, True, TEXT_COLOR)
        self.screen.blit(text, text.get_rect(center=(self.game_w // 2, self.game_h // 2)))

    def draw_level_finished(self):
        overlay = pygame.Surface((self.game_w, self.game_h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        title = self.get_font(50).render("NIVEL COMPLETADO", True, (100, 255, 150))
        self.screen.blit(title, title.get_rect(center=(self.game_w // 2, self.game_h // 2 - 20)))
        
        sub = self.get_font(25).render("Volviendo al selector...", True, TEXT_COLOR)
        self.screen.blit(sub, sub.get_rect(center=(self.game_w // 2, self.game_h // 2 + 30)))