from typing import List,  Tuple, Set

def get_next_and_waiting_users(comments: List[Tuple[str, str]]) -> Tuple[Set[str], Set[str]]:
    '''
    Parses the comments to get the users who want to skip to the next move and those who want to wait.
    Returns two sets: set of users who want next move, set of users who want to wait

    When a user coments "n" or "next" (case insensitive), it indicates they want to jump ahead to the next move.
    When a user comments "w" or "wait" (case insensitive), it indicates they want to wait for the current 30 second timme to run out.

    A user's most recent comment of next or wait determines which group they're in.

    Args:
        comments: List of (username, comment) tuples

    Returns:
        two sets:
            1. set of users who want to proceed to the next move
            2. set of users who want to wait
    '''
    next_users = set()
    waiting_users = set()
    
    # Process comments in order, so later comments override earlier ones
    for username, comment in comments:
        # Convert comment to lowercase for case-insensitive comparison
        comment = comment.lower().strip()
        
        # Add user to appropriate set based on their comment
        
        if comment in ('n', 'next'):
            waiting_users.discard(username)
            next_users.add(username)
        elif comment in ('w', 'wait'):
            next_users.discard(username)
            waiting_users.add(username)
            
    return next_users, waiting_users
