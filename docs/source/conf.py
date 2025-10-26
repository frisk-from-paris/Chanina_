import os
import sys


sys.path.insert(0, os.path.abspath('../../src'))
sys.path.insert(0, os.path.abspath("/home/leo/.cache/pypoetry/virtualenvs/chanina-Iv_yl646-py3.12"))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Chanina'
copyright = '2025, Frisk'
author = 'Frisk'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
templates_path = ['_templates']
exclude_patterns = []
autodoc_mock_imports = [
    "celery",
    "kombu",
    "playwright",
    "argparse",
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
autosummary_generate = True

def setup(app):
    pass
    app.add_css_file("style.css")
  
