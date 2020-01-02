import network
from time import sleep

sleep(5)
safeBoot = False
#for w in network.WLAN(network.STA_IF).scan():
for w in sta_if.scan():
  if "safeBoot" in w[0]:
    safeBoot = True

if not safeBoot:
  import chess
