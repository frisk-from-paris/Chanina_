from sphinx.cmd.build import main as sphinx_main


def run():
    sphinx_main([
        "-b", "html",
        "docs/source",
        "docs/_build/html"
    ])
