from machine import Pin, ADC, reset
from time import sleep, time
import socket
from sound import bip, bipError, mario
import config
color = ""
isCheck = False
isDrawMate = False
from chessDisplay import disableLed, displayLed, display_fen, board


print("begin chess")
addr_info = socket.getaddrinfo(config.serverIp, config.serverPort)
addr = addr_info[0][-1]

goWebRepl = False

while not goWebRepl:
  try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	i = 0
	while i < 20: 
	  i = i + 1
	  try:
	    s.connect(addr)
	    break
	  except:
	    sleep(1)
	  
	s.setblocking(False)
	s.send("ChessBoard 0.0.1") 
	bip()

	oldTouch = None

	def flipFen(string):
	  global color
	  if ourColor == "black": 
	    res = ""
	    for c in reversed(string):
	      res = res + c
	    return res
	  else:
	    return string

	def flip(string):
	  global color
	  res = ""
	  if ourColor == "black": 
	    for c in string:
		if ord(c) >= ord("a") and ord(c) <= ord("h"):
			res = res + chr(ord(c)*-1+201)
		elif ord(c) >= ord("0") and ord(c) <= ord("9"):
			res = res + chr(ord(c)*-1+105)
		else:
			res = res + c
	    return res
	  else:
	    return string
	 
	validMoves = None
	nbLoop = 0
	oldTouch = None
	newMove = None
	moveToSend = ""
	lastSendMove = ""
	ourColor = ""
	computerColor = ""
	lastPing = time()

	while True:
	  caseToDisplay = None
	  if newMove:
	    caseToDisplay = newMove[0:2].upper()
	  elif moveToSend:
	    caseToDisplay = moveToSend[0:2].upper()
	  nbLoop = nbLoop + 1
	  touch = None
	  for row in "12345678op":
	    for col in "ABCDEFGH":
	      disableLed(caseToDisplay)
	      board[col].value(0)
	      if board[row].value() == 0:
		touch = col+row
	      board[col].value(1)
	      displayLed(caseToDisplay, color, isCheck, isDrawMate, newMove)

	  if touch == None and oldTouch != None and time() - lastTouchTime > 0.5 : # on a fini d'apuyer sur la touch du mouvement adverse
	    oldTouch = None 
	  if touch == "Gp": #move => webrepl
	    bip()
            goWebRepl = True
	    break
	  if touch == "Ap": #new game
	    s.send("newGame "+color)
	    touch = None
	    mario()
	  if touch == "Cp": #color
	    color = "white" if color == "black" else "black"
	    bip()
	    continue 
	  if touch == "Ao": #pion
	    bip()
	    display_fen("P")
	    continue
	  if touch == "Bo": #cav
	    bip()
	    display_fen("N")
	    continue
	  if touch == "Co": #fou
	    bip()
	    display_fen("B")
	    continue
	  if touch == "Do": #tour
	    bip()
	    display_fen("R")
	    continue
	  if touch == "Ep": #dame
	    bip()
	    display_fen("Q")
	    continue
	  if touch == "Eo": #roi
	    bip()
	    display_fen("K")
	    continue

	  if touch != None and touch != oldTouch:
	    print(touch)
	    oldTouch = touch
	    lastTouchTime = time()
	    if newMove:
	      if oldTouch == newMove[0:2].upper():
		newMove = newMove[2:]
		#oldTouch = None
		bip()
		if not newMove:
		  color = ourColor
	      else:
		bipError()
	    else:
	      if moveToSend and len(moveToSend)>1:
		if moveToSend == oldTouch:
		  bip()
		  disableLed(caseToDisplay)
		  moveToSend = ""
		elif (moveToSend+oldTouch).lower() in validMoves or (moveToSend+oldTouch).lower()+"q" in validMoves:
		  bip()
		  moveToSend = moveToSend+oldTouch
		  disableLed(caseToDisplay)
		  s.send(flip(moveToSend.lower()))
		  lastSendMove = moveToSend
		  moveToSend = ""
		else:
		  bipError()
	      elif validMoves == None: # no game in progress testLed Mode
		for i in range(0,100):  
		  displayLed(oldTouch)
		  sleep(0.01)
		disableLed(oldTouch)
	      else:
		valid = False # valid if the move is correct
		for v in validMoves:
		  if oldTouch.lower() == v[0:2]:
		    valid = True
		    break
		if valid:
		  bip()
		  moveToSend = oldTouch
		else:
		  bipError()
		  
	      
	  if time() - lastPing > 10:
	    s.send("ping")
	    lastPing = time()
	  r = s.read()
	  if r is not None and "reboot" in r.decode("utf-8"):
	    reset()
	  if r is not None and "web" in r.decode("utf-8"):
            goWebRepl = True
	    break
	  if r:
	    print(r.decode("utf-8"))
	    if "pong" in r.decode("utf-8"):
		continue
	    if "end game" in r.decode("utf-8"):
	      if "check" in r.decode("utf-8"):
		isCheck = True
	      isDrawMate = True
	      continue
	    ourColor = r.decode("utf-8").split("|")[3]
	    computerColor = "black" if ourColor == "white" else "white"
	    newMove = flip(r.decode("utf-8").split("|")[0])
	    fen = flipFen(r.decode("utf-8").split("|")[4])
	    print(newMove)
	    if newMove:
	      color = computerColor
	      if newMove == lastSendMove.lower():
		  newMove = ""
	      else:
		bip()
	    else:
	      color = ourColor
	    validMoves = flip(r.decode("utf-8").split("|")[1]).split()
	    isCheck = False
	    isDrawMate = False
	    if "check" in r.decode("utf-8").split("|")[2]:
	      isCheck = True
	  
	print("end")
	s.close()
  except Exception:
    print("exception")
    reset()
