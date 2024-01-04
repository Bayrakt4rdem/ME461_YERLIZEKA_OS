class Node():
    """
    A class to represent a node in the search tree which holds moves to that instance of the board 
    """
    def __init__(self, parent, move=None, goalboard = None):
        if move == None and goalboard is not None: # if no move is given, then it is the root node, parent is the initial/final npboard NOT NODE!
            self.board = parent
            self.tilepos = [array[0] for array in np.where(self.board == 0)] # keep track of where 0 is
            self.goalboard = goalboard
            self.moves = []
            self.g = 0
            self.h = self.calc_hn
            self.f = self.g + self.h
        else: # if a move is given, then it is a child node, apply move and calculate cost
            self.board = parent.board.copy()
            self.tilepos = parent.tilepos
            self.goalboard = parent.goalboard
            self.ApplyMove(move)
            self.moves = parent.moves + [move]
            self.g = parent.g + 1
            self.h = self.calc_hn
            self.f = self.g + self.h

    def ApplyMove(self, move):
        '''
        applies a single move to the board and updates it
        move is a list such that [deltaY, deltaX]
        this is manual usage, so it does not care about the previous moves
        '''
        dy, dx = move[0], move[1]
        xn, yn = self.tilepos[1]+dx, self.tilepos[0]+dy # record new coordinates
        if ( dx**2 + dy**2 == 1 and 0<=xn<=2 and 0<=yn<=2 ): # then valid
            self.board[self.tilepos[0], self.tilepos[1]], self.board[yn, xn] = self.board[yn, xn], self.board[self.tilepos[0], self.tilepos[1]]
            self.tilepos = [yn,xn]
        else:
            print("Invalid move")
            return None
        
    def PossibleMoves(self):
        y, x = self.tilepos
        moves = []
        if y > 0:
            moves.append([-1,0])
        if y < 2:
            moves.append([1,0])
        if x > 0:
            moves.append([0,-1])
        if x < 2:
            moves.append([0,1])
        return moves


    @property
    def calc_hn(self):
        '''
        Calculates the heuristic value for the given board.
        Heuristic value is the sum of the Manhattan distances of each tile from its goal position.
        '''
        self.hn = 0
        # Manhattan distance
        for i in range(1,9):
            x,y = np.where(self.board == i) #returns x and y as single valued arrays
            x_goal,y_goal = np.where(self.goalboard == i)
            self.hn += abs(x[0]-x_goal[0]) + abs(y[0]-y_goal[0])
        return self.hn

    
    #Function to assess the equality of two nodes
    def __eq__(self, other):
        return np.array_equal(self.board, other.board)
    #Function to allow indexing from the openlist
    def __hash__(self):
        return hash(tuple(self.board.flatten()))
    #Function to allow printing of the board
    def __str__(self):
        return tabulate([[str(x).replace('0', '*') for x in c]  for c in np.ndarray.tolist(self.board)], tablefmt="grid", stralign="center")
    #Function to allow comparison of nodes
    def __lt__(self, other):
        return self.f < other.f


class Solver():
    '''
    A class that handles the A* algorithm.
    '''

    def __init__(self, boardobj):
        self.initboard = boardobj.Board
        self.goalboard = np.array([[1,2,3],[4,5,6],[7,8,0]])
        
    def Slowest(self):
        '''
        Solves the 8-puzzle using the A* algorithm.
        '''
        self.openlist = [] #list of nodes to be evaluated
        self.closedlist = [] #list of nodes already evaluated
        self.openlist.append(Node(self.initboard, goalboard = self.goalboard)) #add the root node to the openlist
        while self.openlist: #while the openlist is not empty
            self.openlist.sort(key = lambda x: x.f) #sort the openlist by f value (lowest first)
            current = self.openlist.pop(0) #pop the node with the lowest f value
            self.closedlist.append(current) #add the node to the closedlist
            moves = current.PossibleMoves() #find the possible moves from the current node
            successor_nodes = [Node(current, move) for move in moves] #create a list of successor nodes
            for successor in successor_nodes: 
                if np.array_equal(successor.board, self.goalboard): #if the successor node is the goal node, return the moves
                    return successor.moves
                if successor in self.closedlist: #if the successor node is already in the closedlist, pass over it
                    continue
                elif successor in self.openlist: #if the successor node is already in the openlist, check if it has a lower g value
                    open_node = self.openlist[self.openlist.index(successor)]
                    if successor.g < open_node.g: #if it does, update the g value and moves
                        open_node.g = successor.g
                        open_node.moves = successor.moves
                else:
                    self.openlist.append(successor) #if the successor node is not in the openlist, add it to the openlist

    def Fastest(self): 
        '''
        Solves the 8-puzzle using the bidirectional A* algorithm.
        '''

        self.openlist_start = [] 
        self.closedlist_start = [] 
        self.openlist_end = []
        self.closedlist_end = []
        self.openlist_start.append(Node(self.initboard, goalboard = self.goalboard)) 
        self.openlist_end.append(Node(self.goalboard, goalboard = self.initboard))
        
        #Basically the same as the A* algorithm, but with paths from both the start and end nodes
        while self.openlist_start or self.openlist_end: 
            self.openlist_start.sort(key = lambda x: x.f)
            self.openlist_end.sort(key = lambda x: x.f)
            current_start = self.openlist_start.pop(0)
            current_end = self.openlist_end.pop(0)
            self.closedlist_start.append(current_start)
            self.closedlist_end.append(current_end)
            self.closedlist_start.sort(key = lambda x: x.f)
            self.closedlist_end.sort(key = lambda x: x.f)
            if current_start in self.closedlist_end: 
                return current_start.moves + [[array[0]*-1, array[1]*-1] for array in self.closedlist_end[self.closedlist_end.index(current_start)].moves[::-1]]
            if current_end in self.closedlist_start:
                return self.closedlist_start[self.closedlist_start.index(current_end)].moves + [[array[0]*-1, array[1]*-1] for array in current_end.moves[::-1]]
            moves_start = current_start.PossibleMoves()
            moves_end = current_end.PossibleMoves()
            successor_nodes_start = [Node(current_start, move) for move in moves_start]
            successor_nodes_end = [Node(current_end, move) for move in moves_end]
            for successor in successor_nodes_start:
                if successor in self.closedlist_start:
                    continue
                elif successor in self.openlist_start:
                    open_node = self.openlist_start[self.openlist_start.index(successor)]
                    if successor.g < open_node.g:
                        open_node.g = successor.g
                        open_node.moves = successor.moves
                else:
                    self.openlist_start.append(successor)
            for successor in successor_nodes_end:
                if successor in self.closedlist_end:
                    continue
                elif successor in self.openlist_end:
                    open_node = self.openlist_end[self.openlist_end.index(successor)]
                    if successor.g < open_node.g:
                        open_node.g = successor.g
                        open_node.moves = successor.moves
                else:
                    self.openlist_end.append(successor)
            
