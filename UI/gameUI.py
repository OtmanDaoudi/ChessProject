import threading
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from functools import partial
from Classes.AiPlayer import AiPlayer
from Classes.Game import Game
from Classes.Piece import Piece
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from kivy.animation import Animation    
from kivy.app import App
from Classes.Knight import Knight
from Classes.Pawn import Pawn
from Classes.Rook import Rook
from Classes.Queen import Queen
from Classes.Bishop import Bishop
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from copy import deepcopy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
import pickle
from Classes.serialisedGame import serialisedGame
import DB.connection as con
from kivy.storage.jsonstore import JsonStore



class Cell(ToggleButton):
    def __init__(self,rank: int,column: int,color: tuple,piece: Piece,**kwargs):
        super().__init__(**kwargs)
        self.piece = piece
        self.rank = rank
        self.column = column
        self.background_normal=''
        self.background_color = color
        self.img = None
        self.firstMake = True
        
    def set_img_pos(self, *args):
        if self.img is not None:
            self.remove_widget(self.img)
        source_ = "./Assets/images/None.png" 
        if self.piece is not None:
            source_ ="./Assets/images/"+self.piece.image
        if self.firstMake:
            self.img = Image(source = source_)
            self.img.opacity = 0
            a = Animation(duration = .3, opacity = 1)
            
            a.start(self.img)
            self.firstMake = False
        else:
            self.img = Image(source = source_)
        self.img.allow_stretch = True
        self.img.pos = [self.pos[0] + 5, self.pos[1]]
        self.img.size = (95,95)
        self.add_widget(self.img)

    def reposition_img(self, *args):
        if self.img is not None:
            self.img.pos = [self.pos[0] + 5, self.pos[1]]

class GameUi(BoxLayout, Screen):
    authType = "Anonymous"
    gameMode = None
    playAs = "w"
    diff = 1
    current_gameui = None
class ChessBoard(GridLayout):
    thread_flag = "N/A"
    current_game = None
    loaded_game = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if ChessBoard.loaded_game is not None:
            GameUi.gameMode = ChessBoard.loaded_game.gameMode

            old_diff = GameUi.diff 
            GameUi.diff = ChessBoard.loaded_game.diff

            GameUi.playAs = ChessBoard.loaded_game.playas
            # print("play as ",ChessBoard.loaded_game.playas)

            # print("turn ",ChessBoard.loaded_game.turn)

            turn = "w" if ChessBoard.loaded_game.turn == "b" else "b"
            self.game = Game(self, turn)
            Clock.schedule_once(partial(self.game.switchTurnes, GameUi.playAs == "w" and self.game.turn == "w"))
            Clock.schedule_once(self.game.updateClockLabelOnLoad)
            Clock.schedule_once(self.update_score)
            ChessBoard.current_game = self.game
            self.game.game_board = ChessBoard.loaded_game.game_board
            self.game.game_status = ChessBoard.loaded_game.game_status
            self.game.white_timer = ChessBoard.loaded_game.white_timer
            self.game.black_timer = ChessBoard.loaded_game.black_timer

            GameUi.diff = old_diff
            # print("restores old diff to ", GameUi.diff)
        else:
            self.game = Game(self)
            ChessBoard.current_game = self.game
        ChessBoard.loaded_game = None

        self.undo_stack = []
        self.redo_stack = []

        self.selected_cell = None
        self.marked_moved = []

        self.cols = 8
        self.rows = 9
        self.padding = -1
        self.spacing = -2

        light_square = (242/255.0, 225/255.0, 195/255.0, 1)
        dark_square  = (195/255.0, 160/255.0, 130/255.0, 1)
        current_color = light_square

        self.cells = [] #stores grid cells
        for _ in range(8):
            self.cells.append([None, None, None, None, None, None, None, None])

        for rank in reversed(range(8)):
            for column in range(8):
                newCell = Cell(rank,column,current_color,self.game.game_board.board[rank][column])
                newCell.on_press = partial(self.selected, rank, column, newCell)
                self.cells[rank][column] = newCell
                self.add_widget(newCell)
                Clock.schedule_once(newCell.set_img_pos, 1)
                newCell.bind(pos=newCell.reposition_img)
                if current_color == light_square:
                    current_color = dark_square
                else: 
                    current_color = light_square
            if current_color == light_square:
                    current_color = dark_square
            else: 
                current_color = light_square
        self.move_piece_sound = SoundLoader.load('./Assets/audio/piece_move.wav')
        
        #schedule clock updates
        self.clocks_job = Clock.schedule_interval(self.game.update_clocks, 1)
        Clock.schedule_once(self.setBtns)

        if isinstance(self.game.white_player, AiPlayer):
            #make the algorithm go firs
            Clock.schedule_once(self.AiMoveThread, 1)
            
        Clock.schedule_once(self.init_names)


    def init_names(self, *agrs):
        #set player names
        if GameUi.gameMode == "PvP":
            if GameUi.authType == "Auth":
                #increment total player for both players
                con.Connection.increment_total_played()
                stored_data = JsonStore('data.json')
                black_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.black_player_banner
                white_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.white_player_banner
                if GameUi.playAs == "w":
                    white_banner.text = stored_data.get('user1')['userName']
                    black_banner.text = stored_data.get('user2')['userName']
                else:
                    black_banner.text = stored_data.get('user1')['userName']
                    white_banner.text = stored_data.get('user2')['userName']    
        else:
            stored_data = JsonStore('data.json')
            if stored_data.exists('user1'):
                #user connected 
                #increment total played
                con.Connection.increment_total_played(); 
                if GameUi.playAs == "w":
                    App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.white_player_banner.text = stored_data.get('user1')['userName']
                else:
                    App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.black_player_banner.text = stored_data.get('user1')['userName']


    def setBtns(self, *args):
        App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.options.ids.go_home.on_press = self.showHome

        self.redo_btn = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.options.ids.redo 
        self.redo_btn.on_press = self.redo
        self.redo_btn.disabled = True

        self.undo_btn = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.options.ids.undo 
        self.undo_btn.on_press = self.undo
        self.undo_btn.disabled = True

    def showHome(self):
        box = BoxLayout(orientation = "vertical")
        vbox = BoxLayout()
        lbl = Label(text="Vous êtes sûr?", size_hint = (1, 0.2), bold = True)
        vbox.add_widget(lbl)

        Boxed_layout= BoxLayout(orientation = "horizontal")
        btn1 = Button(text="Oui", size_hint=(1, .4), bold = True)
        btn2 = Button(text="Non", size_hint=(1, .4) , bold = True)
        Boxed_layout.add_widget(btn1)
        Boxed_layout.add_widget(btn2)
 
        box.add_widget(vbox)
        box.add_widget(Boxed_layout)

        pop = Popup(title="Exit?",content=box, size_hint=(None, None), size = (400, 300), auto_dismiss = False)
        btn1.bind(on_release=partial(self.apply_exiting, pop))
        btn2.bind(on_release=pop.dismiss)
        pop.open()


    def exit(self, *args):
        #check game status before close
        if self.game.game_status.value in (1,6,7):
            #show game save dialogue
            show_popup()
        else:
            #show confirmation diallogue
            btn1 = Button(text="Oui", size_hint=(1, None), height = 80)
            btn2 = Button(text="Non", size_hint=(1, None), height = 80)
            Boxed_layout= BoxLayout(orientation = "horizontal")
            Boxed_layout.add_widget(btn1)
            Boxed_layout.add_widget(btn2)
            pop = Popup(title="Vous êtes sûr?",content=Boxed_layout, size_hint=(.5,.25))
            btn1.bind(on_release=partial(self.apply_exiting, pop))
            # btn1.bind(on_release=partial(doit, pop)) # bind to whatever action is being confiirmed
            btn2.bind(on_release=pop.dismiss)
            pop.open()

    def apply_exiting(self, pop, *args):
        ChessBoard.thread_flag = "ENDED"
        pop.dismiss()
        App.get_running_app().root.current = 'home'
        App.get_running_app().root.remove_widget(GameUi.current_gameui)
        Clock.unschedule(self.clocks_job)

    
    def redo(self, *args):
        # print("redoing...")
        if len(self.redo_stack) > 0:
            redo_entry = self.redo_stack.pop()
            self.undo_stack.append({"board" : deepcopy(self.game.game_board), "game_state" : self.game.game_status})
            # print("available redo : ")
            self.game.game_board = redo_entry["board"]
            self.game.game_status = redo_entry["game_state"]

            #switch turns
            self.game.turn = "b" if self.game.turn == "w" else "w"
            red = (1,0,0,1)
            green = (120/255,238/255,62/255,1)
            black_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.black_player_banner
            white_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.white_player_banner
            FixBox =  App.get_running_app().root.get_screen('gameUi').ids.fixBox

            # switch label background colors
            if self.game.turn == "w":
                black_banner.background_color = red
                FixBox.background_color = red
                white_banner.background_color = green
            else:
                black_banner.background_color = green
                FixBox.background_color = green
                white_banner.background_color = red

            self.update_board()

            # print("done redoing")
            if len(self.redo_stack) == 0:
                self.redo_btn.disabled = True

            #if AI's turn then back again 
            if (self.game.turn == "w" and isinstance(self.game.white_player, AiPlayer)) or (self.game.turn == "b" and isinstance(self.game.black_player, AiPlayer)):
                self.redo()

    def undo(self, *args):
        if len(self.undo_stack) > 0:
            undo_entry = self.undo_stack.pop()
            self.redo_stack.append({"board" : deepcopy(self.game.game_board), "game_state" : self.game.game_status})
            self.game.game_board = undo_entry["board"]
            self.game.game_status = undo_entry["game_state"]

            #switch turns
            self.game.turn = "b" if self.game.turn == "w" else "w"
            red = (1,0,0,1)
            green = (120/255,238/255,62/255,1)
            black_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.black_player_banner
            white_banner = App.get_running_app().root.get_screen('gameUi').ids.boardNclocks.ids.white_player_banner
            FixBox =  App.get_running_app().root.get_screen('gameUi').ids.fixBox

            # switch label background colors
            if self.game.turn == "w":
                black_banner.background_color = red
                FixBox.background_color = red
                white_banner.background_color = green
            else:
                black_banner.background_color = green
                FixBox.background_color = green
                white_banner.background_color = red
            self.update_board()

            # print("done undoing")
            if len(self.undo_stack) == 0:
                # print('btn disabled')
                self.undo_btn.disabled = True
            self.redo_btn.disabled = False

            #if AI's turn then back again 
            if (self.game.turn == "w" and isinstance(self.game.white_player, AiPlayer)) or (self.game.turn == "b" and isinstance(self.game.black_player, AiPlayer)):
                self.undo()
        elif self.game.turn == "b" and isinstance(self.game.black_player, AiPlayer):
            # print("scheduling ai move")
            Clock.schedule_once(self.AiMoveThread, 1)
        elif self.game.turn == "w" and isinstance(self.game.white_player, AiPlayer):
            # print("scheduling ai move")
            Clock.schedule_once(self.AiMoveThread, 1)

    def AiMoveThread(self, *args):
        myThread = threading.Thread(target=self.AiMove, name='AI')
        ChessBoard.thread_flag = "STARTED"
        myThread.start()
            
    def AiMove(self, *args):
        # print("move thread started")
        move = []
        if self.game.turn == "w":
            move = self.game.white_player.getMove(self.game.game_board)
        else:
            move = self.game.black_player.getMove(self.game.game_board)
        Clock.schedule_once(partial(self.playAiMove, move))
        
    def playAiMove(self,move, *args):
        if ChessBoard.thread_flag != "ENDED":
            self.undo_stack.append({"board" : deepcopy(self.game.game_board), "game_state" : self.game.game_status})
            self.game.playMove(move[0], move[1], self)
            self.update_board()
            self.move_piece_sound.play()
            ChessBoard.thread_flag = "ENDED"

    def update_board(self, *args):
        for rank in reversed(range(8)):
            for column in range(8):
                oldPiece = self.cells[rank][column].piece 
                self.cells[rank][column].piece = self.game.game_board.board[rank][column]
                if not (oldPiece == self.game.game_board.board[rank][column]):
                    self.cells[rank][column].set_img_pos()

        self.undo_btn.disabled = False

        #update captured pieces
        self.update_score()

    def update_score(self, *args):
        black_ids = App.get_running_app().root.get_screen('gameUi').ids.black_captured_pieces.ids
        white_ids = App.get_running_app().root.get_screen('gameUi').ids.white_captured_pieces.ids

        #update white pieces           
        pieces_type = list(map(type, self.game.game_board.white_captures_pieces))
        white_ids.pawn.text = str(pieces_type.count(Pawn))
        white_ids.rook.text = str(pieces_type.count(Rook))
        white_ids.bishop.text = str(pieces_type.count(Bishop))
        white_ids.knight.text = str(pieces_type.count(Knight))
        white_ids.queen.text = str(pieces_type.count(Queen))

        #update black pieces           
        pieces_type = list(map(type, self.game.game_board.black_captures_pieces))
        black_ids.pawn.text = str(pieces_type.count(Pawn))
        black_ids.rook.text = str(pieces_type.count(Rook))
        black_ids.bishop.text = str(pieces_type.count(Bishop))
        black_ids.knight.text = str(pieces_type.count(Knight))
        black_ids.queen.text = str(pieces_type.count(Queen))
        
    def animate_move(self,start_cell: Cell, end_cell: Cell):
        ani = Animation(pos=end_cell.pos)
        ani.start(start_cell.img)
   
    def selected(self, rank, column, cell: Cell):
        if ChessBoard.thread_flag == "STARTED":
            print("revoke")
            cell.state = "normal"
            return
        if cell.piece is None:
            if (rank,column) in self.marked_moved:
                self.undo_stack.append({"board" : deepcopy(self.game.game_board) , "game_state" : self.game.game_status})
                self.game.playMove((self.selected_cell.rank,self.selected_cell.column),(rank,column), self)
                self.move_piece_sound.play()
                self.update_board()
                self.selected_cell.state = "normal"
                self.selected_cell = None
                for oldTarget in self.marked_moved:
                    self.cells[oldTarget[0]][oldTarget[1]].state = "normal"
                self.marked_moved.clear()
            else:
                cell.state = "normal"
        elif cell == self.selected_cell:
            cell.state = "down"
        elif cell.piece.color != self.game.turn:
            if (rank,column) in self.marked_moved:
                self.undo_stack.append({"board" : deepcopy(self.game.game_board), "game_state" : self.game.game_status})
                self.game.playMove((self.selected_cell.rank,self.selected_cell.column),(rank,column), self)
                self.update_board()
                # self.animate_move(self.selected_cell,cell)
                self.move_piece_sound.play()
                self.selected_cell.state = "normal"
                self.selected_cell = None
                for oldTarget in self.marked_moved:
                    self.cells[oldTarget[0]][oldTarget[1]].state = "normal"
                self.marked_moved.clear()
            else:
                cell.state = "normal"
        else: #clicked on one of my pieces
            if self.selected_cell is None: #no selected pieces
                self.selected_cell = cell
                PossibleMoves = self.game.game_board.getEligableMoves(rank,column)
                self.marked_moved.clear()
                self.marked_moved.extend(PossibleMoves)
                for target in PossibleMoves:
                    self.cells[target[0]][target[1]].state = "down"
            else:
                self.selected_cell.state = "normal"
                self.selected_cell = cell
                for oldTarget in self.marked_moved:
                    self.cells[oldTarget[0]][oldTarget[1]].state = "normal"
                self.marked_moved.clear()
                PossibleMoves = self.game.game_board.getEligableMoves(rank,column)
                self.marked_moved.extend(PossibleMoves)
                for target in PossibleMoves:
                    self.cells[target[0]][target[1]].state = "down"

        # print("game status : ",self.game.game_status.name)

    def on_exit(self):
        pass

class WindowManager(ScreenManager):
    pass


def show_popup(*args):
    if App.get_running_app().root.current == 'gameUi'  and GameUi.gameMode == "PvM" :
        show = ContentPopup()
        window = Popup(title="Exit", content=show,
                    size_hint=(None, None), size=(400, 400))
        show.popup = window
        window.open()
    else:   
        box = BoxLayout(orientation = "vertical")
        vbox = BoxLayout()
        lbl = Label(text="Vous êtes sûr?", size_hint = (1, 0.2), bold = True)
        vbox.add_widget(lbl)

        Boxed_layout= BoxLayout(orientation = "horizontal")
        btn1 = Button(text="Oui", size_hint=(1, .4), bold = True)
        btn2 = Button(text="Non", size_hint=(1, .4) , bold = True)
        Boxed_layout.add_widget(btn1)
        Boxed_layout.add_widget(btn2)
 
        box.add_widget(vbox)
        box.add_widget(Boxed_layout)
        pop = Popup(title="Exit",content=box, size_hint=(None, None), size=(400, 300))
        pop.auto_dismiss = False
        def closeApp(*args):
            ChessBoard.thread_flag = "ENDED"
            Window.close()
        btn1.bind(on_release=closeApp)
        # btn1.bind(on_release=partial(doit, pop)) # bind to whatever action is being confiirmed
        btn2.bind(on_release=pop.dismiss)
        pop.open()

    return True

class SaveWind(Screen):
    def __init__(self, **kwargs):
        super(SaveWind, self).__init__(**kwargs)
        Window.bind(on_request_close=show_popup)
        
        
class ContentPopup(BoxLayout):
    def __init__(self,popup=None,  **kwargs):
        super().__init__(**kwargs)
        self.popup = popup

    def withSave(self):
        game = ChessBoard.current_game
        obj = serialisedGame(game.game_board, game.turn, game.game_status, GameUi.gameMode, game.white_timer, game.black_timer,GameUi.playAs, GameUi.diff)
        with open('GameObject', 'wb') as f:
            pickle.dump(obj,f)
        ChessBoard.thread_flag = "ENDED"
        Window.close()
    def withoutSave(self):
        ChessBoard.thread_flag = "ENDED"
        Window.close()

    def closePop(self):
        self.popup.dismiss()