"""
Authors: Yann Roberge (1802531)
         Karl Gharios (2143102)

Date created: 19-Nov-2023
"""
from seahorse.game.game_state import GameState
from util import Queue
import json

class TranspositionTableAbalone():
    """
    A container class implementing a transposition table for states that have already been extended.

    Attributes:
        table   (dict[float]) : the large transposition table for our explored states.
                                    string-form state representations are associated to their
                                    previously evaluate heuristic value.
        n_table_entries     (int)       : how many states are currently stored in the table
        max_table_size      (int)       : size of table, measured in # of states stored.
                                        if entries are added when the table is full, then older
                                        elements will be removed as per the replacement policy.
        replacement_queue (Queue[str])  : queue of the oldest saved states.
        replacement_queue_len (int)     : length of replacement policy queue
    """

    def __init__(self, max_table_size: int = 100_000, replacement_queue_len: int = 10_000) -> None:
        self.table = {}
        self.n_table_entries = 0
        self.replacement_queue = Queue()


    def __str__(self) -> str:
        """
        Return a string representation of the transposition table.

        Returns:
            str: The string representation of the table.
        """
        string = self.to_json().dumps()
        return string
    
    def retrieve_value(self, state: GameState) -> float:
        """
        Retrieve the heuristic value associated to a hash from the table.

        Returns:
            If hit:
                float: Heuristic state value
            If miss:
                None
        """
        #TODO
        state_hash = self.__compute_hash(state)
        print("TranspositionTable: Attempting retrieval for", state_hash)
        return None
    
    def store_value(self, state: GameState, state_value: float) -> None:
        """
        Store the heuristic value calculated for a state to the table, so that it
        may be used in the future.
        """
        #TODO
        state_hash = self.__compute_hash(state)
        print("TranspositionTable: storing", state_hash, state_value)
        return None

    def __compute_hash(self, state: GameState) -> str:
        """
        Convert a game state into a compact string form used as a hash in
        the transposition table

        Returns:
            str: A unique string representing a game state
        """
        # TODO: implement
        next_player_id = state.next_player.get_id()

        # Create a long string representing board grid with no whitespaces
        board_lines = []
        for line in state.get_rep().get_grid():
            board_lines.append(''.join(map(str, line)))
        compact_board_grid = ''.join(board_lines)

        hash = str(next_player_id) + compact_board_grid
        return hash

    def to_json(self) -> dict:
        """
        Converts table to a JSON object.

        Returns:
            dict: The JSON representation of the table.
        """
        json_table = {"table" : json.dumps(self.table), \
                "n_table_entries"   : self.n_table_entries, \
                "replacement_queue" : json.dumps(self.replacement_queue.list), \
                "replacement_queue_len": self.n_table_entries }
        return json_table
