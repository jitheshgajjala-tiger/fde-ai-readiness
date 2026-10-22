# Project conventions

Apply these to all Python code in this repo.

1. **Naming:** use `snake_case` for functions, variables and columns. Name cleaning functions `clean_<source>` and aggregation functions `build_<output>`. Prefix private helpers with `_`.
2. **Error handling:** validate input at the boundary and raise `ValueError` (bad data) or `FileNotFoundError` (missing file). The message must name the source, for example `"orders is missing required columns: ..."`. Never use a bare `except` or silently swallow errors.
3. **Logging:** use the `logging` module with `logger = logging.getLogger(__name__)`. Never use `print()` in library code. Log row counts at the start and end of each pipeline step.
