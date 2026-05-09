# Release Notes

Use this checklist before publishing a tagged GitHub release.

1. Open `sources/SquareBotSans.glyphspackage` in Glyphs.
2. Confirm version, copyright, license, instances, and exports.
3. Export static OTFs to `fonts/otf/`.
4. Export static WOFF2 files to `fonts/webfonts/`.
5. Export the source variable font to `fonts/variable/SquareBotSansVF-Regular.ttf` and `fonts/variable/SquareBotSansVF-Regular.woff2`.
6. Build the local/GitHub continuous-axis VF and the split Google Fonts candidate VFs:

```sh
make build
```

This writes:

- `fonts/variable/SquareBotSans[ital,wdth,wght].ttf`
- `fonts/variable/SquareBotSans[ital,wdth,wght].woff2`
- `fonts/googlefonts/SquareBotSans[wdth,wght].ttf`
- `fonts/googlefonts/SquareBotSans-Italic[wdth,wght].ttf`
- `build/googlefonts/squarebotsans/` for Google Fonts QA staging

7. The Google Fonts helper build derives the GF candidate from `fonts/variable/SquareBotSansVF-Regular.ttf`, then applies the GF-specific Roman/Italic split, STAT cleanup, nonhinting fix, and staging copy.
8. Install the local variable TTF for macOS user-level proofing, then regenerate HTML, PDF, and CMYK specimen documents:

```sh
cp fonts/variable/SquareBotSans[ital,wdth,wght].ttf ~/Library/Fonts/
atsutil databases -removeUser
tools/build_specimen_print.sh
```

9. Run FontBakery:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
make test-googlefonts
make test-googlefonts-local
```

`make test-googlefonts` is the official GF profile. Both the local/GitHub variable release and the Google Fonts candidate use the family name `Square Bot Sans`. `make test-googlefonts-local` is kept as a diagnostic fallback.

10. Confirm all README examples and poster image references point to files that exist.
11. Update `CHANGELOG.md`.
12. Tag the release only after accepted FontBakery failures are documented in `docs/PUBLICATION_REVIEW.md`.
