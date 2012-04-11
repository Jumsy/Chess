#A program for playing chess by James

class Piece:
    def __init__(self, type, color):
        self.type = type
        self.color = color


class Board:
    def __init__(self):
        light_square = ' '
        dark_square = '='
        self.board = {}
        for x in range(1, 9):
            for y in range(1, 9):
                if (x + y)%2:
                    self.board[(x, y)] = dark_square
                else:
                    self.board[(x, y)] = light_square
        self.setup_pieces()

    def setup_pieces(self):
        self.pieces = {}
        home_row = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i, piece in enumerate(home_row):
            x = i + 1
            self.pieces[(x, 1)] = Piece(piece, 'White')
            self.pieces[(x, 2)] = Piece('P', 'White')
            self.pieces[(x, 7)] = Piece('P', 'Black')
            self.pieces[(x, 8)] = Piece(piece, 'Black')

    def display(self, side):
        if side%2: #White's turn
            range_x = list(range(1, 9))
            range_y = list(reversed(range(1, 9)))
        else: #Black's turn
            range_x = list(reversed(range(1, 9)))
            range_y = list(range(1, 9))

        print(' ' + '_' * 10)
        for y in range_y:
            line = ''
            for x in range_x:
                location = (x, y)
                if location in self.pieces:
                    line = line + self.pieces[location].type
                    if self.pieces[location].color == 'Black':
                        #All of Black's pieces are lowercase
                        line = line[:-1] + line[-1].lower()
                else:
                    line = line + self.board[(x, y)]
            print(' |' + line + '|')
        print(' ' + '-' * 10 + '\n')

    def move_piece(self, origin, target):
        origin, target = tuple(origin), tuple(target)
        self.pieces[target] = self.pieces[origin]
        del self.pieces[origin]


class Chess:
    def __init__(self):
        self.turn = 1
        self.board = Board()
        self.notation = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}

    def print_board(self):
        self.board.display(self.turn)

    def do_move(self, move):
        '''
        This function takes the move and passes it through a series of
        functions to parse out the specific moves that should be made.
        '''
        move_data = self.parse_move(move)
        possible_origins = self.get_all_origins(move_data)
        actions = self.get_single_origin(possible_origins, move_data)
        if len(actions): self.turn += 1
        for action in actions:
            self.board.move_piece(action[0], action[1])

    def parse_move(self, move):
        '''
        This function takes the player's move passed along as a string.
        It then returns a dictionary full of all relevant parsed data:
            'piece':   The piece the player is moving ('K' if castling)
                       given as one of 'R', 'N', 'B', 'K', 'Q', or 'P'
            'target':  The location of the square the player is
                       attempting to move to in [x, y] format
            'ori_col': Included only when data about the origin column
                       of the active piece can be parsed. Given as int
            'ori_row': Included only when data about the origin row of
                       the active piece can be parsed. Given as int
            'capture': Included only attempting to capture a piece
            'castle':  Included only when attempting to castle
        '''
        parsed_data = {}
        valid_numbers = [ str(x) for x in range(1, 9) ]
        notation = self.notation
        piece_set = ['R', 'N', 'B', 'Q', 'K', 'P']

        if move in ['O-O-O', 'o-o-o', '0-0-0']:
            parsed_data['piece'] = 'K'
            parsed_data['castle'] = 'QS'
            parsed_data['target'] = [3, ((self.turn+1)%2)*7 + 1] #1 or 8

        elif move in ['O-O', 'o-o', '0-0']:
            parsed_data['piece'] = 'K'
            parsed_data['castle'] = 'KS'
            parsed_data['target'] = [7, ((self.turn+1)%2)*7 + 1] #1 or 8

        elif len(move)>1 and move[-1] in valid_numbers and move[-2] in notation:
            parsed_data['target'] = [notation[move[-2]], int(move[-1])]
            move = move[:-2] #Strip away the target from the end of the move
            if len(move):
                if move[0] in piece_set:
                    parsed_data['piece'] = move[0]
                    move = move[1:] #Strip away the piece from the move
                elif move[0] in notation:
                    parsed_data['piece'] = 'P'
                for character in move:
                    if character == 'x':
                        parsed_data['capture'] = True
                    elif character in notation:
                        parsed_data['ori_col'] = notation[character]
                    elif character in valid_numbers:
                        parsed_data['ori_row'] = int(character)
            else:
                parsed_data['piece'] = 'P'
                parsed_data['ori_col'] = parsed_data['target'][0]

        return parsed_data

    def get_all_origins(self, parsed_data):
        '''
        Takes a dictionary containing all the data parsed from the
        move and returns a list containing all the possible
        locations that the piece could have originated from given
        in [[x, y], [x, y], [x,y]] format.
        For pieces that move a set distance from themselves, a list
        containing the offset of each move relative to the target
        square.
        For pieces that move in a direction, a list containing the
        directions is set.
        After move_offset or move_dirs has been set, all relative
        locations are converted to absolute locations on the board
        and the values are returned.
        '''
        possible_origins = []
        if 'target' not in parsed_data or 'piece' not in parsed_data:
            return possible_origins

        valid_numbers = [ x for x in range(1, 9) ]
        piece = parsed_data['piece']
        target = parsed_data['target']
        move_offset = []
        move_dirs = []

        if piece == 'P':
            if self.turn%2: #White's turn
                pawn_direction = -1
            else: #Black's turn
                pawn_direction = 1
            if 'capture' in parsed_data:
                move_offset = [[-1, pawn_direction], [1, pawn_direction]]
            elif 'ori_col' in parsed_data:
                move_offset = [[0, pawn_direction * 2], [0, pawn_direction]]

        elif piece == 'K':
            if 'castle' in parsed_data:
                if self.turn%2:
                     possible_origins.append([5, 1])
                else:
                     possible_origins.append([5, 8])
            else:
                move_offset = [ [-1, 1],  [0, 1],  [1, 1],
                                [-1, 0],           [1, 0],
                                [-1, -1], [0, -1], [1, -1] ]
        
        elif piece == 'N':
            move_offset = [       [-1, 2],      [1, 2],
                           [-2, 1],                    [2, 1],
                           [-2, -1],                   [2, -1],
                                  [-1, -2],     [1, -2]         ]

        elif piece == 'R' or piece == 'Q':
            for direction in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                move_dirs.append(direction)
        
        if piece == 'B' or piece == 'Q':
            for direction in [[-1, 1], [1, 1], [-1, -1], [1, -1]]:
                move_dirs.append(direction)
        
        for offset in move_offset:
            x = offset[0] + target[0]
            y = offset[1] + target[1]
            if x in valid_numbers and y in valid_numbers:
                location = (x, y)
                if location in self.board.pieces:
                    if self.board.pieces[location].type == piece:
                        possible_origins.append([x, y])

        for dir in move_dirs:
            x = dir[0] + target[0]
            y = dir[1] + target[1]
            while x in valid_numbers and y in valid_numbers:
                location = (x, y)
                if location in self.board.pieces:
                    if self.board.pieces[location].type == piece:
                        possible_origins.append([x, y])
                x += dir[0]
                y += dir[1]

        return possible_origins

    def get_single_origin(self, possible_origins, parsed_data):
        '''
        This takes a list of the possible origins of the active piece
        and attempts to determine if any of them are valid moves. If
        only one valid move is found, then a list all the pieces to
        move is returned as [ [ [move1_ori_x, move1_ori_y],
                                [move1_tar_x, move1_tar_y] ],
                              [ [move2_ori_x, move2_ori_y],
                                [move2_tar_x, move2_tar_y] ] ]
        There should only be more than one piece to move when castling.
        If the number of valid moves is not equal to one, then it gets
        printed so the player knows why the move failed.

        What I need to do here is check that the move is consistent
        with all of the data in parsed_move. I also need to check
        that players move their own pieces and capture only enemy
        pieces. There also needs to be collision detection for the
        Queen, Rook, Bishop and Pawn. Finally, I imagine I'll need
        castle-checking in here.
        '''               
        if self.turn%2: #White's turn
            friendly = 'White'
            enemy = 'Black'
        else:
            friendly = 'Black'
            enemy = 'White'
        moves = []
        parsed_origins = []
        
        if tuple(parsed_data['target']) in self.board.pieces:
            target_square = self.board.pieces[tuple(parsed_data['target'])].color
        else:
            target_square = ' '
        
        for origin in possible_origins:
            if 'ori_col' in parsed_data and parsed_data['ori_col'] != origin[0]:
                continue
            if 'ori_row' in parsed_data and parsed_data['ori_row'] != origin[1]:
                continue
            if 'capture' not in parsed_data and target_square != ' ':
                continue
            if target_square == friendly:
                continue
            if self.board.pieces[tuple(origin)] == enemy:
                continue
            parsed_origins.append(origin)
        
        print(parsed_origins)
        if len(parsed_origins) == 1:
            origin = parsed_origins[0]
            target = parsed_data['target']
            moves = [[origin, target]]
        else:
            print("There are", len(parsed_origins), "possible moves")
        return moves


class Play_Game:
    def __init__(self):
        print("Welcome to James' chess program!")
        print("Now starting a new game...")
        self.run_game(Chess())
 
    def run_game(self, game):
        while True:
            print()
            game.print_board()
            
            move = input("Please enter a move: ")
           
            if move == 'q':
                print("Thank you for playing!") 
                return

            game.do_move(move)


Play_Game()
