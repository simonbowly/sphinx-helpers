import json
import pathlib

import docutils.nodes
from sphinx.builders.text import TextBuilder

from .writer import Rewriter, TextRenderer


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

    def __init__(self, app, env):
        super().__init__(app, env)
        self.text_renderer = TextRenderer(app, env)

    def init(self):
        super().init()
        self.text_renderer.init()

    def prepare_writing(self, docnames):
        super().prepare_writing(docnames)
        self.text_renderer.prepare_writing(docnames)

    def write_doc(self, docname, doctree):
        rewriter = Rewriter(doctree, text_renderer=self.text_renderer)
        doctree.walkabout(rewriter)
        super().write_doc(docname, doctree)


class ManifestMixin:

    def __init__(self, app, env):
        super().__init__(app, env)
        self._manifest_base_url = app.config.html_baseurl.rstrip("/")
        self._include_manifest = app.config.markdown_include_manifest

    def create_manifest(self, docname, doctree):
        title_node = doctree.next_node(docutils.nodes.title)
        title = title_node.astext() if title_node else None
        url = f"{self._manifest_base_url}/{docname}.html"
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

    def manifest_target(self, docname):
        outdir = pathlib.Path(self.outdir)
        content_file = outdir / f"{docname}{self.out_suffix}"
        manifest_file = outdir / f"{docname}{self.out_suffix}.manifest.json"
        assert content_file.exists()
        return manifest_file

    def write_doc(self, docname: str, doctree: docutils.nodes.Node) -> None:
        # Before the markdown builder modifies the tree, find the document
        # title and create the manifest
        if self._include_manifest:
            manifest = self.create_manifest(docname, doctree)

        # Call the markdown builder to create the content file
        super().write_doc(docname, doctree)

        # Finally, write manifest file
        if self._include_manifest:
            with self.manifest_target(docname).open("w") as outfile:
                json.dump(manifest, outfile, indent=4, sort_keys=True)


class MarkdownBuilder(ManifestMixin, SimpleMarkdownBuilder):
    pass
