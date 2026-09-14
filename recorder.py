import pygame
import json
import os
import sys

# Importamos las rutas centrales
from config import MUSIC_DIR, LEVELS_DIR

# Configuración de nivel a grabar
SONG_NAME = "South.wav"
SONG_PATH = os.path.join(MUSIC_DIR, SONG_NAME)
OUTPUT_PATH = os.path.join(LEVELS_DIR, "nivel7.json")

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("NIoT Ritmo - Grabador de Niveles")
    font = pygame.font.Font(None, 36)

    # Validamos que los directorios principales existan
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(LEVELS_DIR, exist_ok=True)

    if not os.path.exists(SONG_PATH):
        print(f"Error: Coloca un archivo de música llamado '{SONG_NAME}' en la carpeta '{MUSIC_DIR}'")
        sys.exit()

    pygame.mixer.music.load(SONG_PATH)
    
    notes = []
    recording = False
    running = True

    # Mapeo de 6 carriles (~16.66% del ancho total por cada uno)
    key_mapping = {
        pygame.K_1: 0.083, pygame.K_2: 0.250, pygame.K_3: 0.416, 
        pygame.K_4: 0.583, pygame.K_5: 0.750, pygame.K_6: 0.916
    }

    while running:
        screen.fill((20, 20, 30))
        
        if not recording:
            text = font.render("Presiona ESPACIO para grabar (Teclas 1-6)", True, (255, 255, 255))
        else:
            time_ms = pygame.mixer.music.get_pos()
            text = font.render(f"Grabando... Tiempo: {time_ms} ms", True, (0, 255, 128))
            
        screen.blit(text, (30, 180))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not recording:
                    recording = True
                    pygame.mixer.music.play()
                    print("Grabación iniciada...")
                
                elif recording and event.key in key_mapping:
                    current_time = pygame.mixer.music.get_pos()
                    x_position = key_mapping[event.key]
                    
                    notes.append({
                        "time": current_time,
                        "x": x_position
                    })
                    print(f"Carril {event.unicode} registrado: {current_time} ms | X: {x_position}")

        if recording and not pygame.mixer.music.get_busy():
            running = False

    # Guardar la estructura en JSON (con metadatos para el selector)
    level_data = {
        "title": "Nuevo Nivel",
        "artist": "Artista Desconocido",
        "preview_start": 0.0, 
        "preview_end": 10.0,
        "song": SONG_NAME,
        "cover": "cover.png",
        "lanes": 6,
        "notes": notes
    }
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(level_data, f, indent=4)
        
    print(f"\n¡Grabación finalizada! Nivel guardado en {OUTPUT_PATH}")
    pygame.quit()

if __name__ == "__main__":
    main()