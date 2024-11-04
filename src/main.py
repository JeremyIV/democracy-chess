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
from game_logger import GameLogger
from stockfish_wrapper import create_engine, DIFFICULTY_LEVELS

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Democracy Chess - Chess played by Twitch chat')
    parser.add_argument('--mock', action='store_true', help='Use mock implementations instead of real APIs')
    parser.add_argument('--mock-chat-path', default='mock/chat.csv', help='Path to mock chat CSV file')
    parser.add_argument('--mock-stockfish-path', default='mock/stockfish.csv', help='Path to mock Stockfish CSV file')
    parser.add_argument('--vote-time', type=int, default=30, help='Seconds to wait for votes')
    parser.add_argument('--log-dir', default='logs', help='Directory to store game logs')
    parser.add_argument('--difficulty', type=int, choices=range(1, len(DIFFICULTY_LEVELS) + 1),
                    default=5, help='Stockfish difficulty level (1-15)')
    args = parser.parse_args()

    # Initialize logger
    logger = GameLogger(args.log_dir)

    # Initialize pygame for display
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Democracy Chess")

    # Initialize chess board
    board = chess.Board()

    # Initialize either mock or real components
    if args.mock:
        twitch_chat = MockTwitchChat(args.mock_chat_path)
    else:
        twitch_chat = create_twitch_chat()

    engine = create_engine(args.mock, args.mock_stockfish_path, args.difficulty)

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
        turn_number = 1
        while not board.is_game_over():
            render_board()

            print(f"\nTurn {turn_number} - Waiting {args.vote_time} seconds for votes...")
            vote_start_time = time.time()

            while time.time() - vote_start_time < args.vote_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                pygame.display.flip()
                time.sleep(0.1)

            chat_messages = twitch_chat.get_chat()
            
            if not chat_messages:
                print("No votes received in this period, continuing...")
                continue

            try:
                winning_move = vote_parser.get_winning_move(chat_messages)
                print(f"\nVotes received from {len(chat_messages)} users")
                print(f"Winning move: {winning_move.uci()}")

                # Make Twitch's move
                board.push(winning_move)
                render_board()

                # Get and make Stockfish's move
                result = engine.play(board, chess.engine.Limit(time=2.0))
                board.push(result.move)
                print(f"Stockfish played: {result.move.uci()}")

                # Log the complete turn
                logger.log_turn(
                    turn_number=turn_number,
                    chat_messages=chat_messages,
                    twitch_move=winning_move.uci(),
                    stockfish_move=result.move.uci()
                )
                turn_number += 1

            except ValueError as e:
                print(f"Error processing votes: {e}")
                continue

        # Game is over
        render_board()
        outcome = board.outcome()
        logger.log_outcome(outcome)
        
        print("\nGame Over!")
        winner = "Twitch" if outcome.winner else "Stockfish" if outcome.winner is False else "Draw"
        print(f"Winner: {winner}")
        print(f"Termination: {outcome.termination.name}")
        print(f"Game log saved to: {logger.log_file}")

    except KeyboardInterrupt:
        print("\nGame terminated by user")
    finally:
        engine.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()