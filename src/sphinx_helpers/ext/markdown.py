from ..builders import MarkdownBuilder


def setup(app):
    app.add_builder(MarkdownBuilder)
    app.add_config_value("markdown_include_manifest", default=False, rebuild="env")
