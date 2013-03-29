import sys
import argparse
from glob import glob

import server

argp = argparse.ArgumentParser()
argp.add_argument( '--path', default=None )
argp.add_argument( '--port', default=8080 )
argp.add_argument( '--mode', default='gui')
args = argp.parse_args( sys.argv[1:] )


# gui.init(args)
# server.init(args)

print "ARGS", __file__

if args.mode == 'gui':
	import wx
	import gui
	gui.set_server(__file__)
	gui.start()
elif args.path and args.port:
	server.init( args )
	server.start( path=args.path, port=args.port )

sys.argv.extend(['--path','/Users/kalyan/Dropbox/Projects/Labs/tumblrtemplatr/projects'])
