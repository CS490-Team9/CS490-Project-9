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
          'names': [
            {
              'name': 'ast',
              'alias': None
            }]
        },
        {
          'type': 'import',
          'names': [
            {
              'name': 'math',
              'alias': None
            }
          ]
        }
      ],
      'import_froms': [
        {
          'module': 'math',
          'type': 'import_from',
          'names': [
            {
              'name': 'math.random',
              'alias': None
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
    print(actual)
    self.assertDictEqual(actual, expected)
  
  def test_run_call(self):
    source ="""print(3, test = 7)"""

    expected = {
      'imports': [],
      'import_froms': [],
      'calls': [
        {
          'type': 'call',
          'function': 'print',
          'args': [
            '3'
          ],
          'keywords': [
            {
              'keyword': 'test',
              'value': '7'
            }
          ]
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
      'import_froms': [],
      'calls': [
        {
          'type': 'call',
          'function': 'print',
          'args': [
            {
              'type': 'call',
              'function': 'test',
              'args': [
                  '3'
              ],
              'keywords': [
                {
                  'keyword': 'x',
                  'value': '4'
                }
              ]
            }
          ],
          'keywords': [
            {
              'keyword': 'test',
              'value': '7'
            }
          ]
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
      'import_froms': [],
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
                  '3'
                ],
                'keywords': [
                  {
                    'keyword': 'x',
                    'value': '4'
                  }
                ]
              }
            },
            {
              'keyword': 'hello',
              'value': '7'
            }
          ]
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
      'import_froms': [],
      'calls': [],
      'function_defs': [
        {
          'type': 'function_def',
          'name': 'func_def',
          'args': [
            'x',
            'y',
            'z'],
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
                      '3'
                    ],
                    'keywords': [
                      {
                        'keyword': 'x',
                        'value': '4'
                      }
                    ]
                  }
                },
                {
                  'keyword': 'hello',
                  'value': '7'
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
        }
      ]
    }

    astconverter = ASTConverter()
    actual = astconverter.run(ast.parse(source))
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
      'imports': [
        {
          'type': 'import',
          'names': [
            {
              'name': 'print',
              'alias': 'y'
            },
            {
              'name': 'func',
              'alias': 'func_name',
            }
          ]
        }
      ],
      'import_froms': [],
      'calls': [
        {
          'type': 'call',
          'function': 'func',
          'args': [],
          'keywords': []
        },
        {
          'type': 'call',
          'function': 'print',
          'args': [],
          'keywords': []
        }
      ],
      'function_defs': [
        {
          'type': 'function_def',
          'name': 'func_def',
          'args': [
            'x',
            'y',
            'z'],
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
                      '3'
                    ],
                    'keywords': [
                      {
                        'keyword': 'x',
                        'value': '4'
                      }
                    ]
                  }
                },
                {
                  'keyword': 'hello',
                  'value': '7'
                }
              ]
            },
            {
              'type': 'call',
              'function': 'func',
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
