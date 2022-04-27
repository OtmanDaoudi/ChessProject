from Classes.Piece import Piece


class Knight(Piece):
    def __init__(self,rank,column,color,image = None,isKilled = False) : 
        super().__init__(rank,column,color,image,isKilled)

    def __str__(self):
        if  (self.color == "w"): return f"{Piece.WHITE_KNIGHT}"
        elif(self.color == "b"): return f"{Piece.BLACK_KNIGHT}"
        else :return ""