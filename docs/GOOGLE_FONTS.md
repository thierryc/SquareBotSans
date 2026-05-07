# Google Fonts Candidate Notes

SquareBot Sans has two distribution tracks:

- GitHub/local: a full variable font with continuous `ital`, `wdth`, and `wght` axes.
- Google Fonts candidate: paired Roman and Italic variable TTFs with `wdth` and `wght` axes.

Google Fonts currently expects italic variable families as separate Roman and Italic VFs. The `ital` axis is represented for STAT/style linking as `0` for Roman and `1` for Italic, not as a continuous served axis in one file.

## Files

Local/GitHub release artifacts:

- `fonts/variable/SquareBotSans[ital,wdth,wght].ttf`
- `fonts/variable/SquareBotSans[ital,wdth,wght].woff2`

Google Fonts candidate artifacts:

- `fonts/googlefonts/SquareBotSans[wdth,wght].ttf`
- `fonts/googlefonts/SquareBotSans-Italic[wdth,wght].ttf`

## Build

Build the current distribution artifacts:

```sh
make build
```

The current helper uses the checked-in Glyphs export at `fonts/variable/SquareBotSansVF-Regular.ttf` as its source export and creates the two distribution tracks. Before opening a Google Fonts PR, replace this provisional helper path with a `gftools builder sources/config.yaml` production build from Glyphs-derived Roman and Italic sources.

Install the recommended Google Fonts toolchain in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## QA

Run Google Fonts checks on the candidate files:

```sh
fontbakery check-googlefonts --skip-network fonts/googlefonts/*.ttf
```

Run broader checks on all public release fonts:

```sh
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
```

Known preview blockers from the current export must be resolved before submission: malformed GDEF variation data, duplicate transformed components, previous OTS failure, old name-table RFN text, STAT completeness, width-axis defaults/ranges, and interpolation warnings.

Current generated candidate status:

- The candidate has split Roman/Italic VFs, RFN-free OFL text, `METADATA.pb`, description HTML, and no TTX roundtrip failure.
- The generator currently sanitizes preview-export defects by removing the broken GDEF VarStore, dropping one unreadable `ij.sc` gvar entry, and removing exact duplicate composite components.
- Remaining Google Fonts blockers include family-name camelcase policy, long family+STAT names, nested components, smart dropout/gasp policy, width-axis registry coordinates, missing HVAR, and source-level outline/interpolation warnings.
- The `fonts/googlefonts/` directory is a repo-local staging location; final PR validation should run from `ofl/squarebotsans/` in a fork of `google/fonts`.

## Submission

1. Keep `https://github.com/thierryc/SquareBotSans` public and tagged.
2. Open a Google Fonts issue before preparing a `google/fonts` PR.
3. In the PR, add only the GF artifacts and required metadata under `ofl/squarebotsans`.
4. Use the PR line: `Taken from the upstream repo https://github.com/thierryc/SquareBotSans at commit <commit-url>`.

References:

- https://googlefonts.github.io/gf-guide/variable.html
- https://googlefonts.github.io/gf-guide/build.html
- https://googlefonts.github.io/gf-guide/upstream.html
- https://github.com/google/fonts/tree/main/ofl/texturina
- https://github.com/google/fonts/tree/main/ofl/robotoserif
