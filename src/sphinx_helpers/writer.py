from collections import defaultdict

import docutils.nodes
from docutils import nodes
from sphinx.builders.text import TextBuilder
from sphinx.util import logging
from sphinx.util.docutils import new_document
from sphinx.writers.text import TextTranslator

logger = logging.getLogger(__name__)


class TextRenderer(TextBuilder):

    def render(self, nodes):
        document = new_document("")
        for node in nodes:
            document += node
        visitor = TextTranslator(document, self)
        document.walkabout(visitor)
        return visitor.body.strip()


class Table:
    def __init__(self):
        self.rows = []
        self.current_row = None
        self.closed = False

    def new_row(self):
        assert self.current_row is None
        self.current_row = []

    def close_row(self):
        assert self.current_row is not None
        self.rows.append(self.current_row)
        self.current_row = None

    def add_entry(self, content):
        self.current_row.append(content)

    def close_table(self):
        assert self.current_row is None
        self.closed = True

    def render(self):
        assert self.closed

        column_info = defaultdict(lambda: {"width": 0})

        for row in self.rows:
            for i, entry in enumerate(row):
                info = column_info[i]
                info["width"] = max(info["width"], len(entry))

        columns = len(column_info)
        assert sorted(column_info.keys()) == list(range(columns))

        row_format_parts = ["|"]
        for i in range(columns):
            width = column_info[i]["width"]
            row_format_parts.append(f" {{:{width}s}} |")
        row_format_string = "".join(row_format_parts)

        table_parts = [
            row_format_string.format(*self.rows[0]),
            "|".join(
                "-" * (column_info[i]["width"] + 2) for i in range(-1, columns + 1)
            )[2:-2],
        ]
        table_parts.extend(row_format_string.format(*row) for row in self.rows[1:])

        return "\n".join(table_parts)


class Rewriter(docutils.nodes.NodeVisitor):

    def __init__(self, *args, text_renderer, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_level = 0
        self._renderer = text_renderer
        self._table = None
        self._desc_level = 0

    def visit_math(self, node):
        node.replace_self(nodes.Text(f"${node.astext()}$"))

    def visit_math_block(self, node):
        content = self._renderer.render([node])
        node.replace_self(nodes.raw("", f"$$\n{content}\n$$", format="text"))

    def visit_section(self, node):
        self._current_level += 1

    def depart_section(self, node):
        self._current_level -= 1

    def visit_title(self, node):
        delim = "#" * self._current_level
        content = node.astext()
        node.replace_self(nodes.raw("", f"{delim} {content}", format="text"))

    def visit_table(self, node):
        self._table = Table()

    def visit_row(self, node):
        self._table.new_row()

    def depart_row(self, node):
        self._table.close_row()

    def depart_entry(self, node):
        # Render on departure so any Rewriter transforms are done first
        content = self._renderer.render(node.children)
        content = content.strip().replace("\n", " ")
        self._table.add_entry(content)

    def depart_table(self, node):
        self._table.close_table()
        node.replace_self(nodes.raw("", self._table.render(), format="text"))

    def unknown_visit(self, node):
        pass

    def unknown_departure(self, node):
        pass
