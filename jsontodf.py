import pandas as pd
import json
import os
import sys
import string
import shutil
import re

folder = 'outputs'
def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

subfolders, files = run_fast_scandir(folder, [".json"])

bigDf = pd.DataFrame()
for f in files:
    projectName = f[8:].split('/')[0]
    df = pd.read_json(f)
    df['project_type'] = projectName
    frames = [bigDf, df]
    bigDf = pd.concat(frames)

bigDf = bigDf.reset_index()
bigDf = bigDf[['project_type', 'function', 'keywords']]

for index, row in bigDf.iterrows():
    newDict = {}
    if len(row['keywords']) > 0:
        for i in row['keywords']:
            nk = i['keyword']
            nv = i['value']
            newDict[nk] = nv
        bigDf.at[index, 'keywords'] = newDict
    else :
        bigDf = bigDf.drop(index )


#bigDf.to_csv('testProgramAnalysis')


