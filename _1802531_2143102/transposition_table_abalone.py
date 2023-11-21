"""
Authors: Yann Roberge (1802531)
         Karl Gharios (2143102)

Date created: 19-Nov-2023
"""
from seahorse.game.game_state import GameState
from .util import Queue
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
        self.max_table_size = max_table_size
        self.replacement_queue = Queue()
        self.replacement_queue_current_size = 0
        self.replacement_queue_len = replacement_queue_len

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
        # Compute hash
        state_hash = self.__compute_hash(state)

        # Return table value, none if entry is not in table
        if state_hash in self.table:
            state_value = self.table[state_hash]
        else:
            state_value = None

        return state_value
    
    def store_value(self, state: GameState, state_value: float) -> None:
        """
        Store the heuristic value calculated for a state to the table, so that it
        may be used in the future.
        """
        # Compute hash
        state_hash = self.__compute_hash(state)

        # If table is full, make room for the new entry
        # Else just store it
        #### TODO: REFACTOR, duplicated code in called functions
        if self.n_table_entries == self.max_table_size:
            self.__replace_table_entry(state_hash)
        else:
            self.n_table_entries += 1
            self.__enqueue_table_entry(state_hash)
        self.table[state_hash] = state_value

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

    def __replace_table_entry(self, new_state_hash: str) -> None:
        """
        Implements the replacement policy to our transposition table:
            Each time a state is added to table, it is saved in a FIFO, unless
            the said FIFO is full.
        """
        # Push last added state, unless queue is full
        if self.replacement_queue_current_size != self.replacement_queue_len:
            self.replacement_queue.push(new_state_hash)
            self.replacement_queue_current_size += 1
        else:
            pass

        # Pop oldest entry, which is to be removed from the table,
        # unless queue is empty.
        if not self.replacement_queue.isEmpty():
            oldest_entry = self.replacement_queue.pop()
            self.table.pop(oldest_entry)

    def __enqueue_table_entry(self, new_state_hash: str) -> None:
        """
        Implements the replacement policy to our transposition table:
            Each time a state is added to table, it is saved in a FIFO, unless
            the said FIFO is full.
        """
        # Push last added state, unless queue is full
        if self.replacement_queue_current_size != self.replacement_queue_len:
            self.replacement_queue.push(new_state_hash)
            self.replacement_queue_current_size += 1
        else:
            pass

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
