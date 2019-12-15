from machine import Pin, ADC, reset
from time import sleep, time
import socket
from sound import bip, bipError, mario
import config


print("begin chess")
board = {}
board["o"] = Pin(36, Pin.IN, Pin.PULL_UP)
board["p"] = Pin(39, Pin.IN, Pin.PULL_UP)
board["1"] = Pin(34, Pin.IN, Pin.PULL_UP)
board["2"] = Pin(35, Pin.IN, Pin.PULL_UP)
board["3"] = Pin(32, Pin.IN, Pin.PULL_UP)
board["4"] = Pin(33, Pin.IN, Pin.PULL_UP)
board["5"] = Pin(25, Pin.IN, Pin.PULL_UP)
board["6"] = Pin(26, Pin.IN, Pin.PULL_UP)
board["7"] = Pin(27, Pin.IN, Pin.PULL_UP)
board["8"] = Pin(14, Pin.IN, Pin.PULL_UP)

board["A"] = Pin(22, Pin.OUT)
board["B"] = Pin(18, Pin.OUT)
board["C"] = Pin(5, Pin.OUT)
board["D"] = Pin(17, Pin.OUT)
board["E"] = Pin(16, Pin.OUT)
board["F"] = Pin(4, Pin.OUT)
board["G"] = Pin(0, Pin.OUT)
board["H"] = Pin(2, Pin.OUT)
colMasse = Pin(19, Pin.OUT)
rowMasse = Pin(21, Pin.OUT)
status1 = Pin(12, Pin.OUT)
status2 = Pin(13, Pin.OUT)
status3 = Pin(15, Pin.OUT)

status1.value(1) # check / white
status2.value(1) # drawMate / black
status3.value(1) # enterPos / white

touchToCol = {}
touchToCol["A"] = "H"
touchToCol["B"] = "G"
touchToCol["C"] = "F"
touchToCol["D"] = "E"
touchToCol["E"] = "D"
touchToCol["F"] = "C"
touchToCol["G"] = "B"
touchToCol["H"] = "A"


touchToRow = {}
touchToRow["1"] = "H"
touchToRow["2"] = "G"
touchToRow["3"] = "F"
touchToRow["4"] = "E"
touchToRow["5"] = "D"
touchToRow["6"] = "C"
touchToRow["7"] = "B"
touchToRow["8"] = "A"


addr_info = socket.getaddrinfo(config.serverIp, config.serverPort)
addr = addr_info[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(addr)
s.setblocking(False)
s.send("ChessBoard 0.0.1") 

oldTouch = None

global nb
nb = 0

def disableLed(case):
  rowMasse.value(0)
  colMasse.value(0)
  if case != None:
    if nb == 0: 
      board[touchToCol[case[0]]].value(1)
    else:
      board[touchToRow[case[1]]].value(1)
      
   

def displayLed(case):
  global nb
  global color
  global isCheck
  global isDrawMate
  global newMove
  nb = nb + 1
  if nb > 1: nb = 0
  if nb == 0: 
      rowMasse.value(0)
      if case != None:
        board[touchToRow[case[1]]].value(1)
        board[touchToCol[case[0]]].value(0)
      colMasse.value(1)
      status1.value(isCheck == False or newMove)
      status2.value(isDrawMate == False or newMove)
      sleep(0.001)
  else:
      colMasse.value(0)
      if case != None:
        board[touchToCol[case[0]]].value(1)
        board[touchToRow[case[1]]].value(0)
      rowMasse.value(1)
      status1.value(color != "white")
      status2.value(color != "black")
      sleep(0.001)

def flipFen(string):
  global color
  if ourColor == "black": 
    res = ""
    for c in reversed(string):
      res = res + c
    return reversed(res)
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

def display_fen(piece):
  for l in "ABCDEFGH":
    board[l].value(1)
  global fen
  row = 9
  for line in reversed(fen.split("/")):
    row = row - 1
    col = []
    colW = []
    #colB = []
    pos = 0
    for c in reversed(line):
      pos = pos + 1
      if ord(c) >= ord("2") and ord(c) <= ord("8"):
        pos = pos + ord(c) - ord("1")
      elif c == piece.upper():
        col.append(pos)
        colW.append(pos)
      elif c == piece.lower():
        col.append(pos)
        #colB.append(pos)
    if(len(col)):
      print(line)
      for i in range(0, 200):
	      rowMasse.value(0)
	      colMasse.value(1)
	      for pos in (col if round(i/40)%2 else colW):
		board[chr(ord("A")-1+pos)].value(0)
	      sleep(0.01)
	      for pos in (col if round(i/40)%2 else colW):
		board[chr(ord("A")-1+pos)].value(1)
	      colMasse.value(0)
	      rowMasse.value(1)
	      board[chr(ord("A")-1+row)].value(0)
	      sleep(0.01)
	      board[chr(ord("A")-1+row)].value(1)
	      rowMasse.value(0)
      
validMoves = None
nbLoop = 0
oldTouch = None
newMove = None
moveToSend = ""
lastSendMove = ""
color = ""
isCheck = False
isDrawMate = False
ourColor = ""
computerColor = ""
while True:
  caseToDisplay = None
  if newMove:
    caseToDisplay = newMove[0:2].upper()
  elif moveToSend:
    caseToDisplay = moveToSend[0:2].upper()
  nbLoop = nbLoop + 1
  #if nbLoop > 10:
    #break
  touch = None
  for row in "12345678op":
    for col in "ABCDEFGH":
      disableLed(caseToDisplay)
      board[col].value(0)
      if board[row].value() == 0:
        touch = col+row
      board[col].value(1)
      displayLed(caseToDisplay)

  if touch == None and oldTouch != None and time() - lastTouchTime > 0.5 : # on a fini d'apuyer sur la touch du mouvement adverse
    oldTouch = None 
  if touch == "Gp": #move => webrepl
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
          
      

  r = s.read()
  if r is not None and "reboot" in r.decode("utf-8"):
    reset()
  if r is not None and "web" in r.decode("utf-8"):
    break
  if r:
    print(r.decode("utf-8"))
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
      color = ourColor
    validMoves = flip(r.decode("utf-8").split("|")[1]).split()
    isCheck = False
    isDrawMate = False
    if "check" in r.decode("utf-8").split("|")[2]:
      isCheck = True
  
print("end")
s.close()
