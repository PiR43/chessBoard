import berserk
import threading
import socket
import sys
import chess

global client
global gameId
global move
move = None
endGame = False
color= ""

print("begin")

with open('./lichess.token') as f:
    token = f.read()
session = berserk.TokenSession(token)
client = berserk.Client(session)
#print(client.account.get())

def addLegalMoves(moves):
    global color
    board = chess.Board()
    for move in moves.split():
        board.push(chess.Move.from_uci(move))
    res = ""
    for move in board.legal_moves:
        if res: res = res +" "
        res = res + move.uci()
    if moves:
        lastMove = moves.split()[-1]
    else:
        lastMove = ""
    return lastMove+"|"+res+"|"+("check" if board.is_check() else "")+"|"+color+"|"+board.board_fen()

class Game(threading.Thread):
        def __init__(self, client, game_id, **kwargs):
                global move
                global color
                super().__init__(**kwargs)
                self.game_id = game_id
                self.client = client
                self.stream = client.bots.stream_game_state(game_id)
                self.current_state = next(self.stream)
                print('init')
                print(self.current_state)
                move = self.current_state["state"]["moves"]
                try:
                    if self.current_state["white"]["id"] == "pirboard":
                        color = "white"
                except:
                    pass
                try:
                    if self.current_state["black"]["id"] == "pirboard":
                        color = "black"
                except:
                    pass
       
        def run(self):
            global endGame
            endGame = False
            for event in self.stream:
                print(event)
                if event['type'] == 'gameState':
                    self.handle_state_change(event)
                elif event['type'] == 'chatLine':
                    self.handle_chat_line(event)
            print("end game")
            endGame = True;
   
        def handle_state_change(self, game_state):
            global move
            print(game_state["moves"])
            move = game_state["moves"]
   
        def handle_chat_line(self, chat_line):
            print(chat_line)
            pass

class IncomingEvents(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def run(self):
        global gameId
        for event in client.bots.stream_incoming_events():
            print(event)
            if  event['type'] == 'gameStart':
                gameId = event['game']['id']
                game = Game(client,gameId)
                print("la1")
                game.start()
                print("la2")

IncomingEvents().start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 2323))
s.listen(1)
while 1:
    conn, addr = s.accept()



    conn.setblocking(False)
    print('Connected by', addr)
    lastSendMove = None
    lastClientMove = None
    while 1:
        try:
          data = conn.recv(1024).decode("utf-8")
          if data: 
              print("["+data+"]")
              lastClientMoves = data
              if "newGame" in data:
                  if "white" in data:
                    client.challenges.create("Peit_Frere_Poulpe",False,color="white")
                  else:
                    client.challenges.create("Peit_Frere_Poulpe",False,color="black")
              elif "ChessBoard" not in data:
                res = client.bots.make_move(gameId, data.lower())
                print(res)
          else:
              break
        except BlockingIOError:
          pass
        except UnicodeDecodeError:
          pass
        except:
          print("Unexpected error:", sys.exc_info())
        if move != lastSendMove:
            conn.send((addLegalMoves(move)).encode())
            print((addLegalMoves(move)).encode())
            lastSendMove = move
        if endGame:
            stream = client.bots.stream_game_state(gameId)
            for event in stream:
                pass
            veryLastMoves = event["state"]["moves"]
            if lastClientMoves.lower() != veryLastMoves[-1]:
                conn.send((addLegalMoves(veryLastMoves.lower())).encode())
            conn.send("end game".encode())
            endGame = False
    conn.close()

    print("end")

