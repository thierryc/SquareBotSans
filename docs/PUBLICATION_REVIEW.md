# Square Bot Sans Publication Review

Date: 2026-05-07

## Repository Audit

The starting directory was not a git repository. It contained one current source package, a large `archives/` folder with legacy packages, a flat `export/` folder with OTF/WOFF/WOFF2/TTF builds, stale notes, and `.DS_Store` files.

Public cleanup performed:

- Current source moved to `sources/SquareBotSans.glyphspackage`.
- Static OTF exports moved to `fonts/otf/`.
- Static WOFF2 exports moved to `fonts/webfonts/`.
- Variable TTF/WOFF2 exports moved to `fonts/variable/`.
- Legacy packages, stale docs, legacy WOFF exports, and system files moved to `.private-archive/`, which is ignored by git.
- Public docs and GitHub issue templates added.

## Glyphs MCP Inventory

Glyphs MCP reported one open font before cleanup:

- Family: SquareBot Sans
- Source path: `/Users/thierryc/Documents/fonts/SquareBotSans/sources/SquareBotSans.glyphspackage`
- Release target: 2.004
- Glyphs source version: 2.004 currently reported by Glyphs.
- UPM: 1000
- Masters: 12
- Instances: 49
- Glyphs: 947 total, 909 exporting, 574 encoded
- Axes: Width (`wdth`), Weight (`wght`), Italic (`ital`)
- Features: `aalt`, `ccmp`, `locl`, `numr`, `dnom`, `frac`, `ordn`, `pnum`, `tnum`, `zero`, `c2sc`, `smcp`, `case`, `dlig`, `liga`, `ss01`, `ss02`, `ss03`, `ss04`
- Discretionary ligatures verified in live Glyphs source include `<-`, `->`, `=>`, `=<`, `!=`, `>=`, `<=`, `<>`, `<|`, and `|>`.
- Kerning: about 10,288 to 10,295 pairs per master

Master coverage:

- Condensed ExtraLight, Regular, Black
- Expanded ExtraLight, Regular, Black
- Condensed ExtraLight Italic, Regular Italic, Black Italic
- Expanded ExtraLight Italic, Regular Italic, Black Italic

Note: the live MCP inventory is based on `sources/SquareBotSans.glyphspackage`. Save the source in Glyphs and rebuild release binaries before publishing updated web or PDF specimens.

## License And Name Review

The exported fonts declare SIL Open Font License 1.1 metadata and credit Square Bot Sans as derived from Hubot Sans.

Public license files now preserve:

- Thierry Charbonnel copyright for Square Bot Sans.
- Hubot Sans Project Authors attribution.
- No project Reserved Font Names for the Square Bot Sans public distribution.

Google Fonts posture:

- The repository is prepared for an RFN-free Square Bot Sans submission.
- The local/GitHub distribution may keep a continuous `ital` axis.
- The local/GitHub variable release and Google Fonts candidate both use the family name `Square Bot Sans`.
- The Google Fonts candidate distribution uses split Roman and Italic variable TTFs.

Practical name check:

- No exact `SquareBot Sans` or `Square Bot Sans` match was found in the USPTO-indexed search checked during planning.
- One unrelated stale `SQUAREBOT` appearance was found inside a long educational-material mark, not as a font/typeface mark.
- No exact public typeface match for `Square Bot Sans` was found during planning.
- This is not legal advice. Use legal review before trademark registration or commercial brand enforcement.

## Validation Snapshot

fontTools parse check after cleanup:

```sh
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 <parse check>
```

Result: 102 public binaries parsed successfully, with 0 errors. This covered OTF, WOFF2, TTF, and variable WOFF2 files in `fonts/`.

README release path check after cleanup:

```sh
fonts/webfonts/SquareBotSans-Regular.woff2
fonts/variable/SquareBotSansVF-Regular.woff2
```

Result: both README example paths exist.

## FontBakery Snapshot

Full public OTF plus variable TTF check after 2.004 prep:

```sh
make test-universal
```

Result: 0 errors, 0 fatal, 48 fail, 70 warn, 85 info, 1159 skip, 1870 pass.

Observed blockers in the mixed public tree:

- `check-universal` is currently checking OTFs, local continuous-italic VFs, legacy source VFs, and GF candidate VFs as one family.
- Inconsistent family names across static, local variable, legacy variable, and GF candidate fonts.
- Family name / full font name mismatches in Condensed and Expanded ExtraLight, SemiBold, and ExtraBold OTFs.
- Variable family axis range mismatch between local `ital,wdth,wght` and GF `wdth,wght` files.
- Continuous `ital` axis is intentionally preserved in the local/GitHub VF and fails the universal Google/Chrome-oriented unsupported-axis check.
- Name-table trailing spaces across all checked OTFs and the variable TTF.
- Source variable font issues may remain in `fonts/variable/SquareBotSansVF-Regular.ttf`; use the local/GitHub and Google Fonts distribution VFs for release QA.
- FontBakery single-directory failure because the checked public release separates OTF, variable, and GF directories.
- Static OTFs and regenerated distribution VFs should be checked for version consistency before tagging.

Google Fonts candidate snapshot after GF blocker cleanup:

```sh
.venv/bin/fontbakery check-googlefonts --skip-network build/googlefonts/squarebotsans/*.ttf
```

Result: 0 fatal, 0 error, 0 fail, 19 warn, 13 info, 89 skip, 334 pass.

Local engineering snapshot with the legacy CamelCase policy check excluded:

```sh
make test-googlefonts-local
```

Result: 0 fatal, 0 error, 0 fail, 19 warn, 13 info, 89 skip, 332 pass.

OTS snapshot for the staged Google Fonts package:

```sh
.venv/bin/gftools ots build/googlefonts/squarebotsans
```

Result: both staged GF TTFs sanitized successfully.

Direct table checks confirmed:

- GF and local variable name ID 1 are `Square Bot Sans`.
- GF and local variable name ID 5 and `head.fontRevision` report the release version.
- The local variable font keeps the continuous `ital` axis.
- GF `wdth` axis range is 75/100/125.
- GF Roman and Italic VFs include `HVAR`.
- GF Roman and Italic VFs have no nested composite glyphs after the distribution build flattening pass.
- All 102 exported font files include U+2195 through U+2199.
- README and the Google Fonts article package include the Square Bot Sans poster exported from the 1600x900 Figma frame. The current connector PNG is 1024x576.
- GF STAT exposes `wdth`, `wght`, and Boolean `ital`; width exposes only elidable `Normal`.
- GF fvar instances are weight-only at default width.
- GF name IDs 16/17 are absent.

Resolved during staging:

- Split Roman and Italic candidate variable TTFs.
- RFN-free OFL and generated binary name metadata.
- STAT Boolean italic style-linking.
- Italic post table angle.
- TTX roundtrip failure from unreadable `ij.sc` gvar data.
- Exact duplicate composite components.
- Name ID 25 restricted-character failure.
- Google metadata parse, license, source URL, description URL, full-name/PostScript targeted checks.
- GF CamelCase family-name failure by using `Square Bot Sans` for the GF candidate; the local/GitHub variable release now uses the same public family name.
- Family plus STAT style-name length failures by exposing only elidable `Normal` width in GF STAT.
- Nested component failures by deduplicating and cleaning composites in the distribution build.
- Smart dropout failure by applying `gftools fix-nonhinting`.
- Width-axis registry failure by using 75/100/125 in the GF candidate.
- Missing HVAR by adding HVAR during the distribution build.
- GF directory-name failure by validating in `build/googlefonts/squarebotsans/`.

Remaining candidate blocker:

- None for the staged Google Fonts package in `check-googlefonts`; only WARN-level items remain.

Observed warnings:

- Interpolation warnings.
- Unreachable glyph warnings across checked fonts.
- Legacy long glyph-name warnings across checked fonts.
- Alternate caron decomposed-outline warning in the variable font.

These failures are documented here as preview-release blockers. Resolve them or explicitly accept them in this document before publishing a non-preview release.

## Best Practices Reviewed

Projects reviewed during planning:

- Google Fonts project template: clear source/build/release separation, OFL files, metadata expectations, and CI validation.
- Hubot Sans: upstream license/attribution source and reserved font name handling.
- Recursive: strong documentation, variable-font axis explanation, and contributor expectations.
- Cormorant: public source plus release assets and clear OFL presentation.
- GitHub issue forms documentation: structured issue templates for reproducible reports.

## Release Readiness Checklist

- Reopen `sources/SquareBotSans.glyphspackage` in Glyphs.
- Re-export the complete intended release set from the current source.
- Confirm that the checked-in italic OTF and WOFF2 exports are intended for this public release.
- Run FontBakery on the full release set.
- Confirm all release fonts parse with fontTools.
- Confirm README file references still match actual release filenames.
- Resolve or document all FontBakery `FAIL` results.
