#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

### PUBLISH SETTINGS
SITEURL = 'https://waydegg.com'
DELETE_OUTPUT_DIRECTORY = False
FEED_ALL_ATOM = 'feeds/all.atom.xml'

GOOGLE_ANALYTICS = "UA-156477838-1"

CSS_FILE = "bootstrap.simplex.min.css"