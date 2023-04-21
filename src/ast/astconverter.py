from collections import deque
import ast

class ASTConverter:
  '''General purpose class for converting an abstract syntax tree (AST) generated
  by the Python ast module
  '''

  def __init__(self):
    # Used for substitutions when aliases are encountered in the conversion
    # process.
    self.aliases = {}

  def run(self, root):
    '''We are only interested in Import, ImportFrom, Call, and FunctionDef nodes.
    
    This function returns a simplified JSON representation of an AST,
    segregated by Import, ImportFrom, Call, and FunctionDef nodes.
    '''
    return self.walk_ast(root)


  def convert_arguments(self, root):
    '''Converts arguments to dictionary structures dependent on the type
    of the node.'''

    if isinstance(root, ast.Call):
      return self.convert_call(root)
    elif isinstance(root, ast.Name):
      return self.convert_name(root)
    elif isinstance(root, ast.FunctionDef):
      return self.convert_function_def(root)
    elif isinstance(root, (ast.Import, ast.ImportFrom)):
      return self.convert_import(root)
    elif isinstance(root, ast.Tuple):
      tuple_dict = {}
      tuple_dict['type'] = 'tuple'
      elts = []
      for node in root.elts:
        elts.append(self.convert_arguments(node))
      tuple_dict['elements'] = elts
      return tuple_dict
    elif isinstance(root, ast.List):
      list_dict = {}
      list_dict['type'] = 'list'
      elts = []
      for node in root.elts:
        elts.append(self.convert_arguments(node))
      list_dict['elements'] = elts
      return list_dict
    elif isinstance(root, ast.Set):
      set_dict = {}
      set_dict['type'] = 'set'
      elts = []
      for node in root.elts:
        elts.append(self.convert_arguments(node))
      set_dict['elements'] = elts
      return set_dict
    elif isinstance(root, ast.Dict):
      dict_dict = {}
      dict_dict['type'] = 'dict'
      keys = []
      values = []

      for key in root.keys:
        keys.append(self.convert_arguments(key))
      
      for value in root.values:
        values.append(self.convert_arguments(value))
      
      dict_dict['key_values'] = list(zip(keys, values))
      return dict_dict
    elif isinstance(root, ast.Constant):
      constant = {}
      constant['type'] = 'constant'
      constant['value'] = root.value
      return constant
    else:
      return ast.unparse(root)

  def get_function_names(self, root):
    '''Returns all the function names of a node as a string.
    Example:
    return_test().walk().hello_world()
    
    yields
    
    return_test.walk.hello_world
    '''
    if isinstance(root, ast.Name):
      if root.id in self.aliases:
        return self.aliases[root.id]
      return root.id
    elif isinstance(root, ast.Attribute):
      root_value = self.get_function_names(root.value)
      if isinstance(root_value, str):
        return root_value + '.' + root.attr
      attribute = {}
      attribute['instance'] = root_value
      attribute['attr'] = root.attr
      return attribute
    elif isinstance(root, ast.Call):
      func_name = self.convert_call(root)
      return func_name
    else:
      key = ast.unparse(root)
      if key in self.aliases:
        return self.aliases[key]
      return key

  def convert_name(self, root):
    '''Converts Name nodes into a dictionary with the fields 'type' and 'value'
    '''
    name = {}
    name['type'] = 'name'
    name['value'] = root.id
    return name

  def convert_call(self, root):
    '''Converts Call nodes into a dictionary with the fields 'function', args',
    and 'keywords'.

    Example:
    hello_world(test = 3, 7)

    yields

    {
      'function': 'hello_world',
      'args': [
        '7'
      ],
      'keywords': [
        {
          'keyword': 'test',
          'value': '3'
        }
      ]
    }

    '''
    call = {}
    call['type'] = 'call'
    call['function'] = self.get_function_names(root.func)

    args = []
    for node in root.args:
      args.append(self.convert_arguments(node))
    
    keywords = []
    for node in root.keywords:
      keyword = {}
      keyword['keyword'] = node.arg
      keyword['value'] = self.convert_arguments(node.value)
      keywords.append(keyword)

    call['args'] = args
    call['keywords'] = keywords
    return call

  def convert_import(self, root):
    '''Converts ImportFrom nodes into a dictionary with 'module' and 'names'
    fields.

    Example:

    from ast import parse as p
    
    yields

    {
      'module': 'ast'
      'names': {
        {
          'name': 'ast.parse',
          'alias': 'p'
        }
      }
    }
    '''
    import_res = {}
    import_res['type'] = 'import'
    import_res['module'] = None
    if isinstance(root, ast.ImportFrom) and root.module != None:
      import_res['module'] = root.module
    
    import_aliases = []
    for z in root.names:
      alias = {}
      alias['name'] = z.name
      alias['alias'] = z.asname

      if isinstance(root, ast.ImportFrom) and root.module != None:
        alias_name = root.module + '.' + z.name
      else:
        alias_name = z.name
      
      if z.asname != None:
        self.aliases[z.asname] = alias_name
      else:
        self.aliases[z.name] = alias_name
      import_aliases.append(alias)
    
    import_res['names'] = import_aliases
    return import_res

  def convert_function_defs(self, root):
    '''Converts Function nodes into a dictionary with the fields 'names',
    'args', 'calls', and 'function_defs'.

    'calls' and 'function_defs' are used to represent calls and function
    definitions, respectively, that are nested within the body of the
    function definition.

    Example:
    def hello_world(test = 3):
      print()
      print_out()

      def test_1():
        return None

    yields

    {
      'name': 'hello_world',
      'args': [
        'test'
      ],
      'calls': [
        {
          "function": [
            "print"
          ],
          "args": [],
          "keywords": []
        },
        {
          "function": [
            "print_out"
          ],
          "args": [],
          "keywords": []
        }
      ],
      'function_defs': [
        {
          "name": "test_1",
          "args": [],
          "calls": [],
          "function_defs": []
        }
      ]
    }

    '''
    function = {}
    function['type'] = 'function_def'
    function['name'] = root.name
    function['args'] = [self.convert_arguments(arg) for arg in root.args.args]
    
    calls = []
    function_defs = []
    for item in root.body:
      nested_values = self.walk_function_def((item))
      calls = calls + nested_values['calls']
      function_defs = function_defs + nested_values['function_defs']
    
    function['calls'] = calls
    function['function_defs'] = function_defs
    return function

  def walk_function_def(self, root):
    '''Traverses FunctionDef nodes to find nested call and function definition
    nodes.
    
    This function traverses (in BFS fashion) function definitions and
    returns a dictionary containing 'call' and 'function_defs' fields.
    This is used to find nested Call and FunctionDef nodes in the original
    FunctionDef node.
    '''

    res = {}
    res['calls'] = []
    res['function_defs'] = []

    todo = deque([root])
    while todo:
      node = todo.popleft()

      if isinstance(node, ast.Call):
        res['calls'].append(self.convert_call(node))
      elif isinstance(node, ast.FunctionDef):
        res['function_defs'].append(self.convert_function_defs(node))
      else:
        # If-statement guarantees a single visit for Call/FunctionDef
        # nodes.
        todo.extend(ast.iter_child_nodes(node))
    return res


  def walk_ast(self, node):
    '''Traverses AST to find Import, ImportFrom, Call, and FunctionDef nodes.
    
    This function traverses (in BFS fashion) the AST and returns a dictionary
    containing 'imports', 'call', and 'function_defs' fields.
    
    We are mainly interested in Import, ImportFrom, Call, and FunctionDef
    nodes.
    '''

    res = {}

    res['imports'] = []
    res['calls'] = []
    res['function_defs'] = []

    todo = deque([node])
    while todo:
      node = todo.popleft()

      if isinstance(node, (ast.Import, ast.ImportFrom)):
        res['imports'].append(self.convert_import(node))
      elif isinstance(node, ast.Call):
        res['calls'].append(self.convert_call(node))
      elif isinstance(node, ast.FunctionDef):
        res['function_defs'].append(self.convert_function_defs(node))
      else:
        # If-statement guarantees a single visit for Call/FunctionDef
        # nodes.
        todo.extend(ast.iter_child_nodes(node))

    return res
