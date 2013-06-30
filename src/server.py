import engine
from dialog import TTIntroDialog
import urllib
import argparse
import sys
import bottle
import time
import json
import re
import os
import webbrowser
from BeautifulSoup import BeautifulSoup as Soup
import pickle
import errno
from glob import glob

from jinja2 import Template

DEFAULT_SRC = 'default'
CURRENT_SRC = 'current_source'
API_KEY = 'api_key'

PROJECTS_DIRECTORY = "projects"
project = 'clarus'
app = bottle.Bottle()


# setup some defaults
# hope this works
base_data_path = os.path.expanduser('~/com.lonefish.net/tte/')
data_source_path = base_data_path+'import_sources.txt'
data_source = {'data':{}}

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def render(name, values):
	template_content = open("templates/%s" % name, 'r').read()
	template = Template(template_content)
	return template.render(**values)

# small util to save the data data to file!
def __save_data():
	global data_source, data_source_path
	fh = open(data_source_path,'wb+')
	pickle.dump(data_source,fh)
	fh.close()

# if path doesn't exist, create
if not os.path.exists(base_data_path):
	mkdir_p(base_data_path)

# if path exists, then load the data
if os.path.exists(base_data_path):
	try:
		# this won't exist
		fh = open(data_source_path,'rb')
		data_source = pickle.load(fh)
	except Exception, e:
		print ">>>>", e.message
		data_source = {}
		data_source['data'] = {}

# now load the most default data pack
# we need it in case things get effedup!
# if data_source and type(data_source) == dict:
jsonData = json.load( open("data/sampleData.json",'r') )
data_source['data'][DEFAULT_SRC] = jsonData

# put this in a var
current_data_source_name = None
if data_source.has_key(CURRENT_SRC):
	current_data_source_name = data_source[CURRENT_SRC]
else:
	current_data_source_name = DEFAULT_SRC

# bad idea, but okay for now
current_data_source = data_source['data'].get(current_data_source_name)

shutdown_callback = None

# fetches data from current active data souce and renders the theme
def render_theme(the_path):
	global data_source, current_data_source, current_data_source_name
	current_data_source = data_source['data'][current_data_source_name]
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
		contextDataMap = engine.ContextDataMapper( current_data_source['response'], contextTemplate )
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

# the home!
@app.route('/')
def home():
	global PROJECTS_DIRECTORY
	global data_source, current_data_source, current_data_source_name
	
	prjs = glob(PROJECTS_DIRECTORY.rstrip('/') + "/*")
	prjs_names = map( os.path.basename, prjs )

	srcs_names = data_source['data'].keys()
	src_active = current_data_source_name

	return render( 'index.html', {
		# 'debug_info':'hello',
		'projects':prjs_names, 
		'sources':srcs_names, 
		'active_src':current_data_source_name,
		'api_key' : data_source.get(API_KEY,'')
		})

@app.route('/api/select_source/<source_name>')
def select_source(source_name,**kwargs):
	global data_source, current_data_source, current_data_source_name

	data_source[CURRENT_SRC] = current_data_source_name = source_name
	current_data_source = data_source['data'][current_data_source_name]
	__save_data()

	bottle.redirect('/')
	pass

@app.route('/api/remove_source/<source_name>')
def remove_source(source_name,**kwargs):
	global data_source, current_data_source, current_data_source_name

	del data_source['data'][source_name]
	# if we are deleting active source, switch back to default one
	if current_data_source_name == source_name:
		data_source[CURRENT_SRC] = current_data_source_name = DEFAULT_SRC
		current_data_source = data_source['data'][current_data_source_name]

	__save_data()

	bottle.redirect('/')

# lets you import json blog data from tumblr if you have an api key
@app.route('/api/import_source',method='POST')
def import_source():
	global data_source, current_data_source, current_data_source_name
	api_key = bottle.request.forms.get('api_key')
	src_name = blog_uname = bottle.request.forms.get('blog_uname')

	url_template = "http://api.tumblr.com/v2/blog/%s/posts?api_key=%s" # api_key, blog_url
	blog_url_template = "%s.tumblr.com"


	data_source[API_KEY] = api_key
	__save_data()

	src_name = src_name.replace(' ', '_')
	blog_url = blog_url_template % blog_uname

	try:
		final_url = url_template % (blog_url,api_key)
		content = urllib.urlopen( final_url ).read()
		content = json.loads(content)
		if content.has_key('response') and content['meta']['status'] != 404:
			data_source['data'][src_name] = content
			data_source[CURRENT_SRC] = src_name
			__save_data()
		else:
			raise Exception(content['meta']['msg'])
	except Exception, e:
		print 'ERROR', e.message

	bottle.redirect('/')

@app.route('/<project>')
@app.route("/<project>/<file_path:re:.*>")
def render_page(project,**kwargs):
	global data_source, current_data_source, current_data_source_name
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
		return '404 - %s | %s | %s' % (the_path,theme_directory,project) #+ render_404()

def start( path=PROJECTS_DIRECTORY, port=8080 ):
	global PROJECTS_DIRECTORY
	PROJECTS_DIRECTORY = path
	print "DO START (%s,%s)" % (path,port);
	bottle.debug()
	bottle.run( app, host='localhost', port=port, reloader=False )

def end():
	sys.exit(0)

sysargs = None
def init(args):
	global sysargs
	sysargs = args 

# Get things from command line - makes it easy for testing
if sys.argv[0] == __file__ :
	argp = argparse.ArgumentParser()
	argp.add_argument( '--path' )
	argp.add_argument( '--port', default=8080 )
	args = argp.parse_args( sys.argv[1:] )

	# Extract arguments
	path = args.path.strip().rstrip("/").rstrip("\\")
	port = args.port

	path = os.path.abspath(path)
	print "LETS GO ", path

	# Strip trailing slashes if the path is valid
	if path:
		if os.path.isdir(path):
			webbrowser.open( "http://localhost:%s" %(port) )
			start( port=port, path=path )
	else:
		print "SHIT!"

