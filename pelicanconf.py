#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

### bootstrap3 theme settings
THEME = 'pelican-bootstrap3'
BOOTSTRAP_THEME = "simplex"

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
PLUGIN_PATHS = ["pelican-plugins"]
PLUGINS = ['i18n_subsites', 'pelicanfly']
PADDED_SINGLE_COLUMN_STYLE = False
BANNER = 'images/banner.jpg'
BOOTSTRAP_NAVBAR_INVERSE = False
HIDE_SIDEBAR = True
CUSTOM_CSS = 'extra/custom.css'
ARTICLE_EXCLUDES = ['simplex']
PYGMENTS_STYLE = "monokai"

#### pathing
PATH = 'content'
STATIC_PATHS = ['images','pdfs','extra']

#### site attributes
TIMEZONE = 'America/Los_Angeles'
DEFAULT_LANG = 'en'
RELATIVE_URLS = False
DELETE_OUTPUT_DIRECTORY = False

### menu settings
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = True

### site descriptors
AUTHOR = 'Wayde Gilliam'
SITENAME = "waydegg.com"

### feed settings
DEFAULT_PAGINATION = 5
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

CSS_FILE = "bootstrap.simplex.min.css"