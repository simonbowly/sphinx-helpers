"""Test the build process with Text builder with the test root."""

import json
import pathlib
import shutil
import textwrap

import pytest

here = pathlib.Path(__file__).parent.resolve()
reference_dir = here / "reference"


def assert_exists(fp):
    assert fp.exists(), f"Missing expected file {fp.parts[-1]}"


def assert_not_exists(fp):
    assert not fp.exists(), f"Found unexpected file {fp.parts[-1]}"


@pytest.mark.sphinx(buildername="markdown", testroot=here / "markdown-only")
def test_markdown_only(app, status, warning):
    output_dir = pathlib.Path(app.outdir)
    assert output_dir.parts[-2] == "_build"
    assert output_dir.parts[-1] == "markdown"

    shutil.rmtree(output_dir.parent, ignore_errors=True)
    app.build()

    assert_exists(output_dir.joinpath("doc1.md"))
    assert_not_exists(output_dir.joinpath("doc1.md.metadata.json"))
    assert_not_exists(output_dir.joinpath("doc1.html"))
    assert_not_exists(output_dir.joinpath("doc1.txt"))

    for file_path in ["doc1.md", "code.md"]:
        content = output_dir.joinpath(file_path).read_text()
        expected_content = reference_dir.joinpath(file_path).read_text()
        assert content == expected_content


@pytest.mark.sphinx(buildername="markdown", testroot=here / "markdown-with-metadata")
def test_markdown_with_metadata(app, status, warning):
    output_dir = pathlib.Path(app.outdir)
    assert output_dir.parts[-2] == "_build"
    assert output_dir.parts[-1] == "markdown"

    shutil.rmtree(output_dir.parent, ignore_errors=True)
    app.build()

    assert_exists(output_dir.joinpath("doc1.md"))
    assert_exists(output_dir.joinpath("doc1.md.metadata.json"))
    assert_not_exists(output_dir.joinpath("doc1.html"))
    assert_not_exists(output_dir.joinpath("doc1.txt"))

    for file_path in ["doc1.md"]:
        content = output_dir.joinpath(file_path).read_text()
        expected_content = reference_dir.joinpath(file_path).read_text()
        assert content == expected_content

    for file_path in ["doc1.md.metadata.json"]:
        content = json.loads(output_dir.joinpath(file_path).read_text())
        expected_content = json.loads(reference_dir.joinpath(file_path).read_text())
        assert content == expected_content


@pytest.mark.sphinx(buildername="markdown", testroot=here / "markdown-with-header")
def test_markdown_with_header(app, status, warning):
    output_dir = pathlib.Path(app.outdir)
    assert output_dir.parts[-2] == "_build"
    assert output_dir.parts[-1] == "markdown"

    shutil.rmtree(output_dir.parent, ignore_errors=True)
    app.build()

    assert_exists(output_dir.joinpath("doc1.md"))
    assert_not_exists(output_dir.joinpath("doc1.md.metadata.json"))
    assert_not_exists(output_dir.joinpath("doc1.html"))
    assert_not_exists(output_dir.joinpath("doc1.txt"))

    file_path = "doc1.md"
    content = output_dir.joinpath(file_path).read_text()
    expected_body = reference_dir.joinpath(file_path).read_text()
    expected_header = textwrap.dedent(
        """
        ---
        title: Section A
        url: /path/to/site_root/doc1.md
        ---

        """
    ).lstrip()
    expected_content = expected_header + expected_body
    assert content == expected_content
