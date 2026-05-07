# Issue Guide

Use the GitHub issue forms so reports include the context needed to reproduce font problems.

## Good Font Bug Reports

Include:

- Font file name and version.
- App, browser, or operating system.
- Text sample or glyph names.
- Screenshot or PDF proof.
- Expected result and actual result.

## Kerning And Spacing

Include:

- Pair or string, such as `UA`, `To`, or a short word.
- Style or axis location.
- Screenshot with enough surrounding text to judge rhythm.

## Interpolation And Variable Fonts

Include:

- Axis coordinates, for example `wdth=100, wght=700, ital=1`.
- Glyph names and text sample.
- Whether the issue appears in the static export, variable export, or both.

## Glyph Requests

Include:

- Unicode codepoint and glyph name if known.
- Language or use case.
- Reference text and any shaping expectations.

## Release And Packaging

Include the exact file path from `fonts/`, the install target, and the command or app that failed.
