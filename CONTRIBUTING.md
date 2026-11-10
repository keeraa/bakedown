# Contributing to BakeDown

Thanks for helping! BakeDown is a single-file Blender add-on (`bakedown.py`), GPL-3.0-or-later.

## Before you start

- Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): architecture, data model and the pitfalls that cost real debugging time.
- For bigger changes open an issue first, so we can agree on the approach.

## Run the tests

Tests run inside real Blender (4.5+) without a window:

```bash
blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py
```

On macOS Blender is `/Applications/Blender.app/Contents/MacOS/Blender`. The same suite runs on GitHub Actions for Blender 4.5 and 5.1.

## Rules of thumb

- Only the **active mesh** may be modified; restore selection and the active object afterwards.
- Anything that can fail must roll back (see `_rollback()` in the bake operator and the Simplify rollback).
- Every UI string goes through `_tr()` and needs ru / es / de / zh translations — `translations_complete` fails otherwise.
- Public API changes (`process`, `simplify`, `bake`, `generate_lods`, `export`, `report`) must keep `AGENTS.md` in sync; bump `API_VERSION` on breaking changes.
- Add a test for every bug you fix.
- Update `CHANGELOG.md`.
