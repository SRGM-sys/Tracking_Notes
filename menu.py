import pygame
import sys
import os
import random

from config import *

class MainMenu:
    def __init__(self, screen_info):
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Tracking Notes")
        self.clock = pygame.time.Clock()
        
        self.bg_surface = self.create_gradient_bg()
        
        self.title_font = self.get_font(100) 
        self.btn_font = self.get_font(45) 
        self.small_font = self.get_font(18) 
        
        btn_w, btn_h = 380, 95
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        self.play_rect = pygame.Rect(center_x - btn_w // 2, center_y - 25, btn_w, btn_h)
        self.exit_rect = pygame.Rect(center_x - btn_w // 2, center_y + 100, btn_w, btn_h)
        
        self.niot_logo = self.load_logo("niot.png", target_h=150)
        self.espol_logo = self.load_logo("espol.png", target_h=75)

        self.particles = []
        self.init_particles(90)
        
        self.num_bars = 8 
        self.eq_heights_left = [50] * self.num_bars
        self.eq_targets_left = [50] * self.num_bars
        self.eq_heights_right = [50] * self.num_bars
        self.eq_targets_right = [50] * self.num_bars

    def get_font(self, size):
        font_path = os.path.join(FONT_DIR, "pixel.ttf")
        return pygame.font.Font(font_path, size) if os.path.exists(font_path) else pygame.font.Font(None, size)

    def load_logo(self, filename, target_h):
        path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(path): return None
        
        img = pygame.image.load(path).convert_alpha()
        aspect = img.get_width() / img.get_height()
        return pygame.transform.smoothscale(img, (int(target_h * aspect), target_h))

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
                "x": random.uniform(0, self.screen_width),
                "y": random.uniform(0, self.screen_height),
                "vx": 0, "vy": random.uniform(2.0, 5.0) + (size * 0.2), 
                "size": size,
                "color": random.choice(PARTICLE_COLORS), 
                "alpha": random.randint(80, 200) 
            })

    def update_and_draw_particles(self):
        particle_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] > self.screen_height + 10:
                p["y"] = -10
                p["x"] = random.uniform(0, self.screen_width)
            
            color_with_alpha = (p["color"][0], p["color"][1], p["color"][2], p["alpha"])
            rect = pygame.Rect(int(p["x"]), int(p["y"]), p["size"], int(p["size"] * 1.5))
            pygame.draw.ellipse(particle_surf, color_with_alpha, rect)
            
        self.screen.blit(particle_surf, (0, 0))

    def draw_equalizer(self):
        eq_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        bar_width, gap, max_h = 15, 10, 250
        base_y = self.screen_height // 2 + 100
        
        for i in range(self.num_bars):
            if random.random() < 0.1:
                self.eq_targets_left[i] = random.randint(20, max_h)
                self.eq_targets_right[i] = random.randint(20, max_h)
                
            self.eq_heights_left[i] += (self.eq_targets_left[i] - self.eq_heights_left[i]) * 0.15
            self.eq_heights_right[i] += (self.eq_targets_right[i] - self.eq_heights_right[i]) * 0.15
            
            x_left = 50 + (i * (bar_width + gap))
            pygame.draw.rect(eq_surf, (255, 255, 255, 30), (x_left, base_y - self.eq_heights_left[i], bar_width, self.eq_heights_left[i]), border_radius=5)
            
            x_right = self.screen_width - 50 - ((self.num_bars - i) * (bar_width + gap))
            pygame.draw.rect(eq_surf, (255, 255, 255, 30), (x_right, base_y - self.eq_heights_right[i], bar_width, self.eq_heights_right[i]), border_radius=5)
            
        self.screen.blit(eq_surf, (0, 0))

    def draw_button(self, rect, text, is_hovered):
        btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
        
        pygame.draw.rect(btn_surf, color, btn_surf.get_rect(), border_radius=15)
        pygame.draw.rect(btn_surf, BUTTON_BORDER, btn_surf.get_rect(), width=2, border_radius=15)
        self.screen.blit(btn_surf, rect.topleft)
        
        text_surf = self.btn_font.render(text, True, TEXT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def draw_text_with_offset_shadow(self, text, font, text_color, shadow_color, center_pos, offset=5):
        title_surf = font.render(text, True, text_color)
        title_rect = title_surf.get_rect(center=center_pos)
        
        shadow_surf = font.render(text, True, shadow_color)
        for i in range(1, offset + 1):
            self.screen.blit(shadow_surf, (title_rect.x + i, title_rect.y + i))
                
        self.screen.blit(title_surf, title_rect)

    def run(self):
        pygame.mixer.init()
        song_path = os.path.join(MUSIC_DIR, "MenuSong.wav")
        if os.path.exists(song_path):
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(-1) 

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            play_hover = self.play_rect.collidepoint(mouse_pos)
            exit_hover = self.exit_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.mixer.music.stop()
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    if play_hover:
                        pygame.mixer.music.stop()
                        return "PLAY"
                    if exit_hover:
                        pygame.mixer.music.stop()
                        return "QUIT"

            self.screen.blit(self.bg_surface, (0, 0))
            self.update_and_draw_particles()
            self.draw_equalizer()
            
            self.draw_text_with_offset_shadow(
                text="TRACKING NOTES", font=self.title_font, text_color=TITLE_COLOR, 
                shadow_color=TITLE_SHADOW, center_pos=(self.screen_width // 2, self.screen_height * 0.25), offset=6 
            )
            
            self.draw_button(self.play_rect, "PLAY", play_hover)
            self.draw_button(self.exit_rect, "EXIT", exit_hover)
            
            bottom_y = self.screen_height - 100
            if self.niot_logo and self.espol_logo:
                self.screen.blit(self.niot_logo, self.niot_logo.get_rect(center=(self.screen_width * 0.38, bottom_y)))
                self.screen.blit(self.espol_logo, self.espol_logo.get_rect(center=(self.screen_width * 0.62, bottom_y)))
                
            version_surf = self.small_font.render("v1.0 Alpha", True, (150, 150, 160))
            engine_surf = self.small_font.render("Powered by OpenCV & MediaPipe", True, (150, 150, 160))
            self.screen.blit(version_surf, (20, self.screen_height - 30))
            self.screen.blit(engine_surf, engine_surf.get_rect(topright=(self.screen_width - 20, self.screen_height - 30)))
            
            pygame.display.flip()
            self.clock.tick(FPS)