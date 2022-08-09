# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ # 
# | Author: Faraz Borghei       | #
# | Date Created: June 18, 2020 | #
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ # 

import time, random

class TicTacToe():
    ''' Player vs CPU TicTacToe game (Impossible Mode).
    CPU Performs random playouts on all legal moves based on a given board state. 
    The CPU will never lose a game, thus resulting in a loss or stalemate for the Player every time.
    
    The CPU uses Pure Monte Carlo Tree Search (MCTS) to perform random playouts and record win/loss/draw statistics.
    Default number of iterations is 5000 playouts per available move. '''
    def __init__(self, **kwargs):
        self._board = {i: ' ' for i in range(9)}
        self._player_piece = 'X'
        self._cpu_piece = 'O'
        self._finished = False
        self._occupied = set()
        self._cyan = '\u001b[36;1m'
        self._red = '\u001b[31m'
        self._green= '\u001b[32m'
        self._blue = '\u001b[34m'
        self._reset = '\u001b[0m'
        self.title_screen()
        # MAIN GAME LOOP
        while not self._finished:
            self.print_board(self._board)
            turn = self.actions(self._board)
            if turn == 'X': self.user_input()
            else: self.cpu_turn(100, False)
            self.state = self.check_state(self._board, main=True)
            if self.state == 'X' or self.state == 'O' or self.state == '-': 
                self._finished = True


    def cpu_turn(self, iterations, debug=True):
        ''' Performs random playouts specified by the amount of iterations then
        calculates the best move for the CPU to take based on win/draw/loss statistics 
        **Note: Turning the debug output on will greatly increase running times '''
        win, draw, loss, visited = [], [], [], []
        freqWin, freqDraw, freqLoss, freqVisited, winPercentages = {}, {}, {}, {}, {}
        movesList = self.legal_moves(self._board)
        print(f'CPU performing {iterations} random playouts from current state...')
        for i in range(iterations):
            for move in movesList:
                playouts = self.random_playout(move, win, draw, loss, visited, False)
        
        # Extract the highest frequency of a certain index
        if win: indexToWin = max(win, key=win.count)
        if draw: indexToDraw = max(draw, key=draw.count)
        if loss: indexToLose = max(loss, key=loss.count)
        
        # Populate win/draw/visited frequency dicts
        for item in win:
            if item in freqWin: freqWin[item] += 1     
            else: freqWin[item] = 1
        for item in draw:
            if item in freqDraw: freqDraw[item] += 1
            else: freqDraw[item] = 1
        for item in loss:
            if item in freqLoss: freqLoss[item] += 1
            else: freqLoss[item] = 1
        for item in visited:
            if item in freqVisited: freqVisited[item] += 1
            else: freqVisited[item] = 1

        # Print the frequency lists for win/draw/visited
        if debug:
            print(f'Available Moves: {movesList}')
            print('WIN FREQ')
            for key, value in freqWin.items():
                print(key, value)
            print('DRAW FREQ')
            for key, value in freqDraw.items():
                print(key, value)
            print('LOSS FREQ')
            for key, value in freqLoss.items():
                print(key, value)
            print('VISITED FREQ')
            for key, value in freqVisited.items():
                print(key, value)

        # Determine win percentage of each move based on the amount of (wins + draws) / visited
        for i, (k, v) in enumerate(freqVisited.items()):
            if freqWin.get(k) and freqDraw.get(k):
                winPercentages[k] = (freqWin[k] + freqDraw[k])/freqVisited[k]
                continue
            if freqWin.get(k): 
                winPercentages[k] = freqWin[k]/freqVisited[k]
                continue
            if freqDraw.get(k): 
                winPercentages[k] = freqDraw[k]/freqVisited[k]
                continue

        # Take the highest frequency index as best play for current state
        bestPlay = max(winPercentages, key=winPercentages.get)
        
        if win and draw and loss and debug: 
            debugOutput = f'\nINDEX TO WIN: {indexToWin}, length of win list: {len(win)}\n'\
                f'INDEX TO DRAW: {indexToDraw}, length of draw list: {len(draw)}\n'\
                f'INDEX TO LOSE: {indexToLose}, length of loss list: {len(loss)}\n'\
                f'Length of visited list {len(visited)}\n'\
                f'Best Play: {bestPlay}\n'\
                f'Win Percentages: {winPercentages}\n\n'
            print(debugOutput)

        print(f'After {iterations} Random playouts, CPU determined index {self._cyan}#{bestPlay}{self._reset} as the best play.')
        self.set_index(bestPlay, self._cpu_piece)


    def random_playout(self, init_move, win, draw, loss, visited, debug=True):
        ''' Simulates a gam from init_move to completion and records win/draw/loss statistics.
        
            1. Get action list - whos turn it is
            2. Get list of legal moves from current position
            3. Randomly choose from the moves list and change playout board based on new move '''
        playout_board = {}
        # copy current board state to a separate playout board
        for i, (k, v) in enumerate(self._board.items()): playout_board[k] = v 
        
        # set first initial move and then perform random playout from this state
        playout_board[init_move] = self._cpu_piece 
        
        # Perform random legal moves for each piece until game has ended
        while(True):
            check_state = self.check_state(playout_board)
            if debug: print('state:', check_state)
            if check_state == 'O': 
                win.append(init_move)
                break
            if check_state == '-':
                draw.append(init_move)
                break
            if check_state == 'X': 
                loss.append(init_move)
                break
            action = self.actions(playout_board)
            moves = self.legal_moves(playout_board)
            indexChoice = random.choice(moves)
            playout_board[indexChoice] = action
            visited.append(indexChoice)
        if debug: 
            print('Won Moves:', win)
            print('Draw Moves:', draw)
            print('Loss Moves:', loss)


    def actions(self, board):
        ''' Returns which action to take based on number of empty spots on the given board
            We know (or assume) that player ('X') always starts, therefore:
                If number of empty spots is ODD, then it is the Player's turn
                If number of empty spots is EVEN, then it is the CPU's turn '''
        emptyCount = 0
        for i, (index, letter) in enumerate(board.items()):
            if letter == ' ': emptyCount += 1

        return 'X' if emptyCount % 2 == 1 else 'O'


    def legal_moves(self, board):
        ''' Return list of all legal moves based on current board state.
        Checks for any spots that are empty and returns the location. '''
        legal_moves = [index for i, (index, letter) in enumerate(board.items()) if letter == ' ']
        return legal_moves


    def set_index(self, index, value):
        self._board[index] = value
        self._occupied.add(index)


    def game_end_animation(self, value):
        ''' Animation to show which piece won after game ends '''
        self.print_board(self._board)

        playerColor = [self._red, self._reset]
        cpuColor = [self._blue, self._reset]
        drawColor = [self._cyan, self._reset]

        for i in range(5):
            if value == self._player_piece:
                print(f'{playerColor[i % 2]}PLAYER WINS', end='\r')
            if value == self._cpu_piece:
                print(f'{cpuColor[i % 2]}CPU WINS', end='\r')
            if value == '-':
                print(f'{cpuColor[i % 2]}GAME DRAW', end='\r')

            time.sleep(0.3)


    def check_state(self, board, main=False):
        ''' Checks if the game has ended. 
        Returns '0' if player has won, '1' if CPU has won, and '-1' if draw '''
        # FIRST ROW
        if board[0] == 'X' and board[1] == 'X' and board[2] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[0] == 'O' and board[1] == 'O' and board[2] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # SECOND ROW
        if board[3] == 'X' and board[4] == 'X' and board[5] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[3] == 'O' and board[4] == 'O' and board[5] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # THIRD ROW
        if board[6] == 'X' and board[7] == 'X' and board[8] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[6] == 'O' and board[7] == 'O' and board[8] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # FIRST COLUMN
        if board[0] == 'X' and board[3] == 'X' and board[6] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[0] == 'O' and board[3] == 'O' and board[6] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # SECOND COLUMN
        if board[1] == 'X' and board[4] == 'X' and board[7] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[1] == 'O' and board[4] == 'O' and board[7] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # THIRD COLUMN
        if board[2] == 'X' and board[5] == 'X' and board[8] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[2] == 'O' and board[5] == 'O' and board[8] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
            
        # DIAGONAL
        if board[0] == 'X' and board[4] == 'X' and board[8] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[0] == 'O' and board[4] == 'O' and board[8] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'

        if board[2] == 'X' and board[4] == 'X' and board[6] == 'X':
            if main: self.game_end_animation(self._player_piece)
            return 'X'
            
        if board[2] == 'O' and board[4] == 'O' and board[6] == 'O':
            if main: self.game_end_animation(self._cpu_piece)
            return 'O'
        
        # BOARD FULL
        if ' ' not in board.values():
            if main: self.game_end_animation('-')
            return '-'
            

    def user_input(self):
        ''' Get user input and validate through exceptions '''
        while True:
            try:
                user_index = int(input('Desired Index: '))
                if user_index in self._occupied: raise IndexError(f'Index #{user_index} is already occupied')
                if user_index not in range(9): raise IndexError(f'Index #{user_index} is out of range')

            except IndexError as e:
                print(f'ERROR: {e} \nPlease select another index.\n')
            except ValueError as e:
                print(f'ERROR: {e} \nPlease select another index.\n')
            
            else: 
                self.set_index(int(user_index), self._player_piece)
                break


    def print_board(self, board):
        ''' Print specified board in prettified way '''
        print(f'\nPlayer: {self._red}{self._player_piece}{self._reset} | CPU: {self._blue}{self._cpu_piece}{self._reset}')
        print('+-----------+')
        for i, (k, v) in enumerate(board.items()):
            if not i % 3 and i != 0: print('|')
            print('|', end=' ')
            if board[i] == ' ': print(i, end=' ')
            if board[i] == self._player_piece: 
                print(f'{self._red}{board[i]}{self._reset}', end=' ')
            if board[i] == self._cpu_piece: 
                print(f'{self._blue}{board[i]}{self._reset}', end=' ')
        print('|')
        print('+-----------+\n')


    def title_screen(self):
        ''' Main title screen shown at start of application '''
        titleStr = f'{self._cyan}   ____  __  ___    ____  __    ___    ____  __  ____ \n'\
            '  (_  _)(  )/ __)  (_  _)/ _\  / __)  (_  _)/  \(  __)\n'\
            '    )(   )(( (__     )( /    \( (__     )( (  O )) _) \n'\
            f'   (__) (__)\___)   (__)\_/\_/ \___)   (__) \__/(____){self._green}\n\n'\
            '+ Author: Faraz Borghei\n'\
            f'+ Date Created: June 18, 2020{self._reset}\n'\
            '\nWelcome to the impossible TicTacToe game you will never win!\n\n'\
            'This program uses Monte Carlo Tree Search to play the game as CPU. Default iteration number is 5000.\n'\
            '*Note: The numbers inside the board grid reprsent their index # to enter.\n\n'\
            'Please choose an appropriate index within the range 0 - 8.\n'
        print(titleStr)


if __name__ == '__main__':
    TicTacToe()