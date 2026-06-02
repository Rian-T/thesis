.PHONY: build clean checkbib checkbib-all checkbib-strict

build:
	latexmk

clean:
	latexmk -c

# Non-blocking bibliography hallucination check (cited entries only).
# Resolves each cited bib entry against Crossref / arXiv / OpenAlex / DBLP.
checkbib:
	uv run tools/verify_bib.py

# Same, but over every entry in thesis.bib.
checkbib-all:
	uv run tools/verify_bib.py --all

# Pre-submission gate: non-zero exit if any MISMATCH / NOT_FOUND remains.
checkbib-strict:
	uv run tools/verify_bib.py --strict
