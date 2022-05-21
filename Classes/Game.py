#a class that handels an instance of a game
from unicodedata import name
from Classes.AiPlayer import AiPlayer
from Classes.Board import Board
from enum import Enum
from Classes.OfflinePlayer import OfflinePlayer
import UI.gameUI as chessUI
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock

class GameStatus(Enum):
    ACTIVE = 1
    BLACK_WIN = 2
    WHITE_WIN = 3
    STALEMATE = 4
    INSUFFICIENT_MATERIAL = 5
    BLACK_KING_CHECKED = 6
    WHITE_KING_CHECKED = 7
class Game:
    def __init__(self,boardUI: chessUI,turn="w"):
        self.game_board = Board()
        self.turn = turn
        self.game_status = GameStatus.ACTIVE
        self.boardUI = boardUI
        self.white_player = AiPlayer("w", 1)
        self.black_player = OfflinePlayer("b")
        
        self.white_timer = 300
        self.black_timer = 300

        self.clock_ticking_sound = SoundLoader.load('./Assets/audio/ticking_clock.wav')
        
    def start_game(self):
        #initialise Game UI
        while self.game_status == GameStatus.ACTIVE:
            turn_var = "white" if self.turn == "w" else "black"
            print(f"{turn_var}'s turn")
            if self.turn == "b":
                move = self.black_player.getMove(self.game_board) #returns a valid move
                black_AI_autopromotion = (True if isinstance(self.black_player,AiPlayer) else False)
                print(f"move stat : {self.game_board.move_piece(move[0],move[1],black_AI_autopromotion)}")
                if self.game_board.isCheck("w") :
                    if self.game_board.isCheckMate("w"):
                        print("Game is over, black team wins")
                        self.game_status = GameStatus.BLACK_WIN
                    else :
                        print("White king is under check")
                self.turn = "w"
            else:
                move = self.white_player.getMove(self.game_board) #returns a valid move
                white_AI_autopromotion = (True if isinstance(self.white_player,AiPlayer) else False)
                print(f"move stat : {self.game_board.move_piece(move[0],move[1],white_AI_autopromotion)}")
                if self.game_board.isCheck("b") :
                    if self.game_board.isCheckMate("b"):
                        print("Game is over, white team wins")
                        self.game_status = GameStatus.WHITE_WIN
                    else :
                        print("black king is under check")
                self.turn = "b"

    def update_clocks(self, *args):
        if self.turn == "w":
            mins, secs = divmod(self.white_timer, 60)
            current_time = '{:02d}:{:02d}'.format(mins, secs)
            #update lables
            white_clock = App.get_running_app().root.ids.boardNclocks.ids.white_player_clock
            white_clock.text = current_time
            self.white_timer -= 1
            if mins == 0 and secs <= 30:
                white_clock.color = (1,0,0,1)
                self.clock_ticking_sound.play()
                if secs == 0:
                    #show game over
                    self.game_status = GameStatus.BLACK_WIN
                    self.showGameStatus()
                    return False
        else:
            mins, secs = divmod(self.black_timer, 60)
            current_time = '{:02d}:{:02d}'.format(mins, secs)
            #update lables
            black_clock = App.get_running_app().root.ids.boardNclocks.ids.black_player_clock
            black_clock.text = current_time
            self.black_timer -= 1
            if mins == 0 and secs <= 30:
                black_clock.color = (1,0,0,1)
                self.clock_ticking_sound.play()
                if secs == 0:
                    self.game_status = GameStatus.WHITE_WIN
                    self.showGameStatus()
                    return False
        if self.game_status.value in (2,3,4,5):
            return False
                      
    def switchTurnes(self):
        self.turn = "b" if self.turn == "w" else "w"

        red = (1,0,0,1)
        green = (120/255,238/255,62/255,1)
        black_banner = App.get_running_app().root.ids.boardNclocks.ids.black_player_banner
        white_banner = App.get_running_app().root.ids.boardNclocks.ids.white_player_banner

        # switch label background colors
        if self.turn == "w":
            black_banner.background_color = red
            white_banner.background_color = green
        else:
            black_banner.background_color = green
            white_banner.background_color = red
        
        #schedule ai next move
        if self.turn == "b" and isinstance(self.black_player, AiPlayer):
            Clock.schedule_once(self.boardUI.AiMoveThread, 1)
        if self.turn == "w" and isinstance(self.white_player, AiPlayer):
            Clock.schedule_once(self.boardUI.AiMoveThread, 1)
            
    def playMove(self,start: tuple, end: tuple, gameUI):
        if self.turn == "b":
            black_AI_autopromotion = (True if isinstance(self.black_player,AiPlayer) else False)
            print(f"move stat : {self.game_board.move_piece(start,end, self.boardUI ,black_AI_autopromotion)}")
            if self.game_board.isCheck("w") :
                self.game_status = GameStatus.WHITE_KING_CHECKED
                if self.game_board.isCheckMate("w"): 
                    print("Game is over, black team wins") #
                    self.game_status = GameStatus.BLACK_WIN
                else :
                    print("White king is under check")
        else:
            white_AI_autopromotion = (True if isinstance(self.white_player,AiPlayer) else False)
            print(f"move stat : {self.game_board.move_piece(start,end, self.boardUI,white_AI_autopromotion)}")
            if self.game_board.isCheck("b") :
                self.game_status = GameStatus.BLACK_KING_CHECKED
                if self.game_board.isCheckMate("b"):
                    print("Game is over, white team wins")
                    self.game_status = GameStatus.WHITE_WIN
                else :
                    print("black king is under check")          

        if self.game_board.isStaleMate("b") or self.game_board.isStaleMate("w"):
            self.game_status = GameStatus.STALEMATE
            print("Game is over, Stalemate") #
        elif self.game_board.isInsufficientMaterial():
            print("Game is Over, Draw by insufficient material")#
            self.game_status = GameStatus.INSUFFICIENT_MATERIAL
        
        # print(f"before showing game status : turn = {self.turn} stats = {self.game_status.value}")
        self.showGameStatus()
        
        if self.game_status.value in (1,6,7):
            # print("switching turns")
            self.switchTurnes()

    def getGameStatus(self):
        return self.getGameStatus

    def showGameStatus(self):
        print(f"turn = {self.turn} stat = {self.game_status.value}")
        if self.turn == 'b' and isinstance(self.white_player,AiPlayer) and self.game_status.value in (1,6,7):
            self.game_status = GameStatus.ACTIVE
            print("returning 1 ")
            return
        elif self.turn == 'w' and isinstance(self.black_player,AiPlayer) and self.game_status.value in (1,6,7):
            self.game_status = GameStatus.ACTIVE
            print("returning")
            return 

        popup = Popup(title="Game status",size_hint=(.5, None), height= 120)
        popup.auto_dismiss = False
        btn = Button()
        btn.size_hint = (.2,None)
        btn.height = 50
        popup.content = btn

        if self.game_status == GameStatus.BLACK_WIN:
            popup.title = "Game is Over, black team wins"
            btn.text= "Exit"
            def clicked():
                popup.dismiss()
            btn.on_press = clicked
            #update stats in database
            popup.open()
        elif self.game_status == GameStatus.WHITE_WIN:
            popup.title = "Game is Over, white team wins"
            btn.text= "Exit"
            def clicked():
                popup.dismiss()
            btn.on_press = clicked
            #update stats in database
            popup.open()
        elif self.game_status in  (GameStatus.WHITE_KING_CHECKED,GameStatus.BLACK_KING_CHECKED): 
            name_ = 'white' if self.game_status == GameStatus.WHITE_KING_CHECKED else 'black'
            popup.title = f"{name_} king is under check"
            btn.text= " Ok "
            btn.bind(on_press=popup.dismiss)
            popup.open()
            self.game_status = GameStatus.ACTIVE
        elif self.game_status == GameStatus.STALEMATE: 
            popup.title = "Game is Over, draw by Stalemate"
            btn.text= "EXIT"
            def clicked():
                popup.dismiss()
            btn.on_press = clicked
            popup.open()
        elif self.game_status == GameStatus.INSUFFICIENT_MATERIAL: 
            popup.title = "Game is Over, draw by insufficient material"
            btn.text= "EXIT"
            def clicked():
                popup.dismiss()
            btn.on_press = clicked
            popup.open()