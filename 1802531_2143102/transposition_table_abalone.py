"""
Authors: Yann Roberge (1802531)
         Karl Gharios (2143102)

Date created: 19-Nov-2023
"""
from util import Queue

class TranspositionTableAbalone():
    """
    A container class implementing a transposition table for states that have already been extended.

    Attributes:
        table   (dict[float]) : the large transposition table for our explored states.
                                    string-form state representations are associated to their
                                    previously evaluate heuristic value.
        current_table_size  (int)       : how many states are currently stored in the table
        max_table_size      (int)       : size of table, measured in # of states stored.
                                        if entries are added when the table is full, then older
                                        elements will be removed as per the replacement policy.
        replacement_queue (Queue[str])  : queue of the oldest saved states.
        replacement_queue_len (int)     : length of replacement policy queue
    """

    def __init__(self, max_table_size: int = 100_000, replacement_queue_len: int = 10_000) -> None:
        self.table = {}
        self.table_entries = 0
        self.replacement_queue = Queue()


    def __str__(self) -> str:
        """
        Return a string representation of the transposition table.

        Returns:
            str: The string representation of the table.
        """
        # TODO
        string = None
        return string
    

    def retrieve_value(self, state_hash: str) -> float:
        """
        Retrieve the heuristic value associated to a hash from the table.

        Returns:
            If hit:
                float: Heuristic state value
            If miss:
                None
        """
        #TODO
        print("TranspositionTable: Attempting retrieval for", state_hash)
        return None
    
    def store_value(self, state_hash: str, state_value: float) -> None:
        """
        Store the heuristic value calculated for a state to the table, so that it
        may be used in the future.
        """
        #TODO
        print("TranspositionTable: storing", state_hash, state_value)
        return None
