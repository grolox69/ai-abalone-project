from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError

from _1802531_2143102.transposition_table_abalone import TranspositionTableAbalone

import time

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type   (str): piece type of the player
        board_config (str): board configuration
                            WARNING: We are well aware that board configuration has no place
                            under the player class, however we have been instructed not to
                            change any other file for the purpose of this particular project.
        transposition_table (TranspositionTable): table for caching calculated heuristics
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
        self.board_config = None
        self.transposition_table = TranspositionTableAbalone(\
                                        max_table_size = 1_000_000, \
                                        replacement_queue_len = 10_000)

        #### SEARCH DEPTH ####
        self.search_depth = 3
        ######################

    def get_opponent_id(self, current_state: GameState) -> int:
        """
        Retrieve the opponent's player ID within the current game state.

        Args:
            current_state (GameState): The current state of the game, which contains information about all players.

        Returns:
            int: The ID of the opponent player.
        """
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
        # Detect board configuration
        step = current_state.get_step()
        if step == 0:
            self.detect_board_configuration(current_state)
            print("Board configuration: ", self.board_config)

        # Attempt to retrieve the next move from the hardcoded opening table
        best_action = self.move_from_opening_table(self.board_config, current_state)
        if best_action != None:
            return best_action

        # Main search strategy: Alpha-beta minimax
        begin = time.time()
        best_action = self.alpha_beta(current_state)
        print("my_player step time: ", time.time() - begin)
        return best_action
    

    def detect_board_configuration(self, current_state: GameState):
        """
        Detect whether the starting board configuration is classic, alien, or neither of the two
        
        Args:
            current_state (GameState): The current state of the game including the board layout.

        Returns:
            None: This function does not return anything but sets the board_config attribute.
        """

        # Board configuration can only be checked before any moves have been played
        current_step = current_state.get_step()
        if current_step != 0:
            print("ERROR: board config detection can only take place before any move \
                  has been played.")
            return None

        # Classic config
        board_classic = [
            [ 0 ,  0 , 'W', 'W', 'W', 'W', 'W',  0 ,  0 ],
            [ 0 , 'W', 'W', 'W', 'W', 'W', 'W',  0 ,  0 ],
            [ 0 ,  3 ,  3 , 'W', 'W', 'W',  3 ,  3 ,  0 ],
            [ 3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  0 ],
            [ 3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ],
            [ 3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  0 ],
            [ 0 ,  3 ,  3 , 'B', 'B', 'B',  3 ,  3 ,  0 ],
            [ 0 , 'B', 'B', 'B', 'B', 'B', 'B',  0 ,  0 ],
            [ 0 ,  0 , 'B', 'B', 'B', 'B', 'B',  0 ,  0 ]
        ]

        # Alien config
        board_alien = [
            [ 0 ,  0 , 'B',  3 , 'B',  3 , 'B',  0 ,  0 ],
            [ 0 ,  3 , 'B', 'W', 'W', 'B',  3 ,  0 ,  0 ],
            [ 0 ,  3 , 'B', 'W', 'B', 'W', 'B',  3 ,  0 ],
            [ 3 ,  3 ,  3 , 'B', 'B',  3 ,  3 ,  3 ,  0 ],
            [ 3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ],
            [ 3 ,  3 ,  3 , 'W', 'W',  3 ,  3 ,  3 ,  0 ],
            [ 0 ,  3 , 'W', 'B', 'W', 'B', 'W',  3 ,  0 ],
            [ 0 ,  3 , 'W', 'B', 'B', 'W',  3 ,  0 ,  0 ],
            [ 0 ,  0 , 'W',  3 , 'W',  3 , 'W',  0 ,  0 ]
        ]

        # Get current board grid representation
        current_board = current_state.get_rep().get_grid()

        if current_board == board_classic:
            self.board_config = "classic"
        elif current_board == board_alien:
            self.board_config = "alien"
        else:
            self.board_config = "other"
            
    def move_from_opening_table(self, starting_position: str, current_state: GameState) -> Action:
        # Opening table only covers the first three moves
        current_step = current_state.get_step()
        if current_step >= 6:
            return None

        if starting_position == "classic":
            opening_action = self.move_from_classic_opening_table(current_state)
        elif starting_position == "alien":
            opening_action = self.move_from_alien_opening_table(current_state)
        else:
            opening_action = None
        return opening_action

    def move_from_classic_opening_table(self, current_state: GameState) -> Action:
        # Opening table
        piece_type = current_state.next_player.get_piece_type()
        current_step = current_state.get_step()

        # Opening table only covers the first three moves
        if current_step >= 6:
            return None

        print("Playing from", piece_type, "classic opening table.")

        ## If starting position = classic
        ## Secure the center as fast as possible
        ### If white:
        ###   (1,3) -> down left
        ###   (5,1) -> down right
        ###   If (6,4) is still empty
        ###     (3,1) -> bottom right
        ###   Else (black pushed us into (6,4) ):
        ###     (6,2) -> bottom right
        ### If black:
        ###   (13,7) -> up left
        ###   If (8,4) is still empty:
        ###     (14,4) -> up right
        ###     (15,5) -> up right      
        ###   Else (white already moved into (8,4) ):
        ###     (15,5) -> up right
        ###     (14,6) -> up right      
        if piece_type == 'W':
            if current_step == 0: # First move
                opening_action = current_state.convert_light_action_to_action( \
                                        data={'from':(1,3), 'to':(3,3)})
            elif current_step == 2: # Second move
                opening_action = current_state.convert_light_action_to_action( \
                                        data={'from':(5,1), 'to':(6,2)})
            elif current_step == 4: # Third move
                non_empty_tiles = current_state.get_rep().get_env().keys()

                if (6, 4) not in non_empty_tiles:
                    opening_action = current_state.convert_light_action_to_action( \
                                            data={'from':(3,1), 'to':(4,2)})
                else:
                    opening_action = current_state.convert_light_action_to_action( \
                                            data={'from':(6,2), 'to':(7,3)})

        elif piece_type == 'B':
            white_moved_into_center = False

            if current_step == 1: # First move
                opening_action = current_state.convert_light_action_to_action( \
                                        data={'from':(13,7), 'to':(12,6)})

            elif current_step == 3: # Second move
                # check if (8,4) is empty on step 3:
                non_empty_tiles = current_state.get_rep().get_env().keys()

                if (8, 4) not in non_empty_tiles:
                    white_moved_into_center = False
                    opening_action = current_state.convert_light_action_to_action( \
                                    data={'from':(14,4), 'to':(12,4)})
                else:
                    white_moved_into_center = True
                    opening_action = current_state.convert_light_action_to_action( \
                                    data={'from':(15,5), 'to':(13,5)})
                
            elif current_step == 5: # Third move
                if white_moved_into_center == False:
                    opening_action = current_state.convert_light_action_to_action( \
                                    data={'from':(15,5), 'to':(13,5)})
                else:
                    opening_action = current_state.convert_light_action_to_action( \
                                    data={'from':(14,6), 'to':(12,6)})
        return opening_action

    def move_from_alien_opening_table(self, current_state: GameState) -> Action:
        # Opening table
        piece_type = current_state.next_player.get_piece_type()
        current_step = current_state.get_step()

        # Opening table only covers the first move
        if current_step >= 2:
            return None

        print("Playing from", piece_type, "alien opening table.")

        ## If starting position = alien
        ## Secure the center as fast as possible
        ### If white:
        ###   (4,4) -> up left
        ### If black:
        ###   (12,4) -> up right      
        if piece_type == 'W':
            if current_step == 0: # First move
                opening_action = current_state.convert_light_action_to_action( \
                                        data={'from':(4,4), 'to':(3,3)})

        elif piece_type == 'B':
            if current_step == 1: # First move
                opening_action = current_state.convert_light_action_to_action( \
                                        data={'from':(12,4), 'to':(13,5)})
        return opening_action

    def alpha_beta(self, current_state: GameState) -> Action:
        """
        Implements the Alpha-Beta pruning algorithm to determine the best action in the current game state.
        
        Args:
            current_state (GameState): The current state of the game.

        Returns:
            Action: The best action to take as determined by the Alpha-Beta algorithm.
        """

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
        
        depth = self.search_depth
        _, best_action = maximize(current_state, float('-inf'), float('inf'), depth)
        return best_action
    
    def evaluate_state(self, state: GameState) -> float:
        """
        Evaluates the given game state and returns a numerical score representing its value.

        Args:
            state (GameState): The current state of the game to be evaluated.

        Returns:
            float: A numerical value representing the desirability of the given game state.
        """

        # Attempt retrieving a cached state value from transposition table
        estimated_value_from_table = self.transposition_table.retrieve_value(state)

        ## If hit, return said value
        if estimated_value_from_table != None:
            return estimated_value_from_table
        ## If miss, compute heuristics
        else:
            state_value = self.compute_state_heuristic(state)

        # Save calculated value to transposition table for future use
        self.transposition_table.store_value(state, state_value)

        return self.compute_state_heuristic(state)

    def compute_state_heuristic(self, state: GameState) -> float:
        # Estimate state value based on heuristics
        ## Simple score difference heuristic (favors opponent marbles out)
        scores_heuristic = state.scores[self.player_id] - state.scores[self.get_opponent_id(state)]

        center_control_heuristic = self.calculate_center_control(state, self.player_id) - self.calculate_center_control(state, self.get_opponent_id(state))
        cluster_heuristic = self.calculate_clustering(state, self.player_id) - self.calculate_clustering(state, self.get_opponent_id(state))

        heuristic = scores_heuristic + 0.9 * center_control_heuristic + 0.4 * cluster_heuristic
        return heuristic

    def calculate_center_control(self, state: GameState, player_id: int) -> float:
        """
        Heuristique pour favoriser le controle du centre.
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
    
    def calculate_clustering(self, state: GameState, player_id: int) -> float:
        """
        Heuristic to favor keeping pieces in clusters.

        Args:
            state (GameState): Current game state representation
            player_id (int): ID of the player

        Returns:
            float: Score representing the clustering of pieces
        """
        clustering_score = 0
        processed = set()

        # Calculate the number of adjacent friendly pieces for each piece
        for position, piece in state.get_rep().get_env().items():
            if piece.get_owner_id() == player_id and position not in processed:
                cluster_size = self.get_cluster_size(state, position, player_id, processed)
                clustering_score += cluster_size
        return clustering_score

    def get_cluster_size(self, state: GameState, start_position, player_id: int, processed: set) -> int:
        """
        Determine the size of the cluster starting from start_position.

        Args:
            state (GameState): Current game state representation
            start_position (tuple): The starting position of the piece
            player_id (int): ID of the player
            processed (set): A set to record processed positions to avoid double counting

        Returns:
            int: Size of the cluster
        """
        queue = [start_position]
        cluster_size = 0
        while queue:
            current_position = queue.pop(0)
            if current_position in processed:
                continue

            processed.add(current_position)
            current_piece = state.get_rep().get_env().get(current_position, None)

            if current_piece and current_piece.get_owner_id() == player_id:
                cluster_size += 1
                # Add neighbors of current piece to queue to repeat process
                neighbors = state.get_rep().get_neighbours(current_position[0], current_position[1])
                for direction, neighbor in neighbors.items():
                    if neighbor[1] not in processed:
                        queue.append(neighbor[1])
        return cluster_size
