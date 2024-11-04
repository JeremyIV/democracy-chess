# 🏛️ Democracy Chess ♟️

🏛️ Democracy Chess ♟️ is a Twitch integration that lets chat play chess against Stockfish by voting on moves. Every 30 seconds, the chat's votes are tallied and the most popular legal move is played.

## Setup

### Prerequisites
- Python 3.11 or higher
- Ubuntu (other platforms may work but are untested)
- Stockfish chess engine
- A Twitch account and OAuth token

### Installation

1. Install system dependencies:
```bash
sudo apt update
sudo apt install stockfish python3-pip