"""Test the build process with Text builder with the test root."""

import pathlib
import shutil

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
    assert_not_exists(output_dir.joinpath("doc1.md.manifest.json"))
    assert_not_exists(output_dir.joinpath("doc1.html"))
    assert_not_exists(output_dir.joinpath("doc1.txt"))

    for file_path in ["doc1.md"]:

        content = output_dir.joinpath(file_path).read_text()
        expected_content = reference_dir.joinpath(file_path).read_text()

        assert content == expected_content


@pytest.mark.sphinx(buildername="markdown", testroot=here / "markdown-with-manifest")
def test_markdown_with_manifest(app, status, warning):
    output_dir = pathlib.Path(app.outdir)
    assert output_dir.parts[-2] == "_build"
    assert output_dir.parts[-1] == "markdown"

    shutil.rmtree(output_dir.parent, ignore_errors=True)
    app.build()

    assert_exists(output_dir.joinpath("doc1.md"))
    assert_exists(output_dir.joinpath("doc1.md.manifest.json"))
    assert_not_exists(output_dir.joinpath("doc1.html"))
    assert_not_exists(output_dir.joinpath("doc1.txt"))

    for file_path in ["doc1.md", "doc1.md.manifest.json"]:

        content = output_dir.joinpath(file_path).read_text()
        expected_content = reference_dir.joinpath(file_path).read_text()

        assert content == expected_content
