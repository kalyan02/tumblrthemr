import engine
from dialog import TTIntroDialog

import argparse
import sys
import bottle
import time
import json
import re
import os
import webbrowser
from BeautifulSoup import BeautifulSoup as Soup

PROJECTS_DIRECTORY = "projects"
project = 'clarus'
app = bottle.Bottle()

jsonData = json.load( open("data/sampleData.json",'r') )
# context = engine.createContextMapper( jsonData['response'] )

def render_theme(the_path):
	s_time = time.time()
	try:
		content = open(the_path, 'r').read()

		# Soupify and Extract meta tags
		soup = Soup( content )
		metaTags = { tag['name'] : tag['content'] for tag in soup.findAll('meta', attrs={'name':re.compile('^([a-zA-Z]+):.*')} ) }
		tpl = engine.Template( content )

		# Compile the template
		tpl.compile()
		# Fetch the default template to map the data to template
		# this basically has rules on how to render each tag from raw json
		contextTemplate = engine.defaultContextMapperTemplate()
		# Update data template with info on how to map meta data
		contextTemplate.update( engine.metaContextTemplate( metaTags ) )
		# create the mapper object
		contextDataMap = engine.ContextDataMapper( jsonData['response'], contextTemplate )
		# Render the tumblr template with the data map we constructed
		output = tpl.render(contextDataMap)
	except Exception, e:
		return 'Template Compile Error : ' + e.message

	# Fetch hthe default context mapper template
	e_time = time.time()
	debug_info = "\n<!-- Time to compile and render: %s -->" % (e_time-s_time)
	return output + debug_info


@app.error(404)
def render_404(**kwargs):
	return '404!'

# For future
def render_favicon(**kwargs):
	return None

@app.route('/')
def home():
	return "Hello world"

@app.route('/<project>')
@app.route("/<project>/<file_path:re:.*>")
def render_page(project,**kwargs):
	print "PROJ", project, kwargs
	# TODO:Simplify
	file_path = kwargs.get('file_path','index.html')
	if file_path is '':
		file_path = 'index.html'

	# Output is stupid
	if project == 'favicon.ico':
		return render_favicon()

	# Get started
	theme_directory = PROJECTS_DIRECTORY + '/' + project + '/'
	the_path = theme_directory + file_path
	print "Theme path ", the_path, os.path.exists(the_path)

	if os.path.exists(the_path):
		# If its ending with html, render it as a tumblr theme
		if the_path.lower().endswith('.html') or the_path.lower().endswith('.htm'):
			return render_theme(the_path)
		else:
			# Serve it from the theme's directory
			return bottle.static_file(file_path,theme_directory)
	else:
		return render_404()

def start( path=PROJECTS_DIRECTORY, port=8080 ):
	bottle.debug()
	bottle.run( app, host='localhost', port=port, reloader=False )

def end():
	sys.exit(0)

sysargs = None
def init(args):
	global sysargs
	sysargs = args 

# Get things from command line
# TODO:Figure out how to do without a subprocess

if sys.argv[0] is __file__ :
	argp = argparse.ArgumentParser()
	argp.add_argument( '--path' )
	argp.add_argument( '--port', default=8080 )
	args = argp.parse_args( sys.argv[1:] )

	# Extract arguments
	path = args.path.strip().rstrip("/").rstrip("\\")
	port = args.port

	# Strip trailing slashes if the path is valid
	if path:
		if os.path.isdir(path):
			PROJECTS_DIRECTORY = path
			start( port=port )
	else:
		print "SHIT!"

