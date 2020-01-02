from machine import Pin, ADC, reset
from time import sleep, time

nb = 0

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


def disableLed(case):
  rowMasse.value(0)
  colMasse.value(0)
  if case != None:
    if nb == 0: 
      board[touchToCol[case[0]]].value(1)
    else:
      board[touchToRow[case[1]]].value(1)
      
   

def displayLed(case,color,isCheck,isDrawMate,newMove):
  global nb
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
     
