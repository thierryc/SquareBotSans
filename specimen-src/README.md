# SquareBot Sans Specimen Source

This folder contains the editable source for the generated print specimen.

Note: the reusable specimen-generation tool is not published yet. For now, build this specimen with the local scripts in the repository root instead of installing `font-specimen` from a package registry.

## Preview

Run the live preview server from the repository root:

```sh
python3 tools/specimen_dev_server.py
```

Open:

- `http://127.0.0.1:8080/a4`
- `http://127.0.0.1:8080/letter`

The preview uses external CSS and the local variable WOFF2 so browser devtools can inspect and fine-tune the layout. It refreshes when templates, CSS, YAML/JSON data, or specimen Python modules change.

## Edit Points

- `css/base.css`: tokens, page shell, running headers, footers, shared layout.
- `css/pages.css`: page-specific composition and specimen modules.
- `css/formats.css`: A4 and US Letter page dimensions and spacing overrides.
- `templates/base.html`: document shell.
- `templates/page.html`: repeated page shell.
- `templates/pages/*.html`: bespoke page partials.
- `data/*.yaml`: hand-edited editorial and technical data.
- `data/*.json`: generated or mechanical data such as instances and glyph groups.

## Build

Regenerate the self-contained root HTML files:

```sh
python3 tools/build_specimen.py
```

Regenerate HTML, RGB PDFs, and CMYK PDFs:

```sh
tools/build_specimen_print.sh
```

The root HTML files inline CSS and embed `fonts/variable/SquareBotSans[ital,wdth,wght].woff2` as a base64 data URL. Do not make lasting edits directly in the generated root HTML files.
