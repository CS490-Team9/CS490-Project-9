class ASTFilter():
  '''General purpose class for filtering an abstract syntax tree (AST)
  generated by the astconverter module

  Uses 'function_names' and 'args' to filter out nodes that do not contain
  specified function names or argument names.
  '''
  def __init__(self, args):
    # Used to initialize the filter with function names and arguments that
    # it should use to filter the AST.
    self.func_args = args
    self.function_names = self.func_args.keys()

  def run(self, ast):
    '''Returns a filtered ast. 

    Filtered AST entails an AST that contains functions specified by
    'self.function_names' and argument names specified in 'self.args'.

    Arguments that call nodes are kept in functions that are not filtered out.

    Example:

    function_names = ['test']
    args = {
      'test': ['arg1']
    }

    and given an AST generated from the source
    'test(return_One(x = 1, y = 2), 3, arg1 = 4)'

    yields

    {
      "type": "call",
      "function": "test",
      "args": [
        {
          "type": "call",
          "function": "return_One",
          "args": [],
          "keywords": []
        }
      ],
      "keywords": [
        {
          "keyword": "arg1",
          "value": "4"
        }
      ]
    }

    In this case, test is returned because it is specified in 'function_names'.
    The arguments 'return_One' and 'arg1 = 4' are kept because they are a
    call argument (i.e., a function call) and a specified argument name,
    respectively. 3 is filtered out from args because it is neither of those
    types of arguments.
    '''
    result = self.filter_ast(ast.copy())

    for key in result.keys():
      if len(result[key]) > 0:
        return result
    
    return None

  def filter_ast(self, ast_nodes):
    '''Encapsulating function that filters out imports, import_froms, calls,
    and function_defs fields in the AST and returns the result.
    '''
    if not self.function_names:
      return ast_nodes
    
    new_imports = []
    for import_ast in ast_nodes['imports']:
      temp_import = self.reduce_imports(import_ast)
      if temp_import != None:
        new_imports.append(temp_import)
    ast_nodes['imports'] = new_imports

    new_calls = []
    for call in ast_nodes['calls']:
      if self.reduce_call(call) != None:
        new_calls.append(call)
    ast_nodes['calls'] = new_calls

    new_function_defs = []
    for function_def in ast_nodes['function_defs']:
      if self.reduce_function_def(function_def):
        new_function_defs.append(function_def)

    ast_nodes['function_defs'] = new_function_defs
    return ast_nodes

  def reduce_imports(self, imports_ast):
    '''Returns true if a specified function name is found in the import node.
    False otherwise.
    '''
    names = []
    module = imports_ast['module']
    for name in imports_ast['names']:
      func_name = name['name'] if module == None else module + '.' + name['name']
      if func_name in self.function_names:
        names.append(name)
    imports_ast['names'] = names

    return imports_ast if len(names) > 0 else None

  def filter_call_args(self, call_ast, func_args):
    '''Filters the 'args' and 'keywords' fields of a 'call' node such that
    only 'call' arguments are kept and keywords specified in the
    function argument dictionary are kept.
    '''
    args = []
    for arg in call_ast['args']:
      if isinstance(arg, dict) and 'type' in arg.keys() and arg['type'] == 'call':
        temp_name = self.reduce_call(arg)
        if temp_name != None:
          args.append(arg)
    call_ast['args'] = args

    keywords = []
    for keyword in call_ast['keywords']:
      if keyword['keyword'] in func_args or isinstance(keyword['value'], dict) and keyword['value']['type'] == 'call':
        if isinstance(keyword['value'], dict) and keyword['value']['type'] == 'call':
          temp_name = self.reduce_call(keyword['value'])
        keywords.append(keyword)
    call_ast['keywords'] = keywords

  def reduce_value(self, value):
    '''Acts as a 'dispatch' function that calls the appropriate reducer
    function based on value type, returns function name corresponding to
    the function that it finds in the value.
    '''
    call_name = None
    if isinstance(value, dict) and 'type' in value.keys():
      temp_name = None
      if value['type'] == 'call':
        temp_name = self.reduce_call(value)
      elif value['type'] == 'set' or value['type'] == 'list' or value['type'] == 'tuple':
        temp_name = self.reduce_iterable(value)
      elif value['type'] == 'dict':
        temp_name = self.reduce_dict(value)
      if temp_name != None:
        call_name = temp_name
    return call_name

  def reduce_dict(self, arg):
    '''Encapsulating function that filters out the key value pairs of 'dict' nodes
    and applies the same reduction to each key and value node in key value pair.

    Returns function name if a function specified in 'self.function_names' is
    found. None otherwise.
    '''
    call_name = None
    key_values = []

    for key, value in arg['key_values']:
      key_temp_name = self.reduce_value(key)
      if key_temp_name != None:
        key_values.append([key, value])
        call_name = key_temp_name
        continue
      
      value_temp_name = self.reduce_value(value)
      if value_temp_name != None:
        key_values.append([key, value])
        call_name = value_temp_name

    arg['key_values'] = key_values
    return call_name

  def reduce_iterable(self, args):
    '''Encapsulating function that filters out the elements of 'set', 'list'
    and 'tuple' nodes and applies reduction to each element node.

    Returns function name if a function specified in 'self.function_names' is
    found. None otherwise.
    '''
    call_name = None
    new_elements = []
    for arg in args['elements']:
      temp_name = self.reduce_value(arg)
      if temp_name != None:
        call_name = temp_name
        new_elements.append(arg)
    args['elements'] = new_elements
    return call_name

  def search_function_name(self, instance):
    '''Search functions that are called from other functions for names that are
    specified in self.function_names
    
    Example:
    test().x.test()

    returns test if it is specified in self.function_names
    ''' 
    if isinstance(instance, dict):
      if 'instance' in instance.keys():
        call_name = self.search_function_name(instance['instance'])
        if instance['attr'] in self.function_names:
          return instance['attr']
        return call_name
      else:
        return self.reduce_value(instance)
    elif isinstance(instance, str) and instance in self.function_names:
      return instance
    return None

  def reduce_call(self, call_ast):
    '''Encapsulating function that filters out the arguments and keywords of
    'call' nodes and applies reduction to each argument and keyword value node.

    Returns function name if a function specified in 'self.function_names' is
    found. None otherwise.
    '''
    call_name = self.search_function_name(call_ast['function'])
    if call_name != None:
      self.filter_call_args(call_ast, self.func_args[call_name])
      return call_name

    
    call_name = None
    args = []
    for arg in call_ast['args']:
      temp_name = self.reduce_value(arg)
      if temp_name != None:
        call_name = temp_name
        args.append(arg)

    keywords = []
    for keyword in call_ast['keywords']:
      if call_name != None and keyword['keyword'] in self.func_args[call_name]:
        keywords.append(keyword)
      else:
        temp_name = self.reduce_value(keyword['value'])
        if temp_name != None:
          keywords.append(keyword)
          call_name = temp_name

    call_ast['args'] = args
    call_ast['keywords'] = keywords
    return call_name if len(args) > 0 or len(keywords) > 0 else None

  def reduce_function_def(self, function_def_ast):
    '''Encapsulating function that filters out the calls and function_defs of
    'function_def' nodes and applies reductions to nodes in 'calls' and nodes
    in 'function_defs'.

    Returns True if a function specified in 'self.function_names' is found.
    False otherwise.
    '''
    if function_def_ast['name'] in self.function_names:
      return True
    
    calls = []
    for call in function_def_ast['calls']:
      if self.reduce_call(call) != None:
        calls.append(call)
    
    function_defs = []
    for function_def in function_def_ast['function_defs']:
      if self.reduce_function_def(function_def):
        function_defs.append(function_def)
    
    function_def_ast['calls'] = calls
    function_def_ast['function_defs'] = function_defs
    return len(calls) > 0 or len(function_defs) > 0

