"""
Load the sequences from GenBank.

This is the correct way to do this!
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
