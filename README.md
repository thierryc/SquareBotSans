# SquareBot Sans

SquareBot Sans is a squared, technical sans serif type family derived from Hubot Sans and extended as a multi-axis Glyphs source. The current source supports width, weight, and italic axes, with static Condensed, Normal, and Expanded families plus a variable font build.

This repository contains the public source package, installable release fonts, webfonts, project documentation, and contribution templates.

## Files

- `sources/SquareBotSans.glyphspackage` is the Glyphs source.
- `fonts/otf/` contains static desktop OTF exports.
- `fonts/webfonts/` contains static WOFF2 webfont exports.
- `fonts/variable/` contains the variable TTF and WOFF2 exports.
- `docs/` contains publication notes, coverage notes, and release-readiness review material.

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
  font-family: "SquareBot Sans VF";
  src: url("./fonts/variable/SquareBotSansVF-Regular.woff2") format("woff2-variations");
  font-weight: 200 900;
  font-stretch: 75% 125%;
  font-style: oblique 0deg 12deg;
  font-display: swap;
}

.sample {
  font-family: "SquareBot Sans VF", sans-serif;
  font-variation-settings: "wdth" 100, "wght" 500, "ital" 0;
}
```

## Current Release Fonts

The checked-in static release assets currently include upright OTF and WOFF2 exports:

- `SquareBotSans`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- `SquareBotSansCondensed`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- `SquareBotSansExpanded`: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black

The Glyphs source has additional italic instances. Re-export from the source before tagging a full public release.

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
fontbakery check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf
```

Also confirm that the README snippets reference files that exist and that all release fonts parse with fontTools.

## License

SquareBot Sans is licensed under the SIL Open Font License, Version 1.1. See `OFL.txt`.

Reserved Font Names for this project are `SquareBot Sans` and `SquareBot Sans VF`.

SquareBot Sans is derived from Hubot Sans. The Hubot Sans Reserved Font Name remains `Hubot Sans`; derivatives of this project must not use that name.
