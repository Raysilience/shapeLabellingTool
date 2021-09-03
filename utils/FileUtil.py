#!usr/bin/env python
# coding utf-8
'''
@File       :FileUtil.py
@Copyright  :CV Group
@Date       :9/1/2021
@Author     :Rui
@Desc       :
'''
import pandas as pd
import numpy as np
import os


def csv_to_arr(filepath):
    df = pd.read_csv(filepath, names=['x', 'y'])
    return np.asarray(list(zip(df['x'], df['y'])), dtype=np.int32)

def mkdir(path:str):
    path = path.strip().rstrip("\\")
    is_exist = os.path.exists(path)
    if not is_exist:
        os.makedirs(path)
        return True
    else:
        return False