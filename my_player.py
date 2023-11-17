from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError

import time

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

    def get_opponent_id(self, current_state: GameState) -> int:
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
        begin = time.time()
        best_action = self.alpha_beta(current_state)
        print("Alpha-beta minimax time: ", time.time() - begin)
        return best_action
    
    def alpha_beta(self, current_state: GameState) -> Action:
        def maximize(current_state: GameState, alpha: float, beta: float, depth: int) -> (float, Action):
            if depth == 0 or current_state.is_done():
                return self.evaluate_state(current_state), None

            best_value = float('-inf')
            best_action = None
            for action in current_state.generate_possible_actions():
                transition = action.get_next_game_state()
                value, _ = minimize(transition, alpha, beta, depth - 1)
                if value > best_value:
                    best_value = value
                    best_action = action
                    alpha = max(alpha, best_value)

                if best_value >= beta:
                    return (best_value, best_action)

            return (best_value, best_action)
    
        def minimize(current_state: GameState, alpha: float, beta: float,  depth: int) -> (float, Action):
            if depth == 0 or current_state.is_done():
                return self.evaluate_state(current_state), None

            best_value = float('inf')
            best_action = None
            for action in current_state.generate_possible_actions():
                transition = action.get_next_game_state()
                value, _ = maximize(transition, alpha, beta, depth - 1)
                if value < best_value:
                    best_value = value
                    best_action = action
                    beta = min(beta, best_value)
                
                if best_value <= alpha:
                    return (best_value, best_action)

            return (best_value, best_action)
        
        depth = 3
        _, best_action = maximize(current_state, float('-inf'), float('inf'), depth)
        return best_action
    
    def evaluate_state(self, state: GameState) -> float:
        # Simpple score difference heuristic (favorise opponent marbles out)
        scores_heuristic = state.scores[self.player_id] - state.scores[self.get_opponent_id(state)]

        center_control_heuristic = self.calculate_center_control(state, self.player_id) - self.calculate_center_control(state, self.get_opponent_id(state))

        return scores_heuristic + center_control_heuristic
    
    def calculate_center_control(self, state: GameState, player_id: int) -> float:
        """
        Heuristic pour favoriser le controle du centre.
        Calcule la moyenne de la distance de manhattan entre le centre et l'état (state).   

        Args:
            state (GameState): Current game state representation
            player_id (int): ID du player 

        Returns:
            float: moyenne dist manhattan au centre
        """
        center = (8, 4)
        total_distance = 0
        piece_count = 0

        for position, piece in state.get_rep().get_env().items():
            if piece.get_owner_id() == player_id:
                # Calculate Manhattan distance from the center
                distance = abs(center[0] - position[0]) + abs(center[1] - position[1])
                total_distance += distance
                piece_count += 1

        if piece_count == 0:
            return 0

        return -total_distance / piece_count
