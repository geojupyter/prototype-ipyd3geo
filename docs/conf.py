"""Sphinx configuration for the ipyd3geo docs."""

project = "ipyd3geo"
author = "Benjamin Szeghy"
copyright = "2026, Benjamin Szeghy"

extensions = [
    "jupyterlite_sphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = ["superpowers"]

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "external_links": [{"name": "Try", "url": "lite/lab/index.html"}],
}

jupyterlite_contents = ["../examples/*"]
jupyterlite_dir = "."

autodoc_member_order = "bysource"
