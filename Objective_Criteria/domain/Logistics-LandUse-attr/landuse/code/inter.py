import geopandas as gpd
import os
import argparse
import pdb
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely.ops import transform
import pyproj
from functools import partial
import sys
import shapely.ops as ops
sys.path.append('../../../../scripts/Utils/')
from poly_utils import polygon_list, graphs
from matplotlib import pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def overlap_calc()