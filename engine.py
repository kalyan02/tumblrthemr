#################################################
### TumblrTemplatr
### The main engine. This is it.
#################################################

import bottle
import re
import json
import types
import time
import dateutil.parser as dparser

class Token(object):
	TOKEN_STRING = "token:string"
	TOKEN_BLOCK_START = "token:block"
	TOKEN_BLOCK_END = "token:block_end"
	TOKEN_VAR = "token:var"
	TOKEN_META_VAR = "token:meta_var"
	TOKEN_VAR_LANG = "token:lang"
	TOKEN_VAR_TEXT = "token:text"
	TOKEN_VAR_COLOR = "token:color"

	def __init__(self, token_type, content, params=None):
		self.content = content
		self.type = token_type
		self.params = params

	def __str__(self):
		return "<%s>: %s" % (self.type,self.content)

	def value(self):
		return self.content

	def args(self):
		return self.params

	pass

class SymbolStack(list):
	def top(self):
		return self[ len(self)-1 ]
	def push(self, value):
		self.append(value)
	def size(self):
		return len(self)

class Lexer(object):
	def __init__(self, content):
		self.content = content
		self.re_tokens = re.compile( "\{\s*(.*?)\}",re.IGNORECASE)

		self.re_block = re.compile( "^(\/?Block|text|lang|color)\s*:?(.*?$)", re.IGNORECASE )
		self.re_var = re.compile("^[a-zA-Z0-9_-]*$", re.IGNORECASE)
		self.re_var_args = re.compile("(\S+)=[\"']?((?:.(?![\"']?\s+(?:\S+)=|[>\"']))+.)[\"']?", re.IGNORECASE)
		self.re_var_name = re.compile("^[a-zA-Z0-9]+\s?", re.IGNORECASE)
		
		self.lex_pos = 0

	def tokenize(self):
		self.iter_blocks = self.re_tokens.finditer( self.content )
		for eachBlock in self.iter_blocks:
			span_start, span_end = eachBlock.span()
			if span_start - self.lex_pos > 0:
				yield Token( Token.TOKEN_STRING, self.content[self.lex_pos:span_start] )
				self.lex_pos = span_start

			if span_start - self.lex_pos == 0:
				rawToken = eachBlock.groups()[0]
				self.lex_pos = span_end
				if rawToken:
					rawToken = rawToken.strip()
					
					blockMatch = self.re_block.findall( rawToken )

					if len(blockMatch) > 0:
						token, tokenData = blockMatch.pop()
						token = token.strip().lower()
						tokenData = tokenData.strip()

						if token == '/block':
							yield Token( Token.TOKEN_BLOCK_END, tokenData )
						elif token == 'block':
							yield Token( Token.TOKEN_BLOCK_START, tokenData )
						elif token == 'lang':
							yield Token( Token.TOKEN_VAR_LANG, tokenData )
						elif token == 'text':
							yield Token( Token.TOKEN_VAR_TEXT, tokenData )
						elif token == 'color':
							yield Token( Token.TOKEN_VAR_COLOR, tokenData )
					else:
						varMatch = self.re_var.findall( rawToken )
						if len(varMatch) > 0:
							tokenData = varMatch.pop()
							yield Token( Token.TOKEN_VAR, tokenData )
						else:
							varArgMatch = self.re_var_args.findall( rawToken )
							argName = self.re_var_name.findall( rawToken )
							if len(varArgMatch) > 0 and len(argName) > 0:
								argName = argName.pop()
								argParams = { key:val for key,val in varArgMatch }
								yield Token( Token.TOKEN_VAR, argName, argParams )
							else:
								pass
								#print rawToken
								# Yield String
		content_end = len(self.content)
		if content_end - self.lex_pos > 0:
			yield Token( Token.TOKEN_STRING, self.content[self.lex_pos:content_end] )
			self.lex_pos = content_end

	def tokens(self):
		return list(self.tokenize())



class Node(object):
	def __init__(self):
		self.children = []

	def push(self,item):
		self.children.append(item)

	def render(self,context):
		# print self.children
		result = []
		for each in self.children:
			childRenderResult = each.render(context)
			if childRenderResult:
					result.append( unicode(childRenderResult) )

		try:
			return u"".join(result)
		except:
			pass
			# print result

		return ''

class IfNode(Node):
	pass

class BlockNode(Node):
	def __init__(self, blockName):
		Node.__init__(self)
		self.blockName = blockName
		# print 'foo', blockName

	def __str__(self):
		return "{%s:%s}" % (self.blockName, str(self.children))

	def __repr__(self):
		return object.__repr__(self) + ("(%s)" % self.blockName)
	
	def render(self,context):
		resres = context.resolve(self.blockName.lower())
		# print '>>>>', context.resolve('lines')
		# if self.blockName == 'Text':
		# 	print '>>>>', resres.mapper
			# print '>>>>', resres.data
			# print '>>>>', resres.resolve('title',True)

		# print 'foo', resres, self.children
		if resres:
			strs = []
			if type(resres) is list:
				for eachContext in resres:
					strs.append( Node.render(self,eachContext) )
				return ''.join(strs)
			elif type(resres) is ContextDataMapper:
				# print resres.resolve('lines')
				# print "===", self.blockName, self.children, resres
				return Node.render(self,resres)
			else:
				# print self.blockName, self.children, resres
				# return resres

				return Node.render(self,context)

		# if type(resres) is list:
		# 	for each in self.children:
		# 		resstr += each.render(cont)


class VarNode(Node):
	def __init__(self, varName, varArgs):
		Node.__init__(self)
		self.varName = varName
		self.varArgs = varArgs
	def __str__(self):
		return "{%s:%s}" % (self.varName, self.varArgs)

	def __repr__(self):
		return object.__repr__(self) + ("(%s)" % self.varName)

	def render(self,context):
		# if self.varName == 
		return (context.resolve( self.varName.lower() ))

class MetaVarNode(VarNode):
	def __init__(self, varType, varName, varArgs ):
		VarNode.__init__(self, varName, varArgs)
		self.varType = varType

	def __repr__(self):
		return object.__repr__(self) + ("(%s)" % self.varName)

	def __str__(self):
		return "{%s:%s}" % (self.varType, self.varName)
	pass

class StringNode(Node):
	def __init__(self, content):
		Node.__init__(self)
		self.content = content

	def __str__(self):
		return self.content

	def __repr__(self):
		return object.__repr__(self) + ("(%s)" % self.content.strip())

	def render(self,context):
		return self.content

class NodeFactory(object):
	TOKEN_STRING = "token:string"
	TOKEN_BLOCK_START = "token:block"
	TOKEN_VAR = "token:var"
	TOKEN_VAR_LANG = "token:lang"
	TOKEN_VAR_TEXT = "token:text"
	TOKEN_VAR_COLOR = "token:color"

	@staticmethod
	def create( token ):
		if token.type == Token.TOKEN_BLOCK_START:
			return BlockNode( token.value() )
		if token.type in [ Token.TOKEN_VAR_LANG, Token.TOKEN_VAR_TEXT, Token.TOKEN_VAR_COLOR ]:
			return MetaVarNode( token.type, token.value(), token.args() )
		if token.type == Token.TOKEN_VAR:
			return VarNode( token.value(), token.args() )
		if token.type == Token.TOKEN_STRING:
			return StringNode( token.value() )

class Parser(object):
	def __init__(self,tokens):
		self.tokens = tokens
		self.root = None
		self.stack = SymbolStack()

	def parse(self):
		self.root = Node()
		currentNode = self.root
		self.stack.push( currentNode )
		for eachToken in self.tokens:
			if eachToken.type == Token.TOKEN_BLOCK_START:
				currentNode = BlockNode( eachToken.value() )
				self.stack.push( currentNode )
			elif eachToken.type == Token.TOKEN_BLOCK_END:
				if type(self.stack.top()) == BlockNode and self.stack.top().blockName == eachToken.value():
					# block node is not yet a part of the tree
					# make it so
					blockNode = self.stack.pop()
					currentNode = self.stack.top()
					currentNode.push( blockNode )
				else:
					raise Exception("Mismatched block %s" % self.stack.top().blockName)
			else:
				# print currentNode
				currentNode.push( NodeFactory.create( eachToken ) )

		if self.stack.size() > 1 or self.stack.top() != self.root:
			raise Exception("Invalid syntax. Possibly mismatched blocks.")

		return self.root

class ContextDataMapper(object):
	def __init__(self, data, mapper,parent=None,extra=None):
		self.data = data
		self.mapper = mapper
		self.parent = parent
		self.extra = extra

	# todo: refactor
	def resolve(self,what,askParent=False):

		if type(self.mapper) is dict and self.mapper.has_key(what):
			mapResult = self.mapper[what]
			key = None
			value = None

			if type(mapResult) is tuple:
				json_key, sub_map = mapResult

				# if first arg is function and second arg a map
				# use the function as a condition
				# treat it as boolean
				# make the context subcontext
				if type(json_key) is types.FunctionType:
					node = {
						'data' : self.data
					}
					if type(self.extra) is dict:
						node.update(self.extra)
					funcResult = json_key( node )
					if type(funcResult) is bool:
						if funcResult:
							# print what, sub_map, self.data
							return ContextDataMapper( self.data, sub_map )

					return funcResult

				# if first arg is String
				# and the map is a list,
				# then iterate
				if type(json_key) is str and type(self.data[json_key]) is list:
					mapperlist = []
					index = 0
					for eachdata in self.data[json_key]:
						mapperlist.append( ContextDataMapper( eachdata, sub_map, extra={'index':index} ) )
						index += 1

					return mapperlist
				else:
					return ContextDataMapper( self.data[json_key], sub_map )

			# if result is a string
			# use it as a variable
			elif type(mapResult) is str:
				if self.data.has_key( mapResult ):
					return self.data[mapResult]
				else:
					if askParent and type(self.parent) is ContextDataMapper:
						return parent.data.get(mapResult)

			# if map is a function
			# then use the result of that function as value
			elif type(mapResult) is types.FunctionType:
					node = { 'data' : self.data }
					if type(self.extra) is dict:
						node.update(self.extra)
					return mapResult( node )

			
		# else:
		# 	return self.data

class Template(object):
	def __init__(self,templateString):
		self.templateString = templateString
		self.tokens = None
		self.parseTree = None
		# self.compile()

	def compile(self):
		lexer = Lexer( self.templateString )
		self.tokens = lexer.tokens()
		
		# print 'tokens', self.tokens
		# for each in self.tokens:
		# 	print each.type

		parser = Parser( self.tokens )
		self.parseTree = parser.parse()

	def render(self,context):
		# print '---'
		return self.parseTree.render(context)

	pass


#####################################################
## Utilities to map data from raw JSON to template ##
#####################################################

def _alt_item(*items):
	def __alt_func(node):
		i = node.get('index',0)
		l = len(items)
		mod_i = (i+1) % l
		return items[ mod_i ]
	return __alt_func

def _photo_url(size):
	def __get_optimum_size(size,sizes):
		all_sizes = sizes[:]
		if size in sizes:
			return size
		else:
			sizes.sort()
			for each in sizes:
				if size < each:
					return each

			return sizes[-1]

	def __url_func(node):
		all_sizes_nodes = node['data']['photos'][0]['alt_sizes']
		all_sizes = [ each['width'] for each in all_sizes_nodes ]
		optimum_size = __get_optimum_size( size, all_sizes )
		mySizeIndex = all_sizes.index(optimum_size)

		return all_sizes_nodes[ mySizeIndex ]['url']
		# print all_sizes, size
		return '#'

	return __url_func

def _path(pathstr,delimiter='.'):
	pathFrags = pathstr.split(delimiter)
	def __path_func(node):
		nodePtr = node['data']
		# print pathFrags
		for eachPathFrag in pathFrags:
			nodePtr = nodePtr.get( eachPathFrag )
			# print eachPathFrag, nodePtr
			if not nodePtr:
				return None

		# print ">>>",nodePtr
		return nodePtr
	return __path_func

def _str(string):
	return lambda node: string

def _date(what):
	def __date_func(node):
		try:
			d = dparser.parse( node['data']['date'] )
			return d.strftime('%'+what)
			return {
				'y' : d.year,
				'm' : d.month,
				'd' : d.day,
				'M' : d.strftime('%b')
			}[ what ]
		except:
			return '#Error#'
	return __date_func

# If its a text block, then text = body
# other wise try to look for text variable
def _text(node):
	nodeData = node['data']
	if nodeData['type'] == 'text':
		return nodeData.get('text', nodeData.get('body', None) )
	return nodeData.get('text', None)

#context = None

def metaContextTemplate( metaTags ):
	contextTemplate = {}
	for metaName, metaContent in metaTags.items():
		if not ':' in metaName:
			continue
		_type = metaName[ : metaName.index(':') ].lower()
		_key = metaName[ metaName.index(':')+1 : ].lower()
		_val = metaContent

		_context = {}
		# For text 
		# - create if<text> tag
		# - create text tag
		# for if just use if
		if _type == 'if':
			if_key = 'if'+_key.replace(' ','')
			if_not_key = 'ifnot'+_key.replace(' ','')
			if _val == '1' or _val.lower() == 'true':
				_val = True
			else:
				_val = False

			_context = { 
				if_key : _str(_val),
				if_not_key : _str( not _val )
			}
		# Text requires 3 tags
		# 1. Normal Text tag
		# 
		if _type == 'text' or _type == 'image':
			_isTrue = len(_val) > 0
			if_key = 'if'+_key.replace(' ','')
			if_not_key = 'ifnot'+_key.replace(' ','')

			if _type == 'image':
				if_key += 'image'
				if_not_key += 'image'

			type_key = _type + ':' + _key
			val_key = _key.lower()
			_context = { 
				val_key : _str(_val),
				if_key : _str(_isTrue),
				if_not_key : _str( not _isTrue ),
				type_key : _str(_val)
			}

		contextTemplate.update( _context )
	return contextTemplate

def defaultContextMapperTemplate():
	contextMapTemplate = {
		'title' : _path('blog.title'),
		'url' :  _path('blog.url'),
		'metadescription' : _path('blog.description'),
		'description' : _path('blog.description'),
		'posts' : ('posts',{
					# Map generic stuff
					'title' : 'title',
					'postid' : 'id',
					'body' : 'body',
					'type' : 'type',
					'text' : _text,

					# Map specific data block types
					'chat' : ( lambda node: node['data']['type'] == 'chat', {
								'lines' : ('dialogue',{
									'label' : 'label',
									'line' : 'phrase',
									'alt' : _alt_item('even','odd')
								}),
							}),
					'hastags' : ( lambda node: len(node['data']['tags']) > 0 ),
					'tags' : ('tags', {
								'tag' : lambda node: node['data']
							}),
					'photo' : ( lambda node: node['data']['type'] == 'photo', {
								'linkopentag' : _str('<a href="#">'),
								'linkclosetag' : _str('</a>'),
								'caption' : 'caption',
								'photoalt' : 'caption',
								'photourl-500' : _photo_url(500)
								}),
					'quote' : ( lambda node: node['data']['type'] == 'quote', {
								'quote' : 'text',
								'source' : 'source'
							}),
					'link' : ( lambda node: node['data']['type'] == 'link', {
								'description' : 'description',
								'name' : 'title',
								'target' : 'url'
							}),
					'audio' : ( lambda node: node['data']['type'] == 'audio', {
								'formattedplaycount' : 'plays',
								'audioplayerwhite' : 'player',
								'caption' : 'caption'
							}),

					# Map all the month related functions
					'dayofmonth': _date('e'),
					'dayofmonthwithzero' : _date('d'),
					'dayofWeek' : _date('A'),
					'shortdayofWeek' : _date('a'),
					'dayofWeeknumber' : _date('u'),
					'dayofyear' : _date('j'),
					'Weekofyear' : _date('U'),
					'month' : _date('B'),
					'shortmonth' : _date('b'),
					'monthnumber' : _date('m'), #has zero, remove it
					'monthnumberwithzero' : _date('m'),
					'year' : _date('Y'),
					'shortyear' : _date('y'),
					'ampm' : _date('p'),
					'capitalampm' : _date('p'), #make it caps
					'12hour' : _date('I'), #has zero remove,
					'24hour' : _date('H'), #has zero
					'12hourwithzero' : _date('I'),
					'24hourwithzero' : _date('H'),
					'minutes' : _date('M'),
					'seconds' : _date('S'),
					#'Timestamp' : _date('')
					'permalink' : 'post_url'
				})
	}
	return contextMapTemplate

# def createContextMapper( initData ):

# 	context = ContextDataMapper( initData, contextMapTemplate )
# 	return context

### Sample template
content = """
	{block:title}
		{title}
		{url}
	{/block:title}
	{block:posts}
		{block:chat}
			Lets have a chat
			{block:title}
				I have a title - {title}
			{/block:title}

		        {block:Title}
		          <h3>{Title}</h3>
		        {/block:Title}
		        <table cellpadding='0' cellspacing='10px' width='100%' border='0' class='chat'>
		        {block:Lines}
		            <tr class='{Alt}'>
		            {block:Label}
		                <td class='label'>{Label}</td>
		            {/block:Label}
		            <td>{Line}</td>
		            </tr>
		        {/block:Lines}
		        </table>

		{/block:chat}
	{/block:posts}
"""
