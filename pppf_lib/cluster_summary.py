"""
Summarize the cluster information. We want to get the exemplar, the number of proteins,
and the number of functions. May also want to include information like size of proteins
etc.
"""

import os
import sys
import argparse

from roblib import bcolors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', help='', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()
