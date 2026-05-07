# Release Notes

Use this checklist before publishing a tagged GitHub release.

1. Open `sources/SquareBotSans.glyphspackage` in Glyphs.
2. Confirm version, copyright, license, instances, and exports.
3. Export static OTFs to `fonts/otf/`.
4. Export static WOFF2 files to `fonts/webfonts/`.
5. Export variable TTF and WOFF2 files to `fonts/variable/`.
6. Run FontBakery:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf
```

7. Confirm all README examples reference files that exist.
8. Update `CHANGELOG.md`.
9. Tag the release only after accepted FontBakery failures are documented in `docs/PUBLICATION_REVIEW.md`.
