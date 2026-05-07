# SquareBot Sans

SquareBot Sans is a squared, technical sans serif type family derived from Hubot Sans and extended as a multi-axis Glyphs source. The current source supports width, weight, and italic axes, with static Condensed, Normal, and Expanded families plus a variable font build.

This repository contains the public source package, installable release fonts, webfonts, project documentation, and contribution templates.

## Files

- `sources/SquareBotSans.glyphspackage` is the Glyphs source.
- `fonts/otf/` contains static desktop OTF exports.
- `fonts/webfonts/` contains static WOFF2 webfont exports.
- `fonts/variable/` contains the local/GitHub variable TTF and WOFF2 exports, including the continuous italic-axis build.
- `fonts/googlefonts/` contains the Google Fonts candidate TTF exports, split into Roman and Italic variable fonts.
- `docs/` contains publication notes, coverage notes, and release-readiness review material.
- `documentation/` contains Google Fonts-style family description material.

## Install

For desktop use, install the OTF files from `fonts/otf/`.

For web use, copy the WOFF2 files from `fonts/webfonts/` or `fonts/variable/` into your project and reference them with `@font-face`.

```css
@font-face {
  font-family: "SquareBot Sans";
  src: url("./fonts/webfonts/SquareBotSans-Regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
```

Variable font example:

```css
@font-face {
  font-family: "SquareBot Sans";
  src: url("./fonts/variable/SquareBotSans[ital,wdth,wght].woff2") format("woff2-variations");
  font-weight: 200 900;
  font-stretch: 80% 120%;
  font-style: normal;
  font-display: swap;
}

.sample {
  font-family: "SquareBot Sans", sans-serif;
  font-variation-settings: "ital" 0.35, "wdth" 100, "wght" 500;
}
```

Google Fonts candidate CSS uses separate Roman and Italic files:

```css
@font-face {
  font-family: "SquareBot Sans";
  src: url("./fonts/googlefonts/SquareBotSans[wdth,wght].ttf") format("truetype-variations");
  font-weight: 200 900;
  font-stretch: 80% 120%;
  font-style: normal;
}

@font-face {
  font-family: "SquareBot Sans";
  src: url("./fonts/googlefonts/SquareBotSans-Italic[wdth,wght].ttf") format("truetype-variations");
  font-weight: 200 900;
  font-stretch: 80% 120%;
  font-style: italic;
}
```

## Current Release Fonts

The checked-in static release assets currently include upright OTF and WOFF2 exports:

- `SquareBotSans`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- `SquareBotSansCondensed`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- `SquareBotSansExpanded`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black

The Glyphs source has additional italic instances. Re-export from the source before tagging a full public release.

The local/GitHub variable release keeps continuous interpolation across `ital`, `wdth`, and `wght`. The Google Fonts candidate build follows Google Fonts practice by splitting Roman and Italic variable TTFs and using `ital` only for STAT/style linking.

## Source

Open `sources/SquareBotSans.glyphspackage` in Glyphs 3. Do not edit package files by hand. Make outline, spacing, kerning, feature, and instance changes in Glyphs so generated package data stays consistent.

Current live source inventory:

- Version: 2.000
- UPM: 1000
- Axes: `wdth`, `wght`, `ital`
- Masters: 12
- Instances: 49
- Glyphs: 937 total, 898 exporting
- OpenType features: `aalt`, `ccmp`, `locl`, `numr`, `dnom`, `frac`, `ordn`, `pnum`, `tnum`, `c2sc`, `smcp`, `case`, `dlig`, `liga`, `ss01`, `ss02`, `ss03`, `ss04`

## Validation

Recommended checks before release:

```sh
make build
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
fontbakery check-googlefonts --skip-network fonts/googlefonts/*.ttf
```

Also confirm that the README snippets reference files that exist and that all release fonts parse with fontTools.

## License

SquareBot Sans is licensed under the SIL Open Font License, Version 1.1. See `OFL.txt`.

SquareBot Sans is derived from Hubot Sans. The public SquareBot Sans distribution does not reserve SquareBot Sans as a Reserved Font Name.
