class ChessColors(dict):
    """
    A custom dictionary class for chess.svg.board() that allows using arbitrary arrow colors
    while maintaining the default chess.svg color behavior for other elements.
    
    Usage:
        colors = ChessColors({
            "square light": "#custom-color",  # Override default colors as needed
        })
        board_svg = chess.svg.board(board, arrows=[Arrow(E2, E4, color="#ff000080")], colors=colors)
    """
    
    DEFAULT_COLORS = {
        "square light": "#ffce9e",
        "square dark": "#d18b47",
        "square dark lastmove": "#aaa23b",
        "square light lastmove": "#cdd16a",
        "margin": "#212121",
        "inner border": "#111",
        "outer border": "#111",
        "coord": "#e5e5e5",
        "arrow green": "#15781B80",
        "arrow red": "#88202080",
        "arrow yellow": "#e68f00b3",
        "arrow blue": "#00308880",
    }
    
    def __contains__(self, key):
        # Check if it's a custom arrow color
        if key.startswith("arrow "):
            _, color = key.split(" ", 1)
            if color.startswith("#"):
                return True
        
        # Check our custom overrides
        if super().__contains__(key):
            return True
            
        # Check default colors
        return key in self.DEFAULT_COLORS
    
    def __getitem__(self, key):
        # If the key starts with "arrow " and contains a color code
        if key.startswith("arrow "):
            _, color = key.split(" ", 1)
            # If it looks like a color code (starts with #), return it directly
            if color.startswith("#"):
                return color
            
        # For all other cases, fall back to standard dictionary behavior
        # First check if we have a custom value
        if super().__contains__(key):
            return super().__getitem__(key)
            
        # Then check default colors
        if key in self.DEFAULT_COLORS:
            return self.DEFAULT_COLORS[key]
            
        raise KeyError(key)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default