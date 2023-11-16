from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)
        self.player_id = self.get_id()

    def get_opponent_id(self, current_state: GameState):
        for player in current_state.players:
            if player.get_id() != self.player_id:
                return player.get_id()

    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        depth = 6
        best_action = None
        best_value = float('-inf')

        for action in current_state.generate_possible_actions():
            value = self.minimize(action.get_next_game_state(), depth - 1)
            if value > best_value:
                best_value = value
                best_action = action

        return best_action
    
    def maximize(self, current_state: GameState, depth: int) -> Action:
        if depth == 0 or current_state.is_done():
            return self.evaluate_state(current_state)

        best_value = float('-inf')
        for action in current_state.generate_possible_actions():
            value = self.minimize(action.get_next_game_state(), depth - 1)
            best_value = max(best_value, value)

        return best_value
    
    def minimize(self, current_state: GameState, depth: int) -> Action:
        if depth == 0 or current_state.is_done():
            return self.evaluate_state(current_state)

        best_value = float('inf')
        for action in current_state.generate_possible_actions():
            value = self.maximize(action.get_next_game_state(), depth - 1)
            best_value = min(best_value, value)

        return best_value
    
    def evaluate_state(self, state: GameState) -> float:
        return state.scores[self.player_id] - state.scores[self.get_opponent_id(state)]
