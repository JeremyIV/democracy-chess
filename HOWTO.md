# How to Play Democracy Chess

Democracy Chess is a collaborative chess game where Twitch chat plays against a chess engine. Every 30 seconds, all votes are tallied and the most popular legal move is played.

## How to Vote

First, check the title of the chess window in the stream. It will show which voting system is currently being used:

```
Democracy Chess - [VOTING_METHOD] Voting (Difficulty [LEVEL])
```

### Voting Methods

#### First Past The Post (FPTP)
In FPTP voting, simply type a single chess move in chat. The move with the most votes wins.

- Format: Type one move (e.g., "e4" or "Nf3")
- Example: `e4`
- Example: `Nf3`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Approval Voting (APPROVAL)
In approval voting, you can vote for multiple moves you approve of. Each approved move gets one vote, and the move with the most total votes wins.

- Format: Type multiple moves separated by spaces or commas
- Example: `e4 d4 Nf3`
- Example: `e4, d4, Nf3`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Instant Runoff (RUNOFF)
In instant runoff voting, rank your preferred moves in order. If no move has a majority, the move with the fewest votes is eliminated and those votes transfer to their next choices.

- Format: Type moves in order of preference, separated by spaces or commas
- Example: `e4 d4 Nf3` (where e4 is first choice, d4 second, Nf3 third)
- Example: `e4, d4, Nf3`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Quadratic Voting (QUADRATIC)
In quadratic voting, you can assign different weights to your preferred moves. The more weight you put on a move, the more strongly you support it.

- Format: Type moves followed by optional numbers for weights
- Example: `e4 5 d4 3 Nf3 1` (strongly prefer e4, moderately prefer d4, slightly prefer Nf3)
- Example: `e4 10 Nf3 2` (very strongly prefer e4 over Nf3)
- If you don't specify a number after a move, it defaults to weight 1
- Your weights will be automatically normalized along with everyone else's votes
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

## Move Notation

You can write moves in either:

### Standard Algebraic Notation (SAN)
- Just write the piece and its destination: `Nf3`
- Pawns don't need a letter: `e4`
- Captures use 'x': `Nxe4` or `exd5`
- Castling is written as `O-O` (kingside) or `O-O-O` (queenside)
- Add `+` for check: `Nf3+`
- Add `#` for checkmate: `Qh7#`

### UCI Notation (Universal Chess Interface)
- Moves are written as the starting square followed by the ending square
- Example: `e2e4` means move from e2 to e4
- For pawn promotion, add the promotion piece: `e7e8q` promotes to queen
- Castling is written as the king's movement:
  - Kingside castle: `e1g1` (white) or `e8g8` (black)
  - Queenside castle: `e1c1` (white) or `e8c8` (black)

## Examples

Here are some example scenarios:

1. **FPTP Voting Example:**
```
User1: e4
User2: d4
User3: e4
Result: e4 wins with 2 votes
```

2. **Approval Voting Example:**
```
User1: e4 d4
User2: d4 Nf3
User3: e4 Nf3
Result: All moves get 2 votes, tie is broken randomly
```

3. **Instant Runoff Example:**
```
User1: e4 d4 Nf3
User2: d4 Nf3 e4
User3: Nf3 e4 d4
First round: No majority
Nf3 eliminated, User3's vote moves to e4
Result: e4 wins with 2 votes
```

4. **Quadratic Voting Example:**
```
User1: e4 2 d4 1  (prefers e4)
User2: d4       (strongly supports d4)
User3: e4 4 Nf3 1 (strongly prefers e4, slight support for Nf3)
Result: votes are normalized and e4 wins with the highest weighted support
```

## Tips
- Your most recent vote always replaces your previous votes
- Invalid moves are ignored, but the rest of your vote still counts
- The vote tally happens every 30 seconds
- Watch the stream title to know which voting system is being used
- The chess engine will respond a few seconds after the chat's move is played