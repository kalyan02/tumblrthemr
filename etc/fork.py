import os
import time
from multiprocessing import Process

def main_proc(q):
	#while True:
	time.sleep(5)
	print "Main Proc"
	q.terminate()
	print "Main Proc terminated other"

def sis_proc():
	while True:
		print "Sys proc"

p = Process(target=sis_proc)
p.start()

main_proc(p)