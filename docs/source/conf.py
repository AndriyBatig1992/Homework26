import sys
import os

sys.path.insert(0, os.path.abspath('../../'))

project = 'App Contacts'
copyright = '2023, Andriy'
author = 'Andriy'


extensions = ['sphinx.ext.autodoc']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']

print("Current working directory:", os.getcwd())

# Вивести шлях до модулів
print("Path to modules:")
for path in sys.path:
    print(path)

# Здійснити вивід до лог-файлу
import logging
logging.basicConfig(filename='sphinx_debug.log', level=logging.DEBUG)

autodoc_mock_imports = ["asyncpg"]
html_theme = 'alabaster'
html_static_path = ['_static']
