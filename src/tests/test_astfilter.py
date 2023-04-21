import ast
import unittest

from ..ast.astconverter import ASTConverter
from ..ast.astfilter import ASTFilter

class AstFilterTestClass(unittest.TestCase):
  def test_run_imports(self):
    source ="""
import ast
import math
from math import random as r"""

    expected = {
      'imports': [{
        'type': 'import',
        'module': None,
        'names': [{
          'name': 'ast',
          'alias': None
        }]
      }, {
        'type': 'import',
        'module': None,
        'names': [{
          'name': 'math',
          'alias': None
        }]
      }, {
        'type': 'import',
        'module': 'math',
        'names': [{
          'name': 'random',
          'alias': 'r'
        }]
      }],
      'calls': [],
      'function_defs': []
    }

    args = {
      'ast': [],
      'math.random': [],
      'math': [],
      'r': []
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)
  
  def test_run_call(self):
    source ="""print(4, y = 3, test = 7)"""

    expected = {
      'imports': [],
      'calls': [{
        'type': 'call',
        'function': 'print',
        'args': [],
        'keywords': [{
          'keyword': 'test',
          'value': {
            'type': 'constant',
            'value': 7
          }
        }]
      }],
      'function_defs': []
    }

    args = {
      'print': ['test']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)
  
  def test_run_call_arg(self):
    source ="""print(test(3, x = 4), test = 7)"""

    expected = {
      'imports': [],
      'calls': [{
        'type': 'call',
        'function': 'print',
        'args': [{
          'type': 'call',
          'function': 'test',
          'args': [],
          'keywords': [{
            'keyword': 'x',
            'value': {
              'type': 'constant',
              'value': 4
            }
          }]
        }],
        'keywords': []
      }],
      'function_defs': []
    }

    args = {
      'test': ['x'],
      'print': []
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)
  
  def test_run_call_keyword(self):
    source ="""print(test = test(3, x = 4), hello = 7)"""

    expected = {
      'imports': [],
      'calls': [{
        'type': 'call',
        'function': 'print',
        'args': [],
        'keywords': [{
          'keyword': 'test',
          'value': {
            'type': 'call',
            'function': 'test',
            'args': [],
            'keywords': [{
              'keyword': 'x',
              'value': {
                'type': 'constant',
                'value': 4
              }
            }]
          }
        }, {
          'keyword': 'hello',
          'value': {
            'type': 'constant',
            'value': 7
          }
        }]
      }],
      'function_defs': []
    }

    args = {
      'test': ['x'],
      'print': ['test', 'hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)

  def test_run_function_def(self):
    source ="""
def func_def(x, y, z):
  if z > 0:
    print(test = test(3, x = 4), hello = 7)
  else:
    print()"""

    expected = {
      'imports': [],
      'calls': [],
      'function_defs': [{
        'type': 'function_def',
        'name': 'func_def',
        'args': ['x', 'y', 'z'],
        'calls': [{
          'type': 'call',
          'function': 'print',
          'args': [],
          'keywords': [{
            'keyword': 'test',
            'value': {
              'type': 'call',
              'function': 'test',
              'args': [],
              'keywords': []
            }
          }, {
            'keyword': 'hello',
            'value': {
              'type': 'constant',
              'value': 7
            }
          }]
        }, {
          'type': 'call',
          'function': 'print',
          'args': [],
          'keywords': []
        }],
        'function_defs': []
      }]
    }

    args = {
      'print': ['hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)

  def test_all_nodes_with_import_substitution(self):
    source ="""
import print as y, func as func_name
func_name()
y()
def func_def(x, y, z):
  if z > 0:
    print(test = test(3, x = 4), hello = 7)
  else:
    func_name()"""

    expected = {
      'imports': [{
        'type': 'import',
        'module': None,
        'names': [{
          'name': 'print',
          'alias': 'y'
        }]
      }],
      'calls': [{
        'type': 'call',
        'function': 'print',
        'args': [],
        'keywords': []
      }],
      'function_defs': [{
        'type': 'function_def',
        'name': 'func_def',
        'args': ['x', 'y', 'z'],
        'calls': [{
          'type': 'call',
          'function': 'print',
          'args': [],
          'keywords': [{
            'keyword': 'test',
            'value': {
              'type': 'call',
              'function': 'test',
              'args': [],
              'keywords': []
            }
          }, {
            'keyword': 'hello',
            'value': {
              'type': 'constant',
              'value': 7
            }
          }]
        }],
        'function_defs': []
      }]
    }

    args = {
      'print': ['hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    converted_ast = astconverter.run(ast.parse(source))
    actual = astfilter.run(converted_ast)
    self.assertDictEqual(actual, expected)

if __name__ == '__main__':
  unittest.main()
