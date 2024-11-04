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
from typing import Union, Optional, Literal

# Import our modules
from twitch import create_twitch_chat
from voting.fptp import FPTPVoteParser
from voting.approval import ApprovalVoteParser
from voting.runoff import InstantRunoffVoteParser
from mock_twitch import MockTwitchChat
from mock_stockfish import MockStockfish
from game_logger import GameLogger
from stockfish_wrapper import create_engine, DIFFICULTY_LEVELS

# Define valid voting methods
VOTING_METHODS = {
    'fptp': FPTPVoteParser,
    'approval': ApprovalVoteParser,
    'runoff': InstantRunoffVoteParser
}

VotingMethod = Literal['fptp', 'approval', 'runoff']

def play_game(
    screen: pygame.Surface,
    mock: bool,
    mock_chat_path: str,
    mock_stockfish_path: str,
    vote_time: int,
    log_dir: str,
    difficulty: int,
    game_number: int,
    voting_method: VotingMethod
) -> None:
    """
    Play a single game of Democracy Chess.
    
    Args:
        screen: Pygame surface to render the game on
        mock: Whether to use mock implementations
        mock_chat_path: Path to mock chat CSV file
        mock_stockfish_path: Path to mock Stockfish CSV file
        vote_time: Seconds to wait for votes
        log_dir: Directory to store game logs
        difficulty: Stockfish difficulty level (1-15)
        game_number: The sequential number of this game
        voting_method: Which voting method to use ('fptp', 'approval', or 'runoff')
    """
    # Initialize logger
    logger = GameLogger(log_dir, game_number, voting_method, difficulty)

    # Initialize chess board
    board = chess.Board()

    # Initialize either mock or real components
    if mock:
        twitch_chat = MockTwitchChat(mock_chat_path)
    else:
        twitch_chat = create_twitch_chat()

    engine = create_engine(mock, mock_stockfish_path, difficulty)

    # Initialize vote parser based on selected method
    VoteParserClass = VOTING_METHODS[voting_method]
    vote_parser = VoteParserClass(board)

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
        print(f"\nStarting game {game_number} with {voting_method.upper()} voting")
        
        while not board.is_game_over():
            render_board()

            print(f"\nGame {game_number}, Turn {turn_number} - Waiting {vote_time} seconds for votes...")
            print(f"Voting method: {voting_method.upper()}")
            vote_start_time = time.time()

            while time.time() - vote_start_time < vote_time:
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

    finally:
        engine.quit()

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
    parser.add_argument('--voting-method', 
                    choices=list(VOTING_METHODS.keys()),
                    default='fptp',
                    help='Voting method to use (default: fptp)')
    args = parser.parse_args()

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption(f"Democracy Chess - {args.voting_method.upper()} Voting")

    try:
        game_number = 1
        while True:
            try:
                play_game(
                    screen=screen,
                    mock=args.mock,
                    mock_chat_path=args.mock_chat_path,
                    mock_stockfish_path=args.mock_stockfish_path,
                    vote_time=args.vote_time,
                    log_dir=args.log_dir,
                    difficulty=args.difficulty,
                    game_number=game_number,
                    voting_method=args.voting_method
                )
                game_number += 1
                print(f"\nStarting game {game_number}...")
                time.sleep(5)  # Brief pause between games
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error during game {game_number}: {e}")
                print("Starting new game...")
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()