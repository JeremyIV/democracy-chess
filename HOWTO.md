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

- Format: Type one move in UCI notation (e.g., "e2e4" means move from e2 to e4)
- Example: `e2e4`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Approval Voting (APPROVAL)
In approval voting, you can vote for multiple moves you approve of. Each approved move gets one vote, and the move with the most total votes wins.

- Format: Type multiple moves separated by spaces or commas
- Example: `e2e4 d2d4 g1f3`
- Example: `e2e4, d2d4, g1f3`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Instant Runoff (RUNOFF)
In instant runoff voting, rank your preferred moves in order. If no move has a majority, the move with the fewest votes is eliminated and those votes transfer to their next choices.

- Format: Type moves in order of preference, separated by spaces or commas
- Example: `e2e4 d2d4 g1f3` (where e2e4 is first choice, d2d4 second, g1f3 third)
- Example: `e2e4, d2d4, g1f3`
- If you vote multiple times, only your last vote counts
- Invalid moves are ignored

#### Quadratic Voting (QUADRATIC)
In quadratic voting, you get 100 voting credits. The cost of votes is squared (1 vote = 1 credit, 2 votes = 4 credits, 3 votes = 9 credits, etc).

- Format: Type moves followed by optional vote numbers
- Example: `e2e4 5 d2d4 3` (5 votes for e2e4 costs 25 credits, 3 votes for d2d4 costs 9 credits)
- Example: `e2e4 10` (10 votes costs 100 credits - all in on one move!)
- If you don't specify a number, it defaults to 1 vote
- If your total exceeds 100 credits, your entire vote is invalid
- If you vote multiple times, only your last vote counts

## Move Notation

All moves must be in UCI (Universal Chess Interface) notation:
- Moves are written as the starting square followed by the ending square
- Example: `e2e4` means move from e2 to e4
- For pawn promotion, add the promotion piece: `e7e8q` promotes to queen
- Special moves like castling are written as the king's movement:
  - Kingside castle: `e1g1` (white) or `e8g8` (black)
  - Queenside castle: `e1c1` (white) or `e8c8` (black)

## Examples

Here are some example scenarios:

1. **FPTP Voting Example:**
```
User1: e2e4
User2: d2d4
User3: e2e4
Result: e2e4 wins with 2 votes
```

2. **Approval Voting Example:**
```
User1: e2e4 d2d4
User2: d2d4 g1f3
User3: e2e4 g1f3
Result: All moves get 2 votes, tie is broken randomly
```

3. **Instant Runoff Example:**
```
User1: e2e4 d2d4 g1f3
User2: d2d4 g1f3 e2e4
User3: g1f3 e2e4 d2d4
First round: No majority
g1f3 eliminated, User3's vote moves to e2e4
Result: e2e4 wins with 2 votes
```

4. **Quadratic Voting Example:**
```
User1: e2e4 5 d2d4 3  (25 + 9 = 34 credits)
User2: d2d4 6         (36 credits)
User3: e2e4 8         (64 credits)
Result: e2e4 wins with 13 votes vs d2d4's 9 votes
```

## Tips
- Your most recent vote always replaces your previous votes
- Invalid moves are ignored, but the rest of your vote still counts
- The vote tally happens every 30 seconds
- Watch the stream title to know which voting system is being used
- The chess engine will respond a few seconds after our move is played