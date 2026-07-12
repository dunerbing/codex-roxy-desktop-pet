# Roxy-Inspired Codex Desktop Pet

An animated, fan-made desktop pet for the Codex Windows app. It includes
coordinated jumping, hair and skirt motion, glowing hearts, a pulsing staff gem,
and shy/happy expressions.

![Animation preview](docs/animation-preview.gif)

## Quick install on Windows

1. Download the latest release ZIP and extract it.
2. Double-click `install.cmd`.
3. Fully quit and reopen Codex.
4. Open **Settings > Pets** and choose **Roxy Inspired Mage**.

The installer copies the pet to:

```text
%USERPROFILE%\.codex\pets\roxy-inspired-mage
```

It backs up an existing installation before replacing it.

## Uninstall

Double-click `uninstall.cmd`, then restart Codex. The uninstaller only removes
the `roxy-inspired-mage` directory under your Codex pets folder.

## Build the spritesheet

The prebuilt spritesheet is included, so Python is not needed for installation.
To regenerate it, install Pillow and run:

```powershell
python -m pip install Pillow
python tools/Build-RoxyAnimatedPet.py `
  --source assets/roxy-inspired-cutout.png `
  --sheet pet/spritesheet.png `
  --preview docs/animation-preview.jpg `
  --gif docs/animation-preview.gif
```

Codex sprite version 2 uses a `1536 x 2288` sheet containing an `8 x 11` grid
of `192 x 208` frames. Animation frame counts are constrained by the Codex
desktop pet player.

## Project layout

```text
assets/   Source cutout used by the animation builder
docs/     Animated preview
pet/      Files installed into the Codex pets directory
tools/    Deterministic Pillow-based animation builder
```

## License and attribution

The source code is licensed under the MIT License. The character-inspired
artwork is unofficial fan art and is not covered by the MIT License. See
[`ASSET_NOTICE.md`](ASSET_NOTICE.md) before redistributing or using it.

This project is not affiliated with or endorsed by OpenAI, Codex, the creators
of *Mushoku Tensei*, or their rights holders.

