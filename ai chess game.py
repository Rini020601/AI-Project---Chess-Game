import pygame #Game library
from pygame.locals import * #For useful variables
import copy #Library used to make exact copies of lists.
import pickle #Library used to store dictionaries in a text file and read them from text files.
import random #Used for making random selections
from collections import defaultdict #Used for giving dictionary values default data types.
from collections import Counter #For counting elements in a list effieciently.
import threading
class GamePosition:
    def __init__(self,board,player,castling_rights,EnP_Target,HMC,history = {}):
        self.board = board #A 2D array containing information about piece postitions. Check main
        #function to see an example of such a representation.
        self.player = player #Stores the side to move. If white to play, equals 0. If black to
        #play, stores 1.
        self.castling = castling_rights #A list that contains castling rights for white and
        #black. Each castling right is a list that contains right to castle kingside and queenside.
        self.EnP = EnP_Target #Stores the coordinates of a square that can be targeted by en passant capture.
        self.HMC = HMC #Half move clock. Stores the number of irreversible moves made so far, in order to help
        #detect draw by 50 moves without any capture or pawn movement.
        self.history = history #A dictionary that stores as key a position (hashed) and the value of each of
        #these keys represents the number of times each of these positions was repeated in order for this
        #position to be reached.
        
    def getboard(self):
        return self.board
    def setboard(self,board):
        self.board = board
    def getplayer(self):
        return self.player
    def setplayer(self,player):
        self.player = player
    def getCastleRights(self):
        return self.castling
    def setCastleRights(self,castling_rights):
        self.castling = castling_rights
    def getEnP(self):
        return self.EnP
    def setEnP(self, EnP_Target):
        self.EnP = EnP_Target
    def getHMC(self):
        return self.HMC
    def setHMC(self,HMC):
        self.HMC = HMC
    def checkRepition(self):
    def addtoHistory(self,position):
        #Generate a unique key out of the current position:
        key = pos2key(position)
        #Add it to the history dictionary.
        self.history[key] = self.history.get(key,0) + 1
    def gethistory(self):
        return self.history
    def clone(self):
        #This method returns another instance of the current object with exactly the same
        #parameters but independent of the current object.
        clone = GamePosition(copy.deepcopy(self.board), #Independent copy
                             self.player,
                             copy.deepcopy(self.castling), #Independent copy
                             self.EnP,
                             self.HMC)
        return clone
class Shades:
    #Self explanatory:
    def __init__(self,image,coord):
        self.image = image
        self.pos = coord
    def getInfo(self):
        return [self.image,self.pos]
class Piece:
    def __init__(self,pieceinfo,chess_coord):
        #pieceinfo is a string such as 'Qb'. The Q represents Queen and b
        #shows the fact that it is black:
        piece = pieceinfo[0]
        color = pieceinfo[1]
        #Get the information about where the image for this piece is stored
        #on the overall sprite image with all the pieces. Note that
        #square_width and square_height represent the size of a square on the
        #chess board.
        if piece=='K':
            index = 0
        elif piece=='Q':
            index = 1
        elif piece=='B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        left_x = square_width*index
        if color == 'w':
            left_y = 0
        else:
            left_y = square_height
        
        self.pieceinfo = pieceinfo
        #subsection defines the part of the sprite image that represents our
        #piece:
        self.subsection = (left_x,left_y,square_width,square_height)
        #There are two ways that the position of a piece is defined on the
        #board. The default one used is the chess_coord, which stores something
        #like (3,2). It represents the chess coordinate where our piece image should
        #be blitted. On the other hand, is pos does not hold the default value
        #of (-1,-1), it will hold pixel coordinates such as (420,360) that represents
        #the location in the window that the piece should be blitted on. This is
        #useful for example if our piece is transitioning from a square to another:
        self.chess_coord = chess_coord
        self.pos = (-1,-1)

    #The methods are self explanatory:
    def getInfo(self):
        return [self.chess_coord, self.subsection,self.pos]
    def setpos(self,pos):
        self.pos = pos
    def getpos(self):
        return self.pos
    def setcoord(self,coord):
        self.chess_coord = coord
    def __repr__(self):
        #useful for debugging
        return self.pieceinfo+'('+str(chess_coord[0])+','+str(chess_coord[1])+')'
        def drawText(board):
    for i in range(len(board)):
        for k in range(len(board[i])):
            if board[i][k]==0:
                board[i][k] = 'Oo'
        print (board[i])
    for i in range(len(board)):
        for k in range(len(board[i])):
            if board[i][k]=='Oo':
                board[i][k] = 0
def isOccupied(board,x,y):
    if board[y][x] == 0:
    #The square has nothing on it.
        return False
    return True
def isOccupiedby(board,x,y,color):
    if board[y][x]==0:
        #the square has nothing on it.
        return False
    if board[y][x][1] == color[0]:
        #The square has a piece of the color inputted.
        return True
    #The square has a piece of the opposite color.
    return False
def filterbyColor(board,listofTuples,color):
    filtered_list = []
    #Go through each coordinate:
    for pos in listofTuples:
        x = pos[0]
        y = pos[1]
        if x>=0 and x<=7 and y>=0 and y<=7 and not isOccupiedby(board,x,y,color):
            #coordinates are on-board and no same-color piece is on the square.
            filtered_list.append(pos)
    return filtered_list
def lookfor(board,piece):
    listofLocations = []
    for row in range(8):
        for col in range(8):
            if board[row][col] == piece:
                x = col
                y = row
                listofLocations.append((x,y))
    return listofLocations
def isAttackedby(position,target_x,target_y,color):
    #Get board
    board = position.getboard()
    #Get b from black or w from white
    color = color[0]
    #Get all the squares that are attacked by the particular side:
    listofAttackedSquares = []
    for x in range(8):
        for y in range(8):
            if board[y][x]!=0 and board[y][x][1]==color:
                listofAttackedSquares.extend(
                    findPossibleSquares(position,x,y,True)) #The true argument
                #prevents infinite recursion.
    #Check if the target square falls under the range of attack by the specified
    #side, and return it:
    return (target_x,target_y) in listofAttackedSquares             
def findPossibleSquares(position,x,y,AttackSearch=False):
    #Get individual component data from the position object:
    board = position.getboard()
    player = position.getplayer()
    castling_rights = position.getCastleRights()
    EnP_Target = position.getEnP()
    #In case something goes wrong:
    if len(board[y][x])!=2: #Unexpected, return empty list.
        return [] 
    piece = board[y][x][0] #Pawn, rook, etc.
    color = board[y][x][1] #w or b.
    #Have the complimentary color stored for convenience:
    enemy_color = opp(color)
    listofTuples = [] #Holds list of attacked squares.

    if piece == 'P': #The piece is a pawn.
        if color=='w': #The piece is white
            if not isOccupied(board,x,y-1) and not AttackSearch:
                #The piece immediately above is not occupied, append it.
                listofTuples.append((x,y-1))
                
                if y == 6 and not isOccupied(board,x,y-2):
                    #If pawn is at its initial position, it can move two squares.
                    listofTuples.append((x,y-2))
            
            if x!=0 and isOccupiedby(board,x-1,y-1,'black'):
                #The piece diagonally up and left of this pawn is a black piece.
                #Also, this is not an 'a' file pawn (left edge pawn)
                listofTuples.append((x-1,y-1))
            if x!=7 and isOccupiedby(board,x+1,y-1,'black'):
                #The piece diagonally up and right of this pawn is a black one.
                #Also, this is not an 'h' file pawn.
                listofTuples.append((x+1,y-1))
            if EnP_Target!=-1: #There is a possible en pasant target:
                if EnP_Target == (x-1,y-1) or EnP_Target == (x+1,y-1):
                    #We're at the correct location to potentially perform en
                    #passant:
                    listofTuples.append(EnP_Target)
            
        elif color=='b': #The piece is black, same as above but opposite side.
            if not isOccupied(board,x,y+1) and not AttackSearch:
                listofTuples.append((x,y+1))
                if y == 1 and not isOccupied(board,x,y+2):
                    listofTuples.append((x,y+2))
            if x!=0 and isOccupiedby(board,x-1,y+1,'white'):
                listofTuples.append((x-1,y+1))
            if x!=7 and isOccupiedby(board,x+1,y+1,'white'):
                listofTuples.append((x+1,y+1))
            if EnP_Target == (x-1,y+1) or EnP_Target == (x+1,y+1):
                listofTuples.append(EnP_Target)

    elif piece == 'R': #The piece is a rook.
        #Get all the horizontal squares:
        for i in [-1,1]:
            #i is -1 then +1. This allows for searching right and left.
            kx = x #This variable stores the x coordinate being looked at.
            while True: #loop till break.
                kx = kx + i #Searching left or right
                if kx<=7 and kx>=0: #Making sure we're still in board.
                    
                    if not isOccupied(board,kx,y):
                        #The square being looked at it empty. Our rook can move
                        #here.
                        listofTuples.append((kx,y))
                    else:
                        #The sqaure being looked at is occupied. If an enemy
                        #piece is occupying it, it can be captured so its a valid
                        #move. 
                        if isOccupiedby(board,kx,y,enemy_color):
                            listofTuples.append((kx,y))
                        #Regardless of the occupying piece color, the rook cannot
                        #jump over. No point continuing search beyond in this
                        #direction:
                        break
                        
                else: #We have exceeded the limits of the board
                    break
        #Now using the same method, get the vertical squares:
        for i in [-1,1]:
            ky = y
            while True:
                ky = ky + i 
                if ky<=7 and ky>=0: 
                    if not isOccupied(board,x,ky):
                        listofTuples.append((x,ky))
                    else:
                        if isOccupiedby(board,x,ky,enemy_color):
                            listofTuples.append((x,ky))
                        break
                else:
                    break
        
    elif piece == 'N': #The piece is a knight.
        #The knight can jump across a board. It can jump either two or one
        #squares in the x or y direction, but must jump the complimentary amount
        #in the other. In other words, if it jumps 2 sqaures in the x direction,
        #it must jump one square in the y direction and vice versa.
        for dx in [-2,-1,1,2]:
            if abs(dx)==1:
                sy = 2
            else:
                sy = 1
            for dy in [-sy,+sy]:
                listofTuples.append((x+dx,y+dy))
        #Filter the list of tuples so that only valid squares exist.
        listofTuples = filterbyColor(board,listofTuples,color)
    elif piece == 'B': # A bishop.
        #A bishop moves diagonally. This means a change in x is accompanied by a
        #change in y-coordiante when the piece moves. The changes are exactly the
        #same in magnitude and direction.
        for dx in [-1,1]: #Allow two directions in x.
            for dy in [-1,1]: #Similarly, up and down for y.
                kx = x #These varibales store the coordinates of the square being
                       #observed.
                ky = y
                while True: #loop till broken.
                    kx = kx + dx #change x
                    ky = ky + dy #change y
                    if kx<=7 and kx>=0 and ky<=7 and ky>=0:
                        #square is on the board
                        if not isOccupied(board,kx,ky):
                            #The square is empty, so our bishop can go there.
                            listofTuples.append((kx,ky))
                        else:
                            #The square is not empty. If it has a piece of the
                            #enemy,our bishop can capture it:
                            if isOccupiedby(board,kx,ky,enemy_color):
                                listofTuples.append((kx,ky))
                            #Bishops cannot jump over other pieces so terminate
                            #the search here:
                            break    
                    else:
                        #Square is not on board. Stop looking for more in this
                        #direction:
                        break
    
    elif piece == 'Q': #A queen
        #A queen's possible targets are the union of all targets that a rook and
        #a bishop could have made from the same location
        #Temporarily pretend there is a rook on the spot:
        board[y][x] = 'R' + color
        list_rook = findPossibleSquares(position,x,y,True)
        #Temporarily pretend there is a bishop:
        board[y][x] = 'B' + color
        list_bishop = findPossibleSquares(position,x,y,True)
        #Merge the lists:
        listofTuples = list_rook + list_bishop
        #Change the piece back to a queen:
        board[y][x] = 'Q' + color
    elif piece == 'K': # A king!
        #A king can make one step in any direction:
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                listofTuples.append((x+dx,y+dy))
        #Make sure the targets aren't our own piece or off-board:
        listofTuples = filterbyColor(board,listofTuples,color)
        if not AttackSearch:
            #Kings can potentially castle:
            right = castling_rights[player]
            #Kingside
            if (right[0] and #has right to castle
            board[y][7]!=0 and #The rook square is not empty
            board[y][7][0]=='R' and #There is a rook at the appropriate place
            not isOccupied(board,x+1,y) and #The square on its right is empty
            not isOccupied(board,x+2,y) and #The second square beyond is also empty
            not isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
            not isAttackedby(position,x+1,y,enemy_color) and #Or the path through which
            not isAttackedby(position,x+2,y,enemy_color)):#it will move
                listofTuples.append((x+2,y))
            #Queenside
            if (right[1] and #has right to castle
            board[y][0]!=0 and #The rook square is not empty
            board[y][0][0]=='R' and #The rook square is not empty
            not isOccupied(board,x-1,y)and #The square on its left is empty
            not isOccupied(board,x-2,y)and #The second square beyond is also empty
            not isOccupied(board,x-3,y) and #And the one beyond.
            not isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
            not isAttackedby(position,x-1,y,enemy_color) and #Or the path through which
            not isAttackedby(position,x-2,y,enemy_color)):#it will move
                listofTuples.append((x-2,y)) #Let castling be an option.

    #Make sure the king is not under attack as a result of this move:
    if not AttackSearch:
        new_list = []
        for tupleq in listofTuples:
            x2 = tupleq[0]
            y2 = tupleq[1]
            temp_pos = position.clone()
            makemove(temp_pos,x,y,x2,y2)
            if not isCheck(temp_pos,color):
                new_list.append(tupleq)
        listofTuples = new_list
    return listofTuples
def makemove(position,x,y,x2,y2):
    #Get data from the position:
    board = position.getboard()
    piece = board[y][x][0]
    color = board[y][x][1]
    #Get the individual game components:
    player = position.getplayer()
    castling_rights = position.getCastleRights()
    EnP_Target = position.getEnP()
    half_move_clock = position.getHMC()
    #Update the half move clock:
    if isOccupied(board,x2,y2) or piece=='P':
        #Either a capture was made or a pawn has moved:
        half_move_clock = 0
    else:
        #An irreversible move was played:
        half_move_clock += 1

    #Make the move:
    board[y2][x2] = board[y][x]
    board[y][x] = 0
    
    #Special piece requirements:
    #King:
    if piece == 'K':
        #Ensure that since a King is moved, the castling
        #rights are lost:
        castling_rights[player] = [False,False]
        #If castling occured, place the rook at the appropriate location:
        if abs(x2-x) == 2:
            if color=='w':
                l = 7
            else:
                l = 0
            
            if x2>x:
                    board[l][5] = 'R'+color
                    board[l][7] = 0
            else:
                    board[l][3] = 'R'+color
                    board[l][0] = 0
    #Rook:
    if piece=='R':
        #The rook moved. Castling right for this rook must be removed.
        if x==0 and y==0:
            #Black queenside
            castling_rights[1][1] = False
        elif x==7 and y==0:
            #Black kingside
            castling_rights[1][0] = False
        elif x==0 and y==7:
            #White queenside
            castling_rights[0][1] = False
        elif x==7 and y==7:
            #White kingside
            castling_rights[0][0] = False
    #Pawn:
    if piece == 'P':
        #If an en passant kill was made, the target enemy must die:
        if EnP_Target == (x2,y2):
            if color=='w':
                board[y2+1][x2] = 0
            else:
                board[y2-1][x2] = 0
        #If a pawn moved two steps, there is a potential en passant
        #target. Otherise, there isn't. Update the variable:
        if abs(y2-y)==2:
            EnP_Target = (x,(y+y2)/2)
        else:
            EnP_Target = -1
        #If a pawn moves towards the end of the board, it needs to 
        #be promoted. Note that in this game a pawn is being promoted
        #to a queen regardless of user choice.
        if y2==0:
            board[y2][x2] = 'Qw'
        elif y2 == 7:
            board[y2][x2] = 'Qb'
    else:
        #If a pawn did not move, the en passsant target is gone as well,
        #since a turn has passed:
        EnP_Target = -1

    #Since a move has been made, the other player
    #should be the 'side to move'
    player = 1 - player    
    #Update the position data:       
    position.setplayer(player)
    position.setCastleRights(castling_rights)
    position.setEnP(EnP_Target)
    position.setHMC(half_move_clock)
def opp(color):
    color = color[0]
    if color == 'w':
        oppcolor = 'b'
    else:
        oppcolor = 'w'
    return oppcolor
def isCheck(position,color):
    #Get data:
    board = position.getboard()
    color = color[0]
    enemy = opp(color)
    piece = 'K' + color
    #Get the coordinates of the king:
    x,y = lookfor(board,piece)[0]
    #Check if the position of the king is attacked by
    #the enemy and return the result:
    return isAttackedby(position,x,y,enemy)
def isCheckmate(position,color=-1):
    
    if color==-1:
        return isCheckmate(position,'white') or isCheckmate(position,'b')
    color = color[0]
    if isCheck(position,color) and allMoves(position,color)==[]:
        #The king is under attack, and there are no possible moves for this side to make:
            return True
    #Either the king is not under attack or there are possible moves to be played:
    return False
def isStalemate(position):
    #Get player to move:
    player = position.getplayer()
    #Get color:
    if player==0:
        color = 'w'
    else:
        color = 'b'
    if not isCheck(position,color) and allMoves(position,color)==[]:
        #The player to move is not under check yet cannot make a move.
        #It is a stalemate.
        return True
    return False
def getallpieces(position,color):
    #Get the board:
    board = position.getboard()
    listofpos = []
    for j in range(8):
        for i in range(8):
            if isOccupiedby(board,i,j,color):
                listofpos.append((i,j))
    return listofpos
def allMoves(position, color):
    #Find if it is white to play or black:
    if color==1:
        color = 'white'
    elif color ==-1:
        color = 'black'
    color = color[0]
    #Get all pieces controlled by this side:
    listofpieces = getallpieces(position,color)
    moves = []
    #Loop through each piece:
    for pos in listofpieces:
        #For each piece, find all the targets it can attack:
        targets = findPossibleSquares(position,pos[0],pos[1])
        for target in targets:
            #Save them all as possible moves:
             moves.append([pos,target])
    return moves
def pos2key(position):
    #Get board:
    board = position.getboard()
    #Convert the board into a tuple so it is hashable:
    boardTuple = []
    for row in board:
        boardTuple.append(tuple(row))
    boardTuple = tuple(boardTuple)
    #Get castling rights:
    rights = position.getCastleRights()
    #Convert to a tuple:
    tuplerights = (tuple(rights[0]),tuple(rights[1]))
    #Generate the key, which is a tuple that also takes into account the side to play:
    key = (boardTuple,position.getplayer(),
           tuplerights)
    #Return the key:
    return key

##############################////////GUI FUNCTIONS\\\\\\\\\\\\\#############################
def chess_coord_to_pixels(chess_coord):
    x,y = chess_coord
    #There are two sets of coordinates that this function could choose to return.
    #One is the coordinates that would be usually returned, the other is one that
    #would be returned if the board were to be flipped.
    #Note that square width and height variables are defined in the main function and 
    #so are accessible here as global variables.
    if isAI:
        if AIPlayer==0:
            #This means you're playing against the AI and are playing as black:
            return ((7-x)*square_width, (7-y)*square_height)
        else:
            return (x*square_width, y*square_height)
    #Being here means two player game is being played.
    #If the flipping mode is enabled, and the player to play is black,
    #the board should flip, but not until the transition animation for 
    #white movement is complete:
    if not isFlip or player==0 ^ isTransition:
        return (x*square_width, y*square_height)
    else:
        return ((7-x)*square_width, (7-y)*square_height)
def pixel_coord_to_chess(pixel_coord):
    x,y = pixel_coord[0]/square_width, pixel_coord[1]/square_height
    #See comments for chess_coord_to_pixels() for an explanation of the
    #conditions seen here:
    if isAI:
        if AIPlayer==0:
            return (7-x,7-y)
        else:
            return (x,y)
    if not isFlip or player==0 ^ isTransition:
        return (x,y)
    else:
        return (7-x,7-y)
def getPiece(chess_coord):
    for piece in listofWhitePieces+listofBlackPieces:
        #piece.getInfo()[0] represents the chess coordinate occupied
        #by piece.
        if piece.getInfo()[0] == chess_coord:
            return piece
def createPieces(board):
    #Initialize containers:
    listofWhitePieces = []
    listofBlackPieces = []
    #Loop through all squares:
    for i in range(8):
        for k in range(8):
            if board[i][k]!=0:
                #The square is not empty, create a piece object:
                p = Piece(board[i][k],(k,i))
                #Append the reference to the object to the appropriate
                #list:
                if board[i][k][1]=='w':
                    listofWhitePieces.append(p)
                else:
                    listofBlackPieces.append(p)
    #Return both:
    return [listofWhitePieces,listofBlackPieces]
def createShades(listofTuples):
    global listofShades
    #Empty the list
    listofShades = []
    if isTransition:
        #Nothing should be shaded when a piece is being animated:
        return
    if isDraw:
        #The game ended with a draw. Make yellow circle shades for
        #both the kings to show this is the case:
        coord = lookfor(board,'Kw')[0]
        shade = Shades(circle_image_yellow,coord)
        listofShades.append(shade)
        coord = lookfor(board,'Kb')[0]
        shade = Shades(circle_image_yellow,coord)
        listofShades.append(shade)
        #There is no need to go further:
        return
    if chessEnded:
        #The game has ended, with a checkmate because it cannot be a 
        #draw if the code reached here.
        #Give the winning king a green circle shade:
        coord = lookfor(board,'K'+winner)[0]
        shade = Shades(circle_image_green_big,coord)
        listofShades.append(shade)
    #If either king is under attack, give them a red circle:
    if isCheck(position,'white'):
        coord = lookfor(board,'Kw')[0]
        shade = Shades(circle_image_red,coord)
        listofShades.append(shade)
    if isCheck(position,'black'):
        coord = lookfor(board,'Kb')[0]
        shade = Shades(circle_image_red,coord)
        listofShades.append(shade)
    #Go through all the target squares inputted:
    for pos in listofTuples:
        #If the target square is occupied, it can be captured.
        #For a capturable square, there is a different shade.
        #Create the appropriate shade for each target square:
        if isOccupied(board,pos[0],pos[1]):
            img = circle_image_capture
        else:
            img = circle_image_green
        shade = Shades(img,pos)
        #Append:
        listofShades.append(shade)
def drawBoard():
    #Blit the background:
    screen.blit(background,(0,0))
    #Choose the order in which to blit the pieces.
    #If black is about to play for example, white pieces
    #should be blitted first, so that when black is capturing,
    #the piece appears above:
    if player==1:
        order = [listofWhitePieces,listofBlackPieces]
    else:
        order = [listofBlackPieces,listofWhitePieces]
    if isTransition:
        #If a piece is being animated, the player info is changed despite
        #white still capturing over black, for example. Reverse the order:
        order = list(reversed(order))
    #The shades which appear during the following three conditions need to be
    #blitted first to appear under the pieces:
    if isDraw or chessEnded or isAIThink:
        #Shades
        for shade in listofShades:
            img,chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img,pixel_coord)
    #Make shades to show what the previous move played was:
    if prevMove[0]!=-1 and not isTransition:
        x,y,x2,y2 = prevMove
        screen.blit(yellowbox_image,chess_coord_to_pixels((x,y)))
        screen.blit(yellowbox_image,chess_coord_to_pixels((x2,y2)))

    #Blit the Pieces:
    #Notw that one side has to be below the green circular shades to show
    #that they are being targeted, and the other side if dragged to such
    # a square should be blitted on top to show that it is capturing:

    #Potentially captured pieces:
    for piece in order[0]:
        
        chess_coord,subsection,pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos==(-1,-1):
            #Blit to default square:
            screen.blit(pieces_image,pixel_coord,subsection)
        else:
            #Blit to the specific coordinates:
            screen.blit(pieces_image,pos,subsection)
    #Blit the shades in between:
    if not (isDraw or chessEnded or isAIThink):
        for shade in listofShades:
            img,chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img,pixel_coord)
    #Potentially capturing pieces:
    for piece in order[1]:
        chess_coord,subsection,pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos==(-1,-1):
            #Default square
            screen.blit(pieces_image,pixel_coord,subsection)
        else:
            #Specifc pixels:
            screen.blit(pieces_image,pos,subsection)

###########################////////AI RELATED FUNCTIONS\\\\\\\\\\############################

def negamax(position,depth,alpha,beta,colorsign,bestMoveReturn,root=True):
    #First check if the position is already stored in the opening database dictionary:
    if root:
        #Generate key from current position:
        key = pos2key(position)
        if key in openings:
            #Return the best move to be played:
            bestMoveReturn[:] = random.choice(openings[key])
            return
    #Access global variable that will store scores of positions already evaluated:
    global searched
    #If the depth is zero, we are at a leaf node (no more depth to be analysed):
    if depth==0:
        return colorsign*evaluate(position)
    #Generate all the moves that can be played:
    moves = allMoves(position, colorsign)
    #If there are no moves to be played, just evaluate the position and return it:
    if moves==[]:
        return colorsign*evaluate(position)
    #Initialize a best move for the root node:
    if root:
        bestMove = moves[0]
    #Initialize the best move's value:
    bestValue = -100000
    #Go through each move:
    for move in moves:
        #Make a clone of the current move and perform the move on it:
        newpos = position.clone()
        makemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
        #Generate the key for the new resulting position:
        key = pos2key(newpos)
        #If this position was already searched before, retrieve its node value.
        #Otherwise, calculate its node value and store it in the dictionary:
        if key in searched:
            value = searched[key]
        else:
            value = -negamax(newpos,depth-1, -beta,-alpha,-colorsign,[],False)
            searched[key] = value
        #If this move is better than the best so far:
        if value>bestValue:
            #Store it
            bestValue = value
            #If we're at root node, store the move as the best move:
            if root:
                bestMove = move
        #Update the lower bound for this node:
        alpha = max(alpha,value)
        if alpha>=beta:
            #If our lower bound is higher than the upper bound for this node, there
            #is no need to look at further moves:
            break
    #If this is the root node, return the best move:
    if root:
        searched = {}
        bestMoveReturn[:] = bestMove
        return
    #Otherwise, return the bestValue (i.e. value for this node.)
    return bestValue
def evaluate(position):
    if isCheckmate(position,'white'):
        #Major advantage to black
        return -20000
    if isCheckmate(position,'black'):
        #Major advantage to white
        return 20000
    #Get the board:
    board = position.getboard()
    #Flatten the board to a 1D array for faster calculations:
    flatboard = [x for row in board for x in row]
    #Create a counter object to count number of each pieces:
    c = Counter(flatboard)
    Qw = c['Qw']
    Qb = c['Qb']
    Rw = c['Rw']
    Rb = c['Rb']
    Bw = c['Bw']
    Bb = c['Bb']
    Nw = c['Nw']
    Nb = c['Nb']
    Pw = c['Pw']
    Pb = c['Pb']
    #Note: The above choices to flatten the board and to use a library
    #to count pieces were attempts at making the AI more efficient.
    #Perhaps using a 1D board throughout the entire program is one way
    #to make the code more efficient.
    #Calculate amount of material on both sides and the number of moves
    #played so far in order to determine game phase:
    whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
    blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
    numofmoves = len(position.gethistory())
    gamephase = 'opening'
    if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
        gamephase = 'ending'
    #A note again: Determining game phase is again one the attempts
    #to make the AI smarter when analysing boards and has not been 
    #implemented to its full potential.
    #Calculate number of doubled, blocked, and isolated pawns for 
    #both sides:
    Dw = doubledPawns(board,'white')
    Db = doubledPawns(board,'black')
    Sw = blockedPawns(board,'white')
    Sb = blockedPawns(board,'black')
    Iw = isolatedPawns(board,'white')
    Ib = isolatedPawns(board,'black')
    #Evaluate position based on above data:
    evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb
                )+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib
                )
    #Evaluate position based on piece square tables:
    evaluation2 = pieceSquareTable(flatboard,gamephase)
    #Sum the evaluations:
    evaluation = evaluation1 + evaluation2
    #Return it:
    return evaluation
def pieceSquareTable(flatboard,gamephase):
    #Initialize score:
    score = 0
    #Go through each square:
    for i in range(64):
        if flatboard[i]==0:
            #Empty square
            continue
        #Get data:
        piece = flatboard[i][0]
        color = flatboard[i][1]
        sign = +1
        #Adjust index if black piece, since piece sqaure tables
        #were designed for white:
        if color=='b':
            i = (7-i//8)*8 + i%8
            sign = -1
        #Adjust score:
        if piece=='P':
            score += sign*pawn_table[i]
        elif piece=='N':
            score+= sign*knight_table[i]
        elif piece=='B':
            score+=sign*bishop_table[i]
        elif piece=='R':
            score+=sign*rook_table[i]
        elif piece=='Q':
            score+=sign*queen_table[i]
        elif piece=='K':
            #King has different table values based on phase
            #of the game:
            if gamephase=='opening':
                score+=sign*king_table[i]
            else:
                score+=sign*king_endgame_table[i]
    return score  
def doubledPawns(board,color):
    color = color[0]
    #Get indices of pawns:
    listofpawns = lookfor(board,'P'+color)
    #Count the number of doubled pawns by counting occurences of
    #repeats in their x-coordinates:
    repeats = 0
    temp = []
    for pawnpos in listofpawns:
        if pawnpos[0] in temp:
            repeats = repeats + 1
        else:
            temp.append(pawnpos[0])
    return repeats
def blockedPawns(board,color):
    color = color[0]
    listofpawns = lookfor(board,'P'+color)
    blocked = 0
    #Self explanatory:
    for pawnpos in listofpawns:
        if ((color=='w' and isOccupiedby(board,pawnpos[0],pawnpos[1]-1,
                                       'black'))
            or (color=='b' and isOccupiedby(board,pawnpos[0],pawnpos[1]+1,
                                       'white'))):
            blocked = blocked + 1
    return blocked
def isolatedPawns(board,color):
    color = color[0]
    listofpawns = lookfor(board,'P'+color)
    #Get x coordinates of all the pawns:
    xlist = [x for (x,y) in listofpawns]
    isolated = 0
    for x in xlist:
        if x!=0 and x!=7:
            #For non-edge cases:
            if x-1 not in xlist and x+1 not in xlist:
                isolated+=1
        elif x==0 and 1 not in xlist:
            #Left edge:
            isolated+=1
        elif x==7 and 6 not in xlist:
            #Right edge:
            isolated+=1
    return isolated

#########MAIN FUNCTION####################################################
#Initialize the board:
board = [ ['Rb', 'Nb', 'Bb', 'Qb', 'Kb', 'Bb', 'Nb', 'Rb'], #8
          ['Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb'], #7
          [  0,    0,    0,    0,    0,    0,    0,    0],  #6
          [  0,    0,    0,    0,    0,    0,    0,    0],  #5
          [  0,    0,    0,    0,    0,    0,    0,    0],  #4
          [  0,    0,    0,    0,    0,    0,    0,    0],  #3
          ['Pw', 'Pw', 'Pw',  'Pw', 'Pw', 'Pw', 'Pw', 'Pw'], #2
          ['Rw', 'Nw', 'Bw',  'Qw', 'Kw', 'Bw', 'Nw', 'Rw'] ]#1
          # a      b     c     d     e     f     g     h

#In chess some data must be stored that is not apparent in the board:
player = 0 #This is the player that makes the next move. 0 is white, 1 is black
castling_rights = [[True, True],[True, True]]
#The above stores whether or not each of the players are permitted to castle on
#either side of the king. (Kingside, Queenside)
En_Passant_Target = -1 #This variable will store a coordinate if there is a square that can be
                       #en passant captured on. Otherwise it stores -1, indicating lack of en passant
                       #targets. 
half_move_clock = 0 #This variable stores the number of reversible moves that have been played so far.
#Generate an instance of GamePosition class to store the above data:
position = GamePosition(board,player,castling_rights,En_Passant_Target
                        ,half_move_clock)
#Store the piece square tables here so they can be accessed globally by pieceSquareTable() function:
pawn_table = [  0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0]
knight_table = [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-90,-30,-30,-30,-30,-90,-50]
bishop_table = [-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-90,-10,-10,-90,-10,-20]
rook_table = [0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0]
queen_table = [-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, 70, -5,-10,-10,-20]
king_table = [-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20]
king_endgame_table = [-50,-40,-30,-20,-20,-30,-40,-50,
-30,-20,-10,  0,  0,-10,-20,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-30,  0,  0,  0,  0,-30,-30,
-50,-30,-30,-30,-30,-30,-30,-50]

#Make the GUI:
#Start pygame
pygame.init()
#Load the screen with any arbitrary size for now:
screen = pygame.display.set_mode((600,600))

#Load all the images:
#Load the background chess board image:
background = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\board.png').convert()
#Load an image with all the pieces on it:
pieces_image = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\Chess_Pieces_Sprite.png').convert_alpha()
circle_image_green = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\green_circle_small.png').convert_alpha()
circle_image_capture = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\green_circle_neg.png').convert_alpha()
circle_image_red = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\red_circle_big.png').convert_alpha()
greenbox_image = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\green_box.png').convert_alpha()
circle_image_yellow = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\yellow_circle_big.png').convert_alpha()
circle_image_green_big = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\green_circle_big.png').convert_alpha()
yellowbox_image = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\yellow_box.png').convert_alpha()
#Menu pictures:
withfriend_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\withfriend.png').convert_alpha()
withAI_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\withAI.png').convert_alpha()
playwhite_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\playWhite.png').convert_alpha()
playblack_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\playBlack.png').convert_alpha()
flipEnabled_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\playBlack.png').convert_alpha()
flipDisabled_pic = pygame.image.load(r'C:\Users\Nanditha\Downloads\CHESS_GAME_IN_PYTHON_WITH_SOURCE_CODE\ChessGame_PYTHON\Chess\Media\flipDisabled.png').convert_alpha()

#Getting sizes:
#Get background size:
size_of_bg = background.get_rect().size
#Get size of the individual squares
square_width = size_of_bg[0]//8
square_height = size_of_bg[1]//8


#Rescale the images so that each piece can fit in a square:

pieces_image = pygame.transform.scale(pieces_image,
                                      (square_width*6,square_height*2))
circle_image_green = pygame.transform.scale(circle_image_green,
                                      (square_width, square_height))
circle_image_capture = pygame.transform.scale(circle_image_capture,
                                      (square_width, square_height))
circle_image_red = pygame.transform.scale(circle_image_red,
                                      (square_width, square_height))
greenbox_image = pygame.transform.scale(greenbox_image,
                                      (square_width, square_height))
yellowbox_image = pygame.transform.scale(yellowbox_image,
                                      (square_width, square_height))
circle_image_yellow = pygame.transform.scale(circle_image_yellow,
                                             (square_width, square_height))
circle_image_green_big = pygame.transform.scale(circle_image_green_big,
                                             (square_width, square_height))
withfriend_pic = pygame.transform.scale(withfriend_pic,
                                      (square_width*4,square_height*4))
withAI_pic = pygame.transform.scale(withAI_pic,
                                      (square_width*4,square_height*4))
playwhite_pic = pygame.transform.scale(playwhite_pic,
                                      (square_width*4,square_height*4))
playblack_pic = pygame.transform.scale(playblack_pic,
                                      (square_width*4,square_height*4))
flipEnabled_pic = pygame.transform.scale(flipEnabled_pic,
                                      (square_width*4,square_height*4))
flipDisabled_pic = pygame.transform.scale(flipDisabled_pic,
                                      (square_width*4,square_height*4))



#Make a window of the same size as the background, set its title, and
#load the background image onto it (the board):
screen = pygame.display.set_mode(size_of_bg)
pygame.display.set_caption('Shallow Green')
screen.blit(background,(0,0))

#Generate a list of pieces that should be drawn on the board:
listofWhitePieces,listofBlackPieces = createPieces(board)
#(the list contains references to objects of the class Piece)
#Initialize a list of shades:
listofShades = []

clock = pygame.time.Clock() #Helps controlling fps of the game.
isDown = False #Variable that shows if the mouse is being held down
               #onto a piece 
isClicked = False #To keep track of whether a piece was clicked in order
#to indicate intention to move by the user.
isTransition = False #Keeps track of whether or not a piece is being animated.
isDraw = False #Will store True if the game ended with a draw
chessEnded = False #Will become True once the chess game ends by checkmate, stalemate, etc.
isRecord = False #Set this to True if you want to record moves to the Opening Book. Do not
#set this to True unless you're 100% sure of what you're doing. The program will never modify
#this value.
isAIThink = False #Stores whether or not the AI is calculating the best move to be played.
# Initialize the opening book dictionary, and set its values to be lists by default:
openings = defaultdict(list)
#If openingTable.txt exists, read from it and load the opening moves to the local dictionary.
#If it doesn't, create a new one to write to if Recording is enabled:
try:
    file_handle = open('openingTable.txt','r+')
    openings = pickle.loads(file_handle.read())
except:
    if isRecord:
        file_handle = open('openingTable.txt','w')

searched = {} #Global variable that allows negamax to keep track of nodes that have
#already been evaluated.
prevMove = [-1,-1,-1,-1] #Also a global varible that stores the last move played, to 
#allow drawBoard() to create Shades on the squares.
#Initialize some more values:
#For animating AI thinking graphics:
ax,ay=0,0
numm = 0
#For showing the menu and keeping track of user choices:
isMenu = True
isAI = -1
isFlip = -1
AIPlayer = -1
#Finally, a variable to keep false until the user wants to quit:
gameEnded = False
#########################INFINITE LOOP#####################################
#The program remains in this loop until the user quits the application
while not gameEnded:
    if isMenu:
        #Menu needs to be shown right now.
        #Blit the background:
        screen.blit(background,(0,0))
        if isAI==-1:
            #The user has not selected between playing against the AI
            #or playing against a friend.
            #So allow them to choose between playing with a friend or the AI:
            screen.blit(withfriend_pic,(0,square_height*2))
            screen.blit(withAI_pic,(square_width*4,square_height*2))
        elif isAI==True:
            #The user has selected to play against the AI.
            #Allow the user to play as white or black:
            screen.blit(playwhite_pic,(0,square_height*2))
            screen.blit(playblack_pic,(square_width*4,square_height*2))
        elif isAI==False:
            #The user has selected to play with a friend.
            #Allow choice of flipping the board or not flipping the board:
            screen.blit(flipDisabled_pic,(0,square_height*2))
            screen.blit(flipEnabled_pic,(square_width*4,square_height*2))
        if isFlip!=-1:
            #All settings have already been specified.
            #Draw all the pieces onto the board:
            drawBoard()
            #Don't let the menu ever appear again:
            isMenu = False
            #In case the player chose to play against the AI and decided to 
            #play as black, call upon the AI to make a move:
            if isAI and AIPlayer==0:
                colorsign=1
                bestMoveReturn = []
                move_thread = threading.Thread(target = negamax,
                            args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                isAIThink = True
            continue
        for event in pygame.event.get():
            #Handle the events while in menu:
            if event.type==QUIT:
                #Window was closed.
                gameEnded = True
                break
            if event.type == MOUSEBUTTONUP:
                #The mouse was clicked somewhere.
                #Get the coordinates of click:
                pos = pygame.mouse.get_pos()
                #Determine if left box was clicked or right box.
                #Then choose an appropriate action based on current
                #state of menu:
                if (pos[0]<square_width*4 and
                pos[1]>square_height*2 and
                pos[1]<square_height*6):
                    #LEFT SIDE CLICKED
                    if isAI == -1:
                        isAI = False
                    elif isAI==True:
                        AIPlayer = 1
                        isFlip = False
                    elif isAI==False:
                        isFlip = False
                elif (pos[0]>square_width*4 and
                pos[1]>square_height*2 and
                pos[1]<square_height*6):
                    #RIGHT SIDE CLICKED
                    if isAI == -1:
                        isAI = True
                    elif isAI==True:
                        AIPlayer = 0
                        isFlip = False
                    elif isAI==False:
                        isFlip=True

        #Update the display:
        pygame.display.update()

        #Run at specific fps:
        clock.tick(60)
        continue
    #Menu part was done if this part reached.
    #If the AI is currently thinking the move to play
    #next, show some fancy looking squares to indicate
    #that.
    #Do it every 6 frames so it's not too fast:
    numm+=1
    if isAIThink and numm%6==0:
        ax+=1
        if ax==8:
            ay+=1
            ax=0
        if ay==8:
            ax,ay=0,0
        if ax%4==0:
            createShades([])
        #If the AI is white, start from the opposite side (since the board is flipped)
        if AIPlayer==0:
            listofShades.append(Shades(greenbox_image,(7-ax,7-ay)))
        else:
            listofShades.append(Shades(greenbox_image,(ax,ay)))
    
    for event in pygame.event.get():
        #Deal with all the user inputs:
        if event.type==QUIT:
            #Window was closed.
            gameEnded = True
        
            break
        #Under the following conditions, user input should be
        #completely ignored:
        if chessEnded or isTransition or isAIThink:
            continue
        #isDown means a piece is being dragged.
        if not isDown and event.type == MOUSEBUTTONDOWN:
            #Mouse was pressed down.
            #Get the oordinates of the mouse
            pos = pygame.mouse.get_pos()
            #convert to chess coordinates:
            chess_coord = pixel_coord_to_chess(pos)
            x = chess_coord[0]
            y = chess_coord[1]
            #If the piece clicked on is not occupied by your own piece,
            #ignore this mouse click:
            if not isOccupiedby(board,x,y,'wb'[player]):
                continue
            #Now we're sure the user is holding their mouse on a 
            #piecec that is theirs.
            #Get reference to the piece that should be dragged around or selected:
            dragPiece = getPiece(chess_coord)
            #Find the possible squares that this piece could attack:
            listofTuples = findPossibleSquares(position,x,y)
            #Highlight all such squares:
            createShades(listofTuples)
            #A green box should appear on the square which was selected, unless
            #it's a king under check, in which case it shouldn't because the king
            #has a red color on it in that case.
            if ((dragPiece.pieceinfo[0]=='K') and
                (isCheck(position,'white') or isCheck(position,'black'))):
                None
            else:
                listofShades.append(Shades(greenbox_image,(x,y)))
            #A piece is being dragged:
            isDown = True       
        if (isDown or isClicked) and event.type == MOUSEBUTTONUP:
            #Mouse was released.
            isDown = False
            #Snap the piece back to its coordinate position
            dragPiece.setpos((-1,-1))
            #Get coordinates and convert them:
            pos = pygame.mouse.get_pos()
            chess_coord = pixel_coord_to_chess(pos)
            x2 = chess_coord[0]
            y2 = chess_coord[1]
            #Initialize:
            isTransition = False
            if (x,y)==(x2,y2): #NO dragging occured 
                #(ie the mouse was held and released on the same square)
                if not isClicked: #nothing had been clicked previously
                    #This is the first click
                    isClicked = True
                    prevPos = (x,y) #Store it so next time we know the origin
                else: #Something had been clicked previously
                    #Find out location of previous click:
                    x,y = prevPos
                    if (x,y)==(x2,y2): #User clicked on the same square again.
                        #So 
                        isClicked = False
                        #Destroy all shades:
                        createShades([])
                    else:
                        #User clicked elsewhere on this second click:
                        if isOccupiedby(board,x2,y2,'wb'[player]):
                            #User clicked on a square that is occupied by their
                            #own piece.
                            #This is like making a first click on your own piece:
                            isClicked = True
                            prevPos = (x2,y2) #Store it
                        else:
                            #The user may or may not have clicked on a valid target square.
                            isClicked = False
                            #Destory all shades
                            createShades([])
                            isTransition = True #Possibly if the move was valid.
                            

            if not (x2,y2) in listofTuples:
                #Move was invalid
                isTransition = False
                continue
            #Reaching here means a valid move was selected.
            #If the recording option was selected, store the move to the opening dictionary:
            if isRecord:
                key = pos2key(position)
                #Make sure it isn't already in there:
                if [(x,y),(x2,y2)] not in openings[key]: 
                    openings[key].append([(x,y),(x2,y2)])
                
            #Make the move:
            makemove(position,x,y,x2,y2)
            #Update this move to be the 'previous' move (latest move in fact), so that
            #yellow shades can be shown on it.
            prevMove = [x,y,x2,y2]
            #Update which player is next to play:
            player = position.getplayer()
            #Add the new position to the history for it:
            position.addtoHistory(position)
            #Check for possibilty of draw:
            HMC = position.getHMC()
            if HMC>=100 or isStalemate(position) or position.checkRepition():
                #There is a draw:
                isDraw = True
                chessEnded = True
            #Check for possibilty of checkmate:
            if isCheckmate(position,'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position,'black'):
                winner = 'w'
                chessEnded = True
            #If the AI option was selecteed and the game still hasn't finished,
            #let the AI start thinking about its next move:
            if isAI and not chessEnded:
                if player==0:
                    colorsign = 1
                else:
                    colorsign = -1
                bestMoveReturn = []
                move_thread = threading.Thread(target = negamax,
                            args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                isAIThink = True
            #Move the piece to its new destination:
            dragPiece.setcoord((x2,y2))
            #There may have been a capture, so the piece list should be regenerated.
            #However, if animation is ocurring, the the captured piece should still remain visible.
            if not isTransition:
                listofWhitePieces,listofBlackPieces = createPieces(board)
            else:
                movingPiece = dragPiece
                origin = chess_coord_to_pixels((x,y))
                destiny = chess_coord_to_pixels((x2,y2))
                movingPiece.setpos(origin)
                step = (destiny[0]-origin[0],destiny[1]-origin[1])
            
            #Either way shades should be deleted now:
            createShades([])
    #If an animation is supposed to happen, make it happen:
    if isTransition:
        p,q = movingPiece.getpos()
        dx2,dy2 = destiny
        n= 30.0
        if abs(p-dx2)<=abs(step[0]/n) and abs(q-dy2)<=abs(step[1]/n):
            #The moving piece has reached its destination:
            #Snap it back to its grid position:
            movingPiece.setpos((-1,-1))
            #Generate new piece list in case one got captured:
            listofWhitePieces,listofBlackPieces = createPieces(board)
            #No more transitioning:
            isTransition = False
            createShades([])
        else:
            #Move it closer to its destination.
            movingPiece.setpos((p+step[0]/n,q+step[1]/n))
    #If a piece is being dragged let the dragging piece follow the mouse:
    if isDown:
        m,k = pygame.mouse.get_pos()
        dragPiece.setpos((m-square_width/2,k-square_height/2))
    #If the AI is thinking, make sure to check if it isn't done thinking yet.
    #Also, if a piece is currently being animated don't ask the AI if it's
    #done thining, in case it replied in the affirmative and starts moving 
    #at the same time as your piece is moving:
    if isAIThink and not isTransition:
        if not move_thread.isAlive():
            #The AI has made a decision.
            #It's no longer thinking
            isAIThink = False
            #Destroy any shades:
            createShades([])
            #Get the move proposed:
            [x,y],[x2,y2] = bestMoveReturn
            #Do everything just as if the user made a move by click-click movement:
            makemove(position,x,y,x2,y2)
            prevMove = [x,y,x2,y2]
            player = position.getplayer()
            HMC = position.getHMC()
            position.addtoHistory(position)
            if HMC>=100 or isStalemate(position) or position.checkRepition():
                isDraw = True
                chessEnded = True
            if isCheckmate(position,'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position,'black'):
                winner = 'w'
                chessEnded = True
            #Animate the movement:
            isTransition = True
            movingPiece = getPiece((x,y))
            origin = chess_coord_to_pixels((x,y))
            destiny = chess_coord_to_pixels((x2,y2))
            movingPiece.setpos(origin)
            step = (destiny[0]-origin[0],destiny[1]-origin[1])

    #Update positions of all images:
    drawBoard()
    #Update the display:
    pygame.display.update()

    #Run at specific fps:
    clock.tick(60)

#Out of loop. Quit pygame:
pygame.quit()
#In case recording mode was on, save the openings dictionary to a file:
if isRecord:
    file_handle.seek(0)
    pickle.dump(openings,file_handle)
    file_handle.truncate()
    file_handle.close()

                
