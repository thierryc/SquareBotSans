# Contributing

Thanks for helping improve SquareBot Sans. Please start with an issue before opening a pull request for design, spacing, kerning, feature, build, or packaging changes.

## Source Workflow

- Make font changes in Glyphs 3 using `sources/SquareBotSans.glyphspackage`.
- Do not edit `.glyphspackage` internals by hand.
- Keep generated exports separate from source changes unless the pull request is explicitly a release update.
- Include before/after proof images for visual changes.
- For kerning and spacing, include affected pairs or strings plus the master/style reviewed.
- For interpolation issues, include axis coordinates and the glyph names involved.

## Validation

Run the light checks that match the change:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf
```

For source-only design work, include the Glyphs version used and any masters inspected. For release work, confirm that all exported fonts parse and that no FontBakery `FAIL` remains unless it is documented in `docs/PUBLICATION_REVIEW.md`.

## Pull Requests

Pull requests should include:

- A short description of the problem and the fix.
- Screenshots or proof PDFs for visual changes.
- The affected glyphs, masters, features, or exported files.
- Validation commands run and their results.

## License Terms

By contributing, you agree that your contribution is licensed under the SIL Open Font License, Version 1.1. Do not contribute material copied from fonts, drawings, or code unless it is compatible with this license and clearly attributed.

Reserved Font Names for this project are `SquareBot Sans` and `SquareBot Sans VF`. The upstream Reserved Font Name `Hubot Sans` must not be used for this project or derivatives.
