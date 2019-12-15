# chessBoard

This allow connect a chessboard make with an esp32 programmed to lichess chess server

## client

the client folder contain the micropython code of the board itself. It need a wifi conection already up (normaly done in boot.py). The main loop read clic on the board verify validity of move and send move to server. The main loop read also opposite move send by server and display them with leds.

## server

This part to the bridge between the client and lichess. It use python-chess for found list of valid move and send it to the board.
