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

6. For a final Google Fonts submission, replace the provisional helper build with a `gftools builder sources/config.yaml` build from Glyphs-derived Roman and Italic production sources.
7. Run FontBakery:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
fontbakery check-googlefonts --skip-network fonts/googlefonts/*.ttf
```

8. Confirm all README examples reference files that exist.
9. Update `CHANGELOG.md`.
10. Tag the release only after accepted FontBakery failures are documented in `docs/PUBLICATION_REVIEW.md`.
