import threading
import queue
import pygame
import sys
from tracker import run_tracker
from game import RhythmGame
from menu import MainMenu
from level_selector import LevelSelector

if __name__ == "__main__":
    pygame.init()
    screen_info = pygame.display.Info()
    
    # --- OPTIMIZACIÓN CRÍTICA: Hilo de cámara global ---
    # Arrancamos OpenCV una sola vez para evitar saturación de RAM
    game_active_width = int(screen_info.current_w * 0.60)
    data_queue = queue.Queue(maxsize=1)

    tracker_thread = threading.Thread(
        target=run_tracker, 
        args=(data_queue, game_active_width), 
        daemon=True
    )
    tracker_thread.start()
    
    while True: # Bucle del Menú Principal
        menu = MainMenu(screen_info)
        action = menu.run()
        
        if action == "QUIT" or action is None:
            pygame.quit()
            sys.exit()
            
        elif action == "PLAY":
            # --- NUEVO: Bucle interno para el Selector de Niveles ---
            while True: 
                selector = LevelSelector(screen_info)
                selected_level_json = selector.run()
                
                if selected_level_json is None:
                    break # Presionó ESCAPE, rompe el bucle y vuelve al Menú Principal
                    
                # Vaciar basura vieja de la cámara antes de jugar
                while not data_queue.empty():
                    try: data_queue.get_nowait()
                    except: pass
                        
                # Iniciar el nivel
                game = RhythmGame(data_queue, screen_info, selected_level_json) 
                game_result = game.run()
                
                # Si el juego termina (por victoria o por salir), el bucle repite el Selector
                if game_result == "SELECTOR":
                    continue