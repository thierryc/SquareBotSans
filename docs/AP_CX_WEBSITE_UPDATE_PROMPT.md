# Prompt: Update ap.cx Square Bot Sans Website

Update the ap.cx Square Bot Sans page to match the current Square Bot Sans source and specimen.

Use the latest release/specimen assets from the SquareBotSans repository after the font binaries have been rebuilt from `sources/SquareBotSans.glyphspackage`.

Key content changes:

- Present the family as `Square Bot Sans`, a squared technical sans derived from Hubot Sans and extended with `wdth`, `wght`, and `ital` axes.
- Update the source inventory to `12 masters`, `49 active instances`, `946 total glyphs`, and `908 exporting glyphs`.
- List active OpenType features: `aalt`, `ccmp`, `locl`, `numr`, `dnom`, `frac`, `ordn`, `pnum`, `tnum`, `zero`, `c2sc`, `smcp`, `case`, `dlig`, `liga`, `ss01`, `ss02`, `ss03`, and `ss04`.
- Update the discretionary ligature showcase to include `<-`, `->`, `=>`, `=<`, `!=`, `>=`, `<=`, `<>`, `<|`, and `|>`.
- Show `!=` as the not-equal symbol design. Show `=>` and `=<` as arrow-form ligatures, matching the existing arrow component style.
- Correct `SS03` everywhere to `Compact r forms`, with a sample such as `rare reactor corridor`.
- Keep `SS04` as the technical `I/J` forms showcase and include the password/code zero alternate with samples such as `O0 I1 l0 O0`.
- Replace any stale `Compact f/t forms` or `fit traffic after sector` references.
- Link to or embed the regenerated specimen PDFs: `specimen-squarebot-sans.pdf` and `specimen-squarebot-sans-letter.pdf`.

Implementation notes:

- Use the rebuilt `fonts/variable/SquareBotSans[ital,wdth,wght].woff2` for live browser specimens.
- Enable discretionary ligatures in feature demos with `font-feature-settings: "dlig" 1;`.
- Provide ON/OFF comparison rows for OpenType features instead of static screenshots where possible.
- Keep the page visual language technical and compact: dense specimen rows, axis controls, glyph/operator examples, and direct download links.
- Before publishing, verify in a browser that the `dlig` examples actually substitute from the deployed WOFF2.
