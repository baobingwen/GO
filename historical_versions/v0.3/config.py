from pathlib import Path

class Config:
    COLORS = {
        "black": (0,0,0),
        "white": (255,255,255),
        "gray": (128,128,128),
        "board": (221,182,116)
    }
    
    SIZE = {
        "dimension_init": 19,
        "edge_grid": 36,
        "border": 24,
    }
    
    IMAGE_DIR = Path('./images')
    IMAGE_PATHS = {
        "black_stone": IMAGE_DIR / "blackStone.png",
        "white_stone": IMAGE_DIR / "whiteStone.png",
        
        "icon": IMAGE_DIR / "icon.ico"
    }