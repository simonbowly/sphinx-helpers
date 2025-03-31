.PHONY: wheel

wheel:
	python -m build

develop:
	python -m pip install sphinx[test]==7.2.6 -e .
	python -m pip install build

test:
	python -m pytest
