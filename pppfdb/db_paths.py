
"""
The default paths are ../data/databases

Feel free to edit if you have the databases in different places
"""

import os

phagedb = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "databases", "phages.sql")
clustersdb = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "databases", "clusters.sql")