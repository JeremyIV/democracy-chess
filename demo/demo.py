import chess
import chess.engine
import chess.svg
import pygame
import cairosvg
import io
from PIL import Image
import sys

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Chess vs Stockfish")

# Initialize chess board and stockfish
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")

def render_board():
    """Convert chess.svg board to pygame surface and display it"""
    # Generate SVG
    svg_data = chess.svg.board(board=board).encode('UTF-8')
    
    # Convert SVG to PNG using cairosvg
    png_data = cairosvg.svg2png(bytestring=svg_data)
    
    # Convert to pygame surface
    image = Image.open(io.BytesIO(png_data))
    py_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    py_image = pygame.transform.scale(py_image, (800, 800))
    
    # Display
    screen.fill((255, 255, 255))
    screen.blit(py_image, (0, 0))
    pygame.display.flip()

def get_user_input():
    """Get user input while keeping pygame window responsive"""
    input_str = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.quit()
                pygame.quit()
                sys.exit()
            
        # Use sys.stdin to check for input without blocking
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            return line.strip()
            
        pygame.time.wait(100)  # Short sleep to prevent high CPU usage

try:
    import select  # Add this at the top with other imports
    
    while not board.is_game_over():
        # Render current board state
        render_board()
        
        # Get player move
        print("Enter your move (e.g., 'e2e4'): ", end='', flush=True)
        move_str = get_user_input()
        
        try:
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                board.push(move)
                render_board()
                
                # Let Stockfish play
                result = engine.play(board, chess.engine.Limit(time=2.0))
                board.push(result.move)
                print(f"Stockfish played: {result.move}")
            else:
                print("Illegal move!")
        except ValueError:
            print("Invalid move format! Use format like 'e2e4'")

    # Game over
    print("Game Over!")
    print(f"Result: {board.outcome().result()}")
    
finally:
    # Clean up
    engine.quit()
    pygame.quit()