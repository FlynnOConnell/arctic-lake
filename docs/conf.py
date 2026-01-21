# sphinx configuration for mbo docs

import os
import sys
from pathlib import Path

project = "MBO Docs"
author = "MBO"
copyright = "2026, Miller Brain Observatory"

exclude_patterns = ["Thumbs.db", ".DS_Store", "_build"]

# myst markdown extensions
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "html_image",
    "tasklist",
]

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
]

source_suffix = [".rst", ".md"]

myst_admonition_enable = True
myst_html_img_enable = True

templates_path = ["_templates"]
html_static_path = ["_static"]

suppress_warnings = [
    "misc.highlighting_failure",
    "myst.header",
    "toc.not_included",
    "myst.xref_missing",
    "myst.topmatter",
    "docutils",
]

html_title = "MBO Docs"
html_theme = "sphinx_book_theme"
html_css_files = ["custom.css"]
html_copy_source = True

html_theme_options = {
    "show_toc_level": 1,
    "show_nav_level": 1,
    "navigation_depth": 1,
    "collapse_navigation": True,
    "navbar_align": "content",
    "home_page_in_toc": True,
}

# force dark mode
html_context = {
    "default_mode": "dark",
}
