#!/usr/bin/env python3

from src.ast.astconverter import ASTConverter
from src.ast.astfilter import ASTFilter
from src.ast.astreformatter import ASTReformatter
from src.output_gen.output import create_output_directory
from src.readers.filecrawler import crawl_directory
from src.readers.ignore import create_ignore_dict
from src.readers.parser import generate_file_ast
from src.readers.readfunctionnames import read_function_names

import ast
import json
import os
import sys

def main():
  if len(sys.argv) < 3:
    print('Error: Not enough arguments\nUsage: ./main.py <relative/absolute project path> <output directory>')
    return
  
  project_path = os.path.abspath(sys.argv[1])
  if not os.path.exists(project_path):
    print('Error: Invalid path entered -', project_path)
    return
  else:
    print('Input path entered:', project_path)
  
  output_path = os.path.abspath(sys.argv[2])
  if os.path.exists(output_path):
    print('Error: Output directory already exists -', output_path)
    return

  # Retrieve file paths that are not 'ignored' by the .ignore file.
  file_paths = crawl_directory(project_path, create_ignore_dict())

  # Generate file AST for each path.
  file_asts = generate_file_ast(file_paths)

  func_args = read_function_names('./function_names.json')

  # Convert each AST to a JSON string.
  results = []
  for [path, gen_ast] in file_asts:
    ast_converter = ASTConverter()
    converted_ast = ast_converter.run(gen_ast)

    ast_filter = ASTFilter(func_args)
    filtered_ast = ast_filter.run(converted_ast)
    if filtered_ast != None:
      ast_reformatter = ASTReformatter(func_args)
      reformatted_ast = ast_reformatter.run(converted_ast)
      results.append([path, reformatted_ast])

  # Create the output directory if there is something to output.
  if len(results) > 0:
    os.makedirs(output_path)
    print('Output path entered:', output_path)
  else:
    print('Note: Specified project directory resulted in empty output.')
    return

  # Each file that is found is output under the output directory.
  # The files are output accordining to their name and extension
  # with '_output' attached. Ex: test.py => test_py_output
  for [path, ast_json] in results:
    if len(ast_json) > 0:
      # Create the output directory
      output_dir = create_output_directory(path, project_path, output_path)

      # Output the JSON file.
      output_file = open(output_dir, 'w')
      output_file.write(json.dumps(ast_json, indent = 2))
      output_file.close()
main()
