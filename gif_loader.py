import pygame
from PIL import Image

class AnimatedGif:
    def __init__(self, filepath, speed_multiplier=1.0):
        self.frames = []
        self.durations = [] # Ahora guardamos la duración individual de cada frame
        self.current_frame = 0
        self.last_update = 0
        self.speed_multiplier = speed_multiplier

        try:
            pil_image = Image.open(filepath)
            
            for frame in range(pil_image.n_frames):
                pil_image.seek(frame)
                
                # Obtener la duración específica de este fotograma (por defecto 100ms si no existe)
                frame_duration = pil_image.info.get('duration', 100)
                
                # Algunos GIFs tienen un error de codificación con duración 0, lo evitamos:
                if frame_duration == 0:
                    frame_duration = 100
                
                # Ajustamos el tiempo según el multiplicador de velocidad
                adjusted_duration = int(frame_duration / self.speed_multiplier)
                
                # Convertir la imagen para PyGame
                frame_rgba = pil_image.convert("RGBA")
                pygame_image = pygame.image.frombytes(
                    frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode
                )
                
                self.frames.append(pygame_image)
                self.durations.append(adjusted_duration)
                
        except Exception as e:
            print(f"Error cargando GIF en {filepath}: {e}")

    def update(self, current_time):
        if not self.frames:
            return
        
        # Leer el retraso exacto que corresponde al fotograma que estamos viendo ahora
        current_delay = self.durations[self.current_frame]
        
        if current_time - self.last_update > current_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_surface(self):
        if not self.frames:
            return None
        return self.frames[self.current_frame]