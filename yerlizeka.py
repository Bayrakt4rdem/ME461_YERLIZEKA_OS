import numpy as np
import random
import matplotlib.pyplot as plt
from tabulate import tabulate
#from IPython.display import clear_output

from PIL import Image, ImageDraw, ImageFont
from PIL import Image # if needed more can be importaed
import imageio
import time
import heapq

class EightTile():
    '''
    This class implements a basic 8-tile board when instantiated
    You can shuffle it using shuffle() to generate a puzzle
    After shuffling, you can use manual moves using ApplyMove()
    '''
    # class level variables for image and animation generation
    cellSize = 50 #cell within which a single char will be printed
    xpadding = 13
    ypadding = 5
    fontname = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
    fontsize = 45
    font = ImageFont.truetype(fontname, fontsize) # font instace created
    simSteps = 10 # number of intermediate steps in each digit move

    # a class level function
    def GenerateImage(b, BackColor = (255, 125, 60), ForeColor = (0,0,0)):
        '''
        Generates an image given a board numpy array
        0s are simply neglected in the returned image

        if b is not a board object but a string, a single char image is generated
        '''
        cellSize = EightTile.cellSize
        xpadding, ypadding = EightTile.xpadding, EightTile.ypadding
        font = EightTile.font

        if isinstance(b, str): # then a single character is expected, no checks
            img = Image.new('RGB', (cellSize, cellSize), BackColor ) # blank image
            imgPen = ImageDraw.Draw(img) # pen to draw on the blank image
            imgPen.text((xpadding, ypadding), b, font=font, fill=ForeColor) # write the char to img
        else: # the whole board is to be processed
            img = Image.new('RGB', (3*cellSize, 3*cellSize), BackColor ) # blank image
            imgPen = ImageDraw.Draw(img) # pen to draw on the blank image
            for row in range(3): # go row by row
                y = row * cellSize + ypadding
                for col in range(3): # then columns
                    x = col * cellSize + xpadding
                    txt = str(b[row, col]).replace('0', '')
                    # now that position of the current cell is fixed print into it
                    imgPen.text((x, y), txt, font=font, fill=ForeColor) # write the character to board image
        # finally return whatever desired
        return np.array(img) # return image as a numpy array

    def GenerateAnimation(board, actions, mName = 'puzzle', fps=15, debugON = False):
        # using each action collect images
        framez = []
        for action in actions: # for every action generate animation frames
            frm = board.ApplyMove(action, True, debugON)
            EightTile.print_debug(f'frame:{len(frm)} for action {action}', debugON)
            framez += frm
        imageio.mimsave(mName + ".gif", framez, fps=fps) #Creates gif out of list of images
        return framez

    def print_debug(mess, whether2print):
        # this is a simple conditional print,
        # you should prefer alternative methods for intensive printing
        if whether2print:
            print(mess)

    # object level stuff
    def __init__(me, boardarray = None):
        # board is a numpy array
        if boardarray is None:
            me.__board = np.array([[1,2,3],[4,5,6],[7,8,0]])
            me.__winner = me.__board.copy() # by default a winning board is givenq
            # keep track of where 0 is, you can also use np.where, but I like it better this way
            me.__x, me.__y = 2, 2 # initially it is at the bottom right corner
        else:
            me.__board = boardarray.copy()
            zeropos = np.where(me.__board == 0) # keep track of where 0 is
            me.__x, me.__y = zeropos[1][0], zeropos[0][0]
            me.__winner = np.array([[1,2,3],[4,5,6],[7,8,0]])
        
        


    def shuffle(me, n = 1, debugON = False):
        '''
        randomly moves the empty tile, (i.e. the 0 element) around the gameboard
        n times and returns the moves from the initial to the last move
        Input:
            n: number of shuffles to performe, defaults to 1
        Output:
            a list of n entries [ [y1, x2], [y2, x2], ... , [yn, xn]]
            where [yi, xi] is the relative move of the empty tile at step i
            ex: [-1, 0] means that empty tile moved left horizontally
                note that:
                    on the corners there 2 moves
                    on the edges there are 3 moves
                    only at the center there are 4 moves

        Hence if you apply the negative of the returned list to the board
        step by step the puzzle should be solved!
        Check out ApplyMove()
        '''
        # depending on the current index possible moves are listed
        # think of alternative ways of achieving this, without using if conditions
        movez = [[0,1], [-1,0,1], [-1,0]]
        trace = []
        dxold, dyold = 0, 0 # past moves are tracked to be avoided, at first no such history
        for i in range(n):
            # note that move is along either x or y, but not both!
            # also no move at all is not accepted
            # we should also avoid the last state, i.e. an opposite move is not good
            dx, dy = 0, 0 # initial move is initialized to no move at all
            while ( dx**2 + dy**2 != 1 ) or (dx == -dxold and dy == -dyold): # i.e. it is either no move or a diagonal move
                dx = random.choice(movez[me.__x])
                dy = random.choice(movez[me.__y])
            # now that we have the legal moves, we also have the new coordinates
            xn, yn = me.__x+dx, me.__y+dy # record new coordinates
            trace.append([dy, dx]) # just keeping track of the move not the absolute position tomato, tomato
            me.__board[me.__y, me.__x], me.__board[yn, xn] = me.__board[yn, xn], me.__board[me.__y, me.__x]
            # enable print if debug is desired
            EightTile.print_debug(f'shuffle[{i}]: {me.__y},{me.__x} --> {yn},{xn}\n{me}\n', debugON)
            # finally update positions as well
            me.__x, me.__y = xn, yn

            dxold, dyold = dx, dy # keep track of old moves to avoid oscillations

        # finally return the sequence of shuffles
        # note that if negative of trace is applied to the board in reverse order board should reset!
        return trace

    def ApplyMove(me, move, generateAnimation = False, debugON = False):
        '''
        applies a single move to the board and updates it
        move is a list such that [deltaY, deltaX]
        this is manual usage, so it does not care about the previous moves
        if generateAnimation is set, a list of images will be returned that animates the move
        '''
        dy, dx = move[0], move[1]
        xn, yn = me.__x+dx, me.__y+dy # record new coordinates
        img = None
        imList = []
        if ( dx**2 + dy**2 == 1 and 0<=xn<=2 and 0<=yn<=2 ): # then valid
            if generateAnimation:
                # the value at the target will move to the current location
                cellSize = EightTile.cellSize
                simSteps = EightTile.simSteps
                c = me.__board[yn, xn]
                EightTile.print_debug(f'{c} is moving', debugON)
                # generate a template image
                temp = me.Board # copy board
                temp[yn, xn] = 0 # blank the moving number as well which is kept in c
                tempimg = EightTile.GenerateImage(temp) # get temp image
                tempnum = EightTile.GenerateImage(str(c)) # get the image for moving number
                # now at every animation step generate a new image
                # image will move in either along x or y, but linspace does not care
                xPos = np.linspace(xn * cellSize, me.__x * cellSize, simSteps+1, dtype=int)
                yPos = np.linspace(yn * cellSize, me.__y * cellSize, simSteps+1, dtype=int)
                Pos = np.vstack((yPos, xPos)).T # position indices in target image are in rows
                EightTile.print_debug(f'Position', debugON)
                # go over each pos pair to generate new images
                for p in range(Pos.shape[0]):
                    frm = tempimg.copy() # generate a template image
                    xi, yi = Pos[p,1], Pos[p,0]
                    EightTile.print_debug(f'moving to {yi}:{xi}', debugON)
                    #'''
                    frm[yi:yi+50, xi:xi+50, :] = tempnum # set image
                    EightTile.print_debug(f'frm = {frm.shape}, tempnum = {tempnum.shape}', debugON)
                    # finally add image to list
                    imList.append(frm)
            me.__board[me.__y, me.__x], me.__board[yn, xn] = me.__board[yn, xn], me.__board[me.__y, me.__x]
            me.__x, me.__y = xn, yn
            return imList
        else:
            return None

    def __str__(me):
        '''
        generates a printable version of the board
        note that * is the empty space and in the numpy representation of
        the board it is 0 (zero)
        '''
        return tabulate([[str(x).replace('0', '*') for x in c]  for c in np.ndarray.tolist(me.__board)], tablefmt="grid", stralign="center")

    @property
    def Position(me):
        # returns the position of the empty cell
        return [me.__y, me.__x]

    @property
    def Board(me):
        # returns a numpy array stating the current state of the board
        return me.__board.copy() # return a copy of the numpy array

    @property
    def isWinner(me):
        # returns true, if current board is a winner
        return np.array_equal(me.__winner, me.__board)

    @property
    def BoardImage(me):
        return EightTile.GenerateImage(me.Board)
    

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
            


board = EightTile()
board.shuffle(500)
print(board)
solver = Solver(board)
start = time.time()
solution = solver.Fastest()
end = time.time()
print(solution)
print(f"Solved in {len(solution)} moves")
print(f"Time taken: {end-start} seconds")
frm = EightTile.GenerateAnimation(board, solution, f'puzzle{60}', fps=50)


