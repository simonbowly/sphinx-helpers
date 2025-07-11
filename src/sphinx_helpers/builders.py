import json
import pathlib

import docutils.nodes
import yaml
from sphinx.builders.text import TextBuilder
from sphinx.util.logging import getLogger
from sphinx.writers.text import TextTranslator

from .writer import Rewriter, TextRenderer

logger = getLogger(__name__)


class FallbackTextTranslator(TextTranslator):
    def unknown_visit(self, node):
        # Ignore unknown nodes
        logger.warning("Skip unknown node: %s", node.__class__.__name__)

    def unknown_departure(self, node):
        # Ignore unknown nodes
        pass


class SimpleMarkdownBuilder(TextBuilder):
    """Simple markdown builder. Piggy-backs on the text builder by rewriting
    some parts of the doctree before the build."""

    # These are used by the parent class implementation of builder methods
    # - 'name' sets the output directory
    # - 'out_suffix' sets the file extension (added to {outdir}/{docname})
    # - 'format' should stay as set by the parent (in this case, 'text') as
    #   it affects custom node type registration for builders and translators

    name = "markdown"
    out_suffix = ".md"
    default_translator_class = FallbackTextTranslator

    def __init__(self, app, env):
        super().__init__(app, env)
        self.text_renderer = TextRenderer(app, env)
        self._include_header = app.config.markdown_include_header

    def init(self):
        super().init()
        self.text_renderer.init()

    def get_header_data(self, docname, doctree):
        # FIXME should this also follow ManifestMixin.get_title?
        title_node = doctree.next_node(docutils.nodes.title)
        title = title_node.astext() if title_node else None
        url = f"{self._metadata_base_url}/{docname}.md"
        return dict(title=title, url=url)

    def format_header(self, docname, doctree):
        header_data = self.get_header_data(docname, doctree)
        return "".join(
            [
                "---\n",
                yaml.safe_dump(header_data),
                "---\n",
            ]
        )

    def prepare_writing(self, docnames):
        super().prepare_writing(docnames)
        self.text_renderer.prepare_writing(docnames)

    def write_doc(self, docname, doctree):
        if self._include_header:
            header = self.format_header(docname, doctree)
        else:
            header = None
        rewriter = Rewriter(doctree, text_renderer=self.text_renderer, header=header)
        doctree.walkabout(rewriter)
        super().write_doc(docname, doctree)


class ManifestMixin:

    def __init__(self, app, env):
        super().__init__(app, env)
        self._metadata_base_url = app.config.html_baseurl.rstrip("/")
        self._include_metadata = app.config.markdown_include_metadata
        self._use_title_attribute = app.config.metadata_use_title_attribute

    def get_title(self, doctree):
        meta_title = doctree.attributes.get("title")
        if meta_title and self._use_title_attribute:
            return meta_title
        else:
            title_node = doctree.next_node(docutils.nodes.title)
            return title_node.astext() if title_node else None

    def create_metadata(self, docname, doctree):
        title = self.get_title(doctree)
        url = f"{self._metadata_base_url}/{docname}.html"
        return {
            "metadataAttributes": {
                "title": {
                    "value": {
                        "type": "STRING",
                        "stringValue": title,
                    },
                    "includeForEmbedding": True,
                },
                "x-amz-bedrock-kb-source-uri": {
                    "value": {
                        "type": "STRING",
                        "stringValue": url,
                    },
                    "includeForEmbedding": True,
                },
            }
        }

    def metadata_target(self, docname):
        outdir = pathlib.Path(self.outdir)
        content_file = outdir / f"{docname}{self.out_suffix}"
        metadata_file = outdir / f"{docname}{self.out_suffix}.metadata.json"
        assert content_file.exists()
        return metadata_file

    def write_doc(self, docname: str, doctree: docutils.nodes.Node) -> None:
        # Before the markdown builder modifies the tree, find the document
        # title and create the metadata
        if self._include_metadata:
            metadata = self.create_metadata(docname, doctree)

        # Call the markdown builder to create the content file
        super().write_doc(docname, doctree)

        # Finally, write metadata file
        if self._include_metadata:
            with self.metadata_target(docname).open("w") as outfile:
                json.dump(metadata, outfile, indent=4, sort_keys=True)


class MarkdownBuilder(ManifestMixin, SimpleMarkdownBuilder):
    pass
