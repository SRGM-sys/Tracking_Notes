import os

# ==========================================
# 1. RUTAS Y DIRECTORIOS
# ==========================================
BASE_DIR = "assets"
MUSIC_DIR = os.path.join(BASE_DIR, "music")
IMG_DIR = os.path.join(BASE_DIR, "img")
LEVELS_DIR = os.path.join(BASE_DIR, "levels")
FONT_DIR = os.path.join(BASE_DIR, "font")

# ==========================================
# 2. CONFIGURACIÓN GENERAL DEL SISTEMA
# ==========================================
FPS = 60

# ==========================================
# 3. PALETA DE COLORES Y ESTÉTICA
# ==========================================
# Fondos
GRADIENT_TOP = (70, 30, 100)          
GRADIENT_MID = (40, 15, 60)            
GRADIENT_BOTTOM = (15, 5, 25) 

# Interfaz General
PANEL_COLOR_UI = (15, 10, 30)         
PANEL_BG = (10, 5, 20, 180)           
TEXT_COLOR = (255, 255, 255)          

# Menú Principal
TITLE_COLOR = (255, 255, 255)
TITLE_SHADOW = (45, 15, 65)
BUTTON_COLOR = (255, 255, 255, 20)      
BUTTON_HOVER = (255, 255, 255, 50)      
BUTTON_BORDER = (255, 255, 255, 120)

# Efectos de Cristal 
GLASS_BG = (255, 255, 255, 12)
GLASS_HIGHLIGHT = (255, 255, 255, 180)
GLASS_SHADOW = (0, 0, 0, 80)

# Elementos Interactivos (Gameplay)
CATCHER_COLOR = (0, 255, 128)         
NOTE_COLOR = (255, 50, 150)           
LANE_COLOR = (255, 255, 255, 30)      
PARTICLE_COLORS = [(0, 255, 128), (255, 50, 150), (255, 255, 255)]

# ==========================================
# 4. FÍSICAS Y MECÁNICAS
# ==========================================
ALPHA = 0.15           # Suavizado de la cámara (Tracking)
FALL_TIME_MS = 1200    # Tiempo en milisegundos que tarda la nota en caer