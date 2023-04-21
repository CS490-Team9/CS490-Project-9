import ast
import unittest

from ..ast.astconverter import ASTConverter

class AstConverterTestClass(unittest.TestCase):
  def test_run_imports(self):
    source ="""
import ast
import math
from math import random as r
r()"""

    expected = {
      'imports': [
        {
          'type': 'import',
          'module': None,
          'names': [
            {
              'name': 'ast',
              'alias': None
            }
          ]
        },
        {
          'type': 'import',
          'module': None,
          'names': [
            {
              'name': 'math',
              'alias': None
            }
          ]
        },
        {
          'type': 'import',
          'module': 'math',
          'names': [
            {
              'name': 'random',
              'alias': 'r'
            }
          ]
        }
      ],
      'calls': [
        {
          'type': 'call',
          'function': 'math.random',
          'args': [],
          'keywords': []
        }
      ],
      'function_defs': []
    }

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
    self.assertDictEqual(actual, expected)
  
  def test_run_call(self):
    source ="""print(3, test = 7)"""

    expected = {
      'imports': [],
      'calls': [{
        'type': 'call',
        'function': 'print',
        'args': [{
          'type': 'constant',
          'value': 3
        }],
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

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
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
          'args': [{
            'type': 'constant',
            'value': 3
          }],
          'keywords': [{
            'keyword': 'x',
            'value': {
              'type': 'constant',
              'value': 4
            }
          }]
        }],
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

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
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
            'args': [{
              'type': 'constant',
              'value': 3
            }],
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

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
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
                  'args': [{
                    'type': 'constant',
                    'value': 3
                  }],
                  'keywords': [{
                    'keyword': 'x',
                    'value': {
                      'type': 'constant',
                      'value': 4
                    }
                  }]
                }
              },
              {
                'keyword': 'hello',
                'value': {
                  'type': 'constant',
                  'value': 7
                }
              }
            ]
          },
          {
            'type': 'call',
            'function': 'print',
            'args': [],
            'keywords': []
          }
        ],
        'function_defs': []
      }]
    }

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
    self.assertDictEqual(actual, expected)

  def test_all_nodes_with_import_substitution(self):
    source ="""
from test import print as y, func as func_name
func_name()
y()
def func_def(x, y, z):
  if z > 0:
    print(test = test(3, x = 4), hello = 7)
  else:
    func_name()"""

    expected = {
      'imports': [
        {
          'type': 'import',
          'module': 'test',
          'names': [
            {
              'name': 'print',
              'alias': 'y'
            },
            {
              'name': 'func',
              'alias': 'func_name'
            }
          ]
        }
      ],
      'calls': [
        {
          'type': 'call',
          'function': 'test.func',
          'args': [],
          'keywords': []
        },
        {
          'type': 'call',
          'function': 'test.print',
          'args': [],
          'keywords': []
        }
      ],
      'function_defs': [
        {
          'type': 'function_def',
          'name': 'func_def',
          'args': ['x', 'y', 'z'],
          'calls': [
            {
              'type': 'call',
              'function': 'print',
              'args': [],
              'keywords': [
                {
                  'keyword': 'test',
                  'value': {
                    'type': 'call',
                    'function': 'test',
                    'args': [
                      {
                        'type': 'constant',
                        'value': 3
                      }
                    ],
                    'keywords': [
                      {
                        'keyword': 'x',
                        'value': {
                          'type': 'constant',
                          'value': 4
                        }
                      }
                    ]
                  }
                },
                {
                  'keyword': 'hello',
                  'value': {
                    'type': 'constant',
                    'value': 7
                  }
                }
              ]
            },
            {
              'type': 'call',
              'function': 'test.func',
              'args': [],
              'keywords': []
            }
          ],
          'function_defs': []
        }
      ]
    }

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
    self.assertDictEqual(actual, expected)

if __name__ == '__main__':
  unittest.main()
