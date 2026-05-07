# SquareBot Sans Publication Review

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
- Source path: `/Users/thierryc/Documents/fonts/SquareBotSans/SquareBotSans-003.glyphspackage`
- Version: 2.000
- UPM: 1000
- Masters: 12
- Instances: 49
- Glyphs: 937 total, 898 exporting, 569 encoded
- Axes: Width (`wdth`), Weight (`wght`), Italic (`ital`)
- Features: `aalt`, `ccmp`, `locl`, `numr`, `dnom`, `frac`, `ordn`, `pnum`, `tnum`, `c2sc`, `smcp`, `case`, `dlig`, `liga`, `ss01`, `ss02`, `ss03`, `ss04`
- Kerning: about 10,288 to 10,295 pairs per master

Master coverage:

- Condensed ExtraLight, Regular, Black
- Expanded ExtraLight, Regular, Black
- Condensed ExtraLight Italic, Regular Italic, Black Italic
- Expanded ExtraLight Italic, Regular Italic, Black Italic

Note: the source package was moved after the live MCP inventory. Reopen `sources/SquareBotSans.glyphspackage` in Glyphs before saving or exporting a final release.

## License And Name Review

The exported fonts declare SIL Open Font License 1.1 metadata and credit SquareBot Sans as derived from Hubot Sans.

Public license files now preserve:

- Thierry Charbonnel copyright for SquareBot Sans.
- Hubot Sans Project Authors attribution.
- No project Reserved Font Names for the SquareBot Sans public distribution.

Google Fonts posture:

- The repository is prepared for an RFN-free SquareBot Sans submission.
- The local/GitHub distribution may keep a continuous `ital` axis.
- The Google Fonts candidate distribution must use split Roman and Italic variable TTFs.

Practical name check:

- No exact `SquareBot Sans` or `Square Bot Sans` match was found in the USPTO-indexed search checked during planning.
- One unrelated stale `SQUAREBOT` appearance was found inside a long educational-material mark, not as a font/typeface mark.
- No exact public typeface match for `SquareBot Sans` was found during planning.
- This is not legal advice. Use legal review before trademark registration or commercial brand enforcement.

## Validation Snapshot

fontTools parse check after cleanup:

```sh
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 <parse check>
```

Result: 50 public binaries parsed successfully, with 0 errors. This covered OTF, WOFF2, TTF, and variable WOFF2 files in `fonts/`.

README release path check after cleanup:

```sh
fonts/webfonts/SquareBotSans-Regular.woff2
fonts/variable/SquareBotSansVF-Regular.woff2
```

Result: both README example paths exist.

## FontBakery Snapshot

Full public OTF plus variable TTF check after cleanup:

```sh
fontbakery check-universal --skip-network --succinct --no-progress --loglevel WARN --loglevel-messages WARN fonts/otf/*.otf fonts/variable/*.ttf
```

Result: 0 errors, 0 fatal, 37 fail, 52 warn, 51 info, 1000 skip, 1195 pass.

Observed blockers:

- Inconsistent family names across representative static and variable fonts.
- Family name / full font name mismatches in Condensed and Expanded ExtraLight, SemiBold, and ExtraBold OTFs.
- Variable family axis range mismatch.
- Missing STAT axis value tables in the variable font.
- Name-table trailing spaces across all checked OTFs and the variable TTF.
- Variable font OTS failure.
- Duplicate transformed components in the variable font.
- FontBakery single-directory failure because the checked public release separates OTF and variable directories.
- Google Fonts production build still needs `gftools builder` output from Glyphs-derived Roman and Italic sources rather than a font-editor binary export.

Google Fonts candidate snapshot after two-track implementation:

```sh
.venv/bin/fontbakery check-googlefonts --skip-network --succinct --no-progress --loglevel WARN --loglevel-messages WARN fonts/googlefonts/*.ttf
```

Result: 0 fatal, 0 error, 16 fail, 21 warn, 17 info, 85 skip, 316 pass.

Resolved during staging:

- Split Roman and Italic candidate variable TTFs.
- RFN-free OFL and generated binary name metadata.
- STAT Boolean italic style-linking.
- Italic post table angle.
- TTX roundtrip failure from unreadable `ij.sc` gvar data.
- Exact duplicate composite components.
- Name ID 25 restricted-character failure.
- Google metadata parse, license, source URL, description URL, full-name/PostScript targeted checks.

Remaining candidate blockers:

- Google family name compliance flags `SquareBot` camelcase.
- Family plus STAT style names exceed Google length limits.
- Nested components remain in generated binaries.
- Smart dropout still fails even with a generated `gasp` table.
- Width-axis coordinates are 80/100/120; Google axis registry check rejects them.
- Generated VFs lack HVAR.
- The repo-local `fonts/googlefonts/` path is not the final `ofl/squarebotsans/` PR directory.

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
- Confirm whether italic exports should be included in this public release.
- Run FontBakery on the full release set.
- Confirm all release fonts parse with fontTools.
- Confirm README file references still match actual release filenames.
- Resolve or document all FontBakery `FAIL` results.
