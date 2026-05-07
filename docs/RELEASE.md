# Release Notes

Use this checklist before publishing a tagged GitHub release.

1. Open `sources/SquareBotSans.glyphspackage` in Glyphs.
2. Confirm version, copyright, license, instances, and exports.
3. Export static OTFs to `fonts/otf/`.
4. Export static WOFF2 files to `fonts/webfonts/`.
5. Build the local/GitHub continuous-axis VF and the split Google Fonts candidate VFs:

```sh
make build
```

This writes:

- `fonts/variable/SquareBotSans[ital,wdth,wght].ttf`
- `fonts/variable/SquareBotSans[ital,wdth,wght].woff2`
- `fonts/googlefonts/SquareBotSans[wdth,wght].ttf`
- `fonts/googlefonts/SquareBotSans-Italic[wdth,wght].ttf`
- `build/googlefonts/squarebotsans/` for Google Fonts QA staging

6. The Google Fonts helper build derives the GF candidate from `sources/SquareBotSans.glyphspackage` with `fontmake`, then applies the GF-specific Roman/Italic split, STAT cleanup, nonhinting fix, and staging copy.
7. Run FontBakery:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
make test-googlefonts
make test-googlefonts-local
```

`make test-googlefonts` is the official GF profile. The Google Fonts candidate uses the GF-compliant family name `Square Bot Sans`; the local/GitHub release remains `SquareBot Sans`. `make test-googlefonts-local` is kept as a diagnostic fallback.

8. Confirm all README examples reference files that exist.
9. Update `CHANGELOG.md`.
10. Tag the release only after accepted FontBakery failures are documented in `docs/PUBLICATION_REVIEW.md`.
