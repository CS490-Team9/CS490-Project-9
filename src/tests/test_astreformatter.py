import ast
import unittest

from ..ast.astconverter import ASTConverter
from ..ast.astfilter import ASTFilter
from ..ast.astreformatter import ASTReformatter

class AstReformatterTestClass(unittest.TestCase):
  def test_run_call(self):
    source ="""print(4, y = 3, test = 7)"""

    expected = [
      {
        'type': 'call',
        'function': 'print',
        'args': [],
        'keywords': [{
          'keyword': 'test',
          'value': 7
        }]
      }
    ]

    args = {
      'print': ['test']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    self.assertListEqual(actual, expected)
  
  def test_run_call_arg(self):
    source ="""print(test(3, x = 4), test = 7)"""

    expected = [{
      'type': 'call',
      'function': 'test',
      'args': [],
      'keywords': [{
        'keyword': 'x',
        'value': 4
      }]
    }, {
      'type': 'call',
      'function': 'print',
      'args': [],
      'keywords': [{
        'keyword': 'test',
        'value': 7
      }]
    }]

    args = {
      'test': ['x'],
      'print': ['test']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    print(actual)
    self.assertListEqual(actual, expected)
  
  def test_run_call_keyword(self):
    source ="""print(test = test(3, x = 4), hello = 7)"""

    expected = []

    args = {
      'print': ['test', 'hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    self.assertListEqual(actual, expected)

  def test_run_function_def(self):
    source ="""
def func_def(x, y, z):
  if z > 0:
    print(test = test(3, x = 4), hello = 7)
  else:
    print()"""

    expected = [{
      'type': 'call',
      'function': 'print',
      'args': [],
      'keywords': [{
        'keyword': 'hello',
        'value': 7
      }]
    }]

    args = {
      'print': ['hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    self.assertListEqual(actual, expected)

  def test_all_nodes_with_import_substitution(self):
    source ="""
import print as y, func as func_name
func_name()
y(hello = 3)
def func_def(x, y, z):
  if z > 0:
    y(test = test(3, x = 4), hello = 7)
  else:
    func_name()"""

    expected = [
    {
      'type': 'call',
      'function': 'print',
      'args': [],
      'keywords': [{
        'keyword': 'hello',
        'value': 3
      }]
    }, {
      'type': 'call',
      'function': 'print',
      'args': [],
      'keywords': [{
        'keyword': 'hello',
        'value': 7
      }]
    }]

    args = {
      'print': ['hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    self.assertListEqual(actual, expected)

  def test_chained_functions(self):
    source ="""
from x import print as y
y(hello = 3).y(hello = 2).y(hello = 1)
x.y(hello = 1)
x.print(hello = 4)"""

    expected = [{
      'type': 'call',
      'function': 'x.print',
      'args': [],
      'keywords': [{
        'keyword': 'hello',
        'value': 3
      }]
    }, {
      'type': 'call',
      'function': 'x.print',
      'args': [],
      'keywords': [{
        'keyword': 'hello',
        'value': 4
      }]
    }]

    args = {
      'x.print': ['hello']
    }
    astconverter = ASTConverter()
    astfilter = ASTFilter(args)
    astreformatter = ASTReformatter(args)
    
    converted_ast = astconverter.run(ast.parse(source))
    filtered_ast = astfilter.run(converted_ast)
    actual = astreformatter.run(filtered_ast)
    self.assertListEqual(actual, expected)

if __name__ == '__main__':
  unittest.main()
