from game_master import GameMaster
from read import *
from util import *

class TowerOfHanoiGame(GameMaster):

    def __init__(self):
        super().__init__()
        
    def produceMovableQuery(self):
        """
        See overridden parent class method for more information.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?disk ?init ?target)')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.
        The output should be a Tuple of three Tuples. Each inner tuple should
        represent a peg, and its content the disks on the peg. Disks
        should be represented by integers, with the smallest disk
        represented by 1, and the second smallest 2, etc.

        Within each inner Tuple, the integers should be sorted in ascending order,
        indicating the smallest disk stacked on top of the larger ones.

        For example, the output should adopt the following format:
        ((1,2,5),(),(3, 4))

        Returns:
            A Tuple of Tuples that represent the game state
        """
        ### student code goes here
        peg1 = ()
        peg2 = ()
        peg3 = ()
        # ask for all pegs
        get_pegs = parse_input('fact: (inst ?p Peg)')
        pegs = self.kb.kb_ask(get_pegs)
        for peg in pegs:
            is_this_peg_empty = Fact(instantiate(Statement(('empty', '?p')), peg)) # construct query fact
            # check if peg is not empty
            if is_this_peg_empty not in self.kb.facts:
                # get the disks on this peg
                get_disks = Fact(instantiate(Statement(('on', '?d', '?p')), peg))
                disks = self.kb.kb_ask(get_disks)
                # convert the list of disks to a list of integers representing the disks
                disks = list(map(lambda d: int(d.bindings_dict['?d'].replace('disk', '')), disks))
                disks.sort() # sort by acending order
                # retrieve peg identity
                peg_num = int(peg.bindings_dict['?p'].replace('peg', ''))
                # switch cases
                if peg_num is 1:
                    peg1 = tuple(disks)
                elif peg_num is 2:
                    peg2 = tuple(disks)
                else:
                    peg3 = tuple(disks)
        return (peg1, peg2, peg3)

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable disk1 peg1 peg3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        ### Student code goes here
        if (movable_statement.predicate != 'movable'):
            return
        (disk, src, dst) = movable_statement.terms
        retract_facts = []
        assert_facts = []
        dst_top = None
        src_below = None
        # facts to be retracted
        retract_facts.append(Fact(Statement(('on', disk, src))))
        retract_facts.append(Fact(Statement(('top', disk, src))))
        is_dst_empty = self.kb.kb_ask(Fact(Statement(('empty', dst))))
        if is_dst_empty:
            retract_facts.append(Fact(Statement(('empty', dst))))
        else:
            dst_top = self.kb.kb_ask(Fact(Statement(('top', '?d', dst))))[0]
            retract_facts.append(Fact(instantiate(Statement(('top', '?d', dst)), dst_top)))
        is_src_least_two = self.kb.kb_ask(Fact(Statement(('onTop', disk, '?d'))))
        if is_src_least_two:
            src_below = is_src_least_two[0]
            retract_facts.append(Fact(instantiate(Statement(('onTop', disk, '?d')), src_below)))
        # facts to be added
        assert_facts.append(Fact(Statement(('on', disk, dst))))
        assert_facts.append(Fact(Statement(('top', disk, dst))))
        if not is_dst_empty:
            assert_facts.append(Fact(instantiate(Statement(('onTop', disk, '?d')), dst_top)))
        if is_src_least_two:
            assert_facts.append(Fact(instantiate(Statement(('top', '?d', src)), src_below)))
        else:
            assert_facts.append(Fact(Statement(('empty', src))))

        # retract/add facts
        for r in retract_facts:
            self.kb.kb_retract(r)
        for a in assert_facts:
            self.kb.kb_assert(a)      

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[2], sl[1]]
        self.makeMove(Statement(newList))

class Puzzle8Game(GameMaster):

    def __init__(self):
        super().__init__()

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?piece ?initX ?initY ?targetX ?targetY)')

    def getGameState(self):
        """
        Returns a representation of the the game board in the current state.
        The output should be a Tuple of Three Tuples. Each inner tuple should
        represent a row of tiles on the board. Each tile should be represented
        with an integer; the empty space should be represented with -1.

        For example, the output should adopt the following format:
        ((1, 2, 3), (4, 5, 6), (7, 8, -1))

        Returns:
            A Tuple of Tuples that represent the game state
        """
        ### Student code goes here
        state = [[],[],[]]
        for y in range(3):
            for x in range(3):
                what_tile_is_here = Fact(Statement(('position', '?t', f'pos{x+1}', f'pos{y+1}')))
                tile = self.kb.kb_ask(what_tile_is_here)[0]
                if (tile.bindings_dict['?t'] == 'empty'):
                    state[y].append(-1)
                else:
                    tile_num = int(tile.bindings_dict['?t'].replace('tile', ''))
                    state[y].append(tile_num)
        
        return tuple(map(lambda r: tuple(r), state))

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable tile3 pos1 pos3 pos2 pos3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        ### Student code goes here
        if (movable_statement.predicate != 'movable'):
            return
        (tile, src_x, src_y, dst_x, dst_y) = movable_statement.terms
        # facts to be retracted
        old_fact1 = Fact(Statement(('position', tile, src_x, src_y)))
        old_fact2 = Fact(Statement(('position', 'empty', dst_x, dst_y)))
        # facts to be added
        new_fact1 = Fact(Statement(('position', 'empty', src_x, src_y)))
        new_fact2 = Fact(Statement(('position', tile, dst_x, dst_y)))
        # retract/add facts
        self.kb.kb_retract(old_fact1)
        self.kb.kb_retract(old_fact2)
        self.kb.kb_assert(new_fact1)
        self.kb.kb_assert(new_fact2)

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[3], sl[4], sl[1], sl[2]]
        self.makeMove(Statement(newList))
