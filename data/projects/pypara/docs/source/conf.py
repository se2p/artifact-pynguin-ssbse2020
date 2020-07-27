import pypara

# -- Project information -----------------------------------------------------

project = "pypara"
copyright = "2020, Vehbi Sinan Tunalioglu"
author = "Vehbi Sinan Tunalioglu"
release = pypara.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.graphviz",
    "sphinxcontrib.apidoc",
]
templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for APIDOC ------------------------------------------------------

apidoc_module_dir = "../../pypara"
apidoc_output_dir = "api/"
apidoc_separate_modules = True
apidoc_toc_file = "index"
apidoc_module_first = True
apidoc_extra_args = ["--private", "--no-toc"]

# -- Additional configuration ------------------------------------------------

rst_prolog = f"""
.. |pypara-version| replace:: { release }
"""
