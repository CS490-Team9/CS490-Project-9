#!/usr/bin/env python3

from asttojson import convert_ast_to_json
from filecrawler import crawl_directory
from ignore import create_ignore_dict
from parser import generate_file_ast

import ast
import json
import os
import sys

def main():
  if len(sys.argv) < 3:
    print('Python project path not found!\nUsage: ./main.py <relative/absolute project path> <output directory>')
    return
  
  project_path = sys.argv[1]
  print('Path entered:', os.path.abspath(project_path))

  # Retrieve file paths that are not 'ignored' by the .ignore file.
  file_paths = crawl_directory(project_path, create_ignore_dict())

  # Generate file AST for each path.
  file_ast = generate_file_ast(file_paths)

  # Convert each AST to a JSON string.
  results = []
  for ast in file_ast:
    results.append(convert_ast_to_json(ast))

  # Check if valid output path
  output_path = sys.argv[2]
  if len(results) > 0:
    if not os.path.exists(output_path):
      os.makedirs(output_path)
    else:
      print('Error: Output directory already exists')
      return
    
    # Each file that is found is output under the output directory
    # The naming convention of the output files is
    # [0, number of files with valid JSON data).
    count = 0
    for result in results:
      if len(result) > 0:
        output_file = open(output_path + '/' + str(count), 'w')
        output_file.write(json.dumps(result, indent = 2))
        output_file.close()
        count = count + 1
main()
