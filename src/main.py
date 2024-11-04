import argparse
import chess
import chess.engine
import chess.svg
import pygame
import cairosvg
import io
from PIL import Image
import time
import sys
from typing import Union

# Import our modules
from twitch import create_twitch_chat
from voting.fptp import FPTPVoteParser
from mock_twitch import MockTwitchChat
from mock_stockfish import MockStockfish

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Democracy Chess - Chess played by Twitch chat')
    parser.add_argument('--mock', action='store_true', help='Use mock implementations instead of real APIs')
    parser.add_argument('--mock-chat-path', default='mock/chat.csv', help='Path to mock chat CSV file')
    parser.add_argument('--mock-stockfish-path', default='mock/stockfish.csv', help='Path to mock Stockfish CSV file')
    parser.add_argument('--vote-time', type=int, default=30, help='Seconds to wait for votes')
    args = parser.parse_args()

    # Initialize pygame for display
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Democracy Chess")

    # Initialize chess board
    board = chess.Board()

    # Initialize either mock or real components
    if args.mock:
        twitch_chat = MockTwitchChat(args.mock_chat_path)
        engine = MockStockfish(args.mock_stockfish_path)
    else:
        # For real games, we'll use actual Stockfish and Twitch
        twitch_chat = create_twitch_chat()
        engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")

    # Initialize vote parser
    vote_parser = FPTPVoteParser(board)

    def render_board():
        """Convert chess.svg board to pygame surface and display it"""
        svg_data = chess.svg.board(board=board).encode('UTF-8')
        png_data = cairosvg.svg2png(bytestring=svg_data)
        image = Image.open(io.BytesIO(png_data))
        py_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        py_image = pygame.transform.scale(py_image, (800, 800))
        screen.fill((255, 255, 255))
        screen.blit(py_image, (0, 0))
        pygame.display.flip()

    try:
        while not board.is_game_over():
            # Display current board state
            render_board()

            print(f"\nWaiting {args.vote_time} seconds for votes...")
            vote_start_time = time.time()

            # Keep processing events while waiting for votes
            while time.time() - vote_start_time < args.vote_time:
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                
                # Update display to keep window responsive
                pygame.display.flip()
                time.sleep(0.1)  # Short sleep to prevent high CPU usage

            # Get chat messages from the voting period
            chat_messages = twitch_chat.get_chat()
            
            if not chat_messages:
                print("No votes received in this period, continuing...")
                continue

            try:
                # Parse votes and get winning move
                winning_move = vote_parser.get_winning_move(chat_messages)
                
                # Print voting results
                print(f"\nVotes received from {len(chat_messages)} users")
                print(f"Winning move: {winning_move.uci()}")

                # Make the winning move
                board.push(winning_move)
                render_board()

                # Get and make Stockfish's move
                result = engine.play(board, chess.engine.Limit(time=2.0))
                board.push(result.move)
                print(f"Stockfish played: {result.move.uci()}")

            except ValueError as e:
                print(f"Error processing votes: {e}")
                continue

        # Game is over
        render_board()
        print("\nGame Over!")
        print(f"Result: {board.outcome().result()}")

    except KeyboardInterrupt:
        print("\nGame terminated by user")
    finally:
        # Clean up
        engine.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()