from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


FRAME_W = 192
FRAME_H = 208
SHEET_COLS = 8
SHEET_ROWS = 11


def ease_in_out(value: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * value)


def fit_source(source: Image.Image) -> Image.Image:
    alpha = source.getchannel("A")
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError("Source image has no visible pixels")
    source = source.crop(bounds)
    scale = min(174 / source.width, 196 / source.height)
    size = (round(source.width * scale), round(source.height * scale))
    return source.resize(size, Image.Resampling.LANCZOS)


def feathered_polygon(size: tuple[int, int], points: list[tuple[int, int]], blur: int = 4) -> Image.Image:
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur))


def shift_region(image: Image.Image, mask: Image.Image, dx: float, dy: float, angle: float = 0) -> Image.Image:
    layer = Image.new("RGBA", image.size)
    layer.paste(image, mask=mask)
    if angle:
        layer = layer.rotate(angle, Image.Resampling.BICUBIC, center=(FRAME_W // 2, FRAME_H // 2))
    moved = Image.new("RGBA", image.size)
    moved.alpha_composite(layer, (round(dx), round(dy)))
    cleared = image.copy()
    cleared.paste((0, 0, 0, 0), mask=mask)
    cleared.alpha_composite(moved)
    return cleared


def draw_heart(layer: Image.Image, x: float, y: float, size: float, alpha: int, glow: bool = True) -> None:
    if size <= 0:
        return
    points = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        px = 16 * math.sin(t) ** 3
        py = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        points.append((x + px * size / 32, y - py * size / 32))
    if glow:
        halo = Image.new("RGBA", layer.size)
        ImageDraw.Draw(halo).polygon(points, fill=(255, 80, 190, min(150, alpha)))
        halo = halo.filter(ImageFilter.GaussianBlur(max(2, round(size * 0.45))))
        layer.alpha_composite(halo)
    ImageDraw.Draw(layer).polygon(points, fill=(255, 95, 170, alpha), outline=(255, 210, 240, alpha))


def draw_star(layer: Image.Image, x: float, y: float, radius: float, color: tuple[int, int, int], alpha: int) -> None:
    halo = Image.new("RGBA", layer.size)
    draw = ImageDraw.Draw(halo)
    draw.ellipse((x - radius * 2, y - radius * 2, x + radius * 2, y + radius * 2), fill=(*color, alpha // 2))
    halo = halo.filter(ImageFilter.GaussianBlur(max(2, round(radius))))
    layer.alpha_composite(halo)
    draw = ImageDraw.Draw(layer)
    draw.polygon([(x, y-radius), (x+radius*0.28, y-radius*0.28), (x+radius, y),
                  (x+radius*0.28, y+radius*0.28), (x, y+radius),
                  (x-radius*0.28, y+radius*0.28), (x-radius, y),
                  (x-radius*0.28, y-radius*0.28)], fill=(*color, alpha))


def draw_gem_glow(layer: Image.Image, pulse: float) -> None:
    # The fitted source places the floating blue gem near the upper-right staff head.
    x, y = 157, 58
    halo = Image.new("RGBA", layer.size)
    draw = ImageDraw.Draw(halo)
    radii = (10 + 7 * pulse, 6 + 4 * pulse, 3 + 2 * pulse)
    colors = ((40, 155, 255, 40), (80, 205, 255, 90), (220, 250, 255, 220))
    for radius, color in zip(radii, colors):
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    halo = halo.filter(ImageFilter.GaussianBlur(3 + round(2 * pulse)))
    layer.alpha_composite(halo)
    draw = ImageDraw.Draw(layer)
    draw.polygon([(x, y-5), (x+3, y), (x, y+6), (x-3, y)], fill=(105, 220, 255, 230))
    draw.line((x, y-4, x, y+3), fill=(240, 255, 255, 245), width=1)


def add_expression(layer: Image.Image, mood: float, blink: float = 0) -> None:
    draw = ImageDraw.Draw(layer)
    if mood > 0.15:
        blush_alpha = round(115 * mood)
        for cx in (79, 111):
            draw.ellipse((cx-7, 83, cx+7, 89), fill=(255, 120, 155, blush_alpha))
            for offset in (-4, 0, 4):
                draw.line((cx+offset-2, 84, cx+offset+1, 87), fill=(255, 205, 215, blush_alpha), width=1)
    if blink > 0.5:
        # Short happy-eye arcs make the peak pose read as a delighted blink at pet scale.
        draw.arc((72, 67, 88, 80), 200, 340, fill=(40, 35, 50, 235), width=2)
        draw.arc((102, 67, 118, 80), 200, 340, fill=(40, 35, 50, 235), width=2)
    if mood > 0.7:
        draw.arc((91, 86, 101, 94), 10, 170, fill=(150, 60, 90, 230), width=2)


def add_ground_effects(layer: Image.Image, strength: float) -> None:
    if strength <= 0:
        return
    draw = ImageDraw.Draw(layer)
    for x, direction in ((61, -1), (129, 1)):
        for i in range(3):
            radius = 2 + i
            cx = x + direction * i * 5
            cy = 198 - i * 2
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(218, 231, 250, round(150 * strength)))


def render_frame(base: Image.Image, *, body_y: float = 0, body_x: float = 0,
                 squash: float = 0, tilt: float = 0, braid_sway: float = 0,
                 skirt_lift: float = 0, hand_wave: float = 0, mood: float = 0,
                 blink: float = 0, gem: float = 0.25, hearts: float = 0,
                 heart_phase: float = 0, dust: float = 0) -> Image.Image:
    canvas = Image.new("RGBA", (FRAME_W, FRAME_H))
    sprite = base.copy()
    if squash:
        factor = 1 - squash
        resized = sprite.resize((sprite.width, max(1, round(sprite.height * factor))), Image.Resampling.LANCZOS)
        sprite = Image.new("RGBA", base.size)
        sprite.alpha_composite(resized, (0, base.height - resized.height))
    if tilt:
        sprite = sprite.rotate(tilt, Image.Resampling.BICUBIC, center=(96, 150))

    left_braid = feathered_polygon(sprite.size, [(15, 67), (63, 72), (71, 169), (20, 172)])
    right_braid = feathered_polygon(sprite.size, [(119, 64), (176, 61), (181, 174), (127, 171)])
    skirt = feathered_polygon(sprite.size, [(48, 124), (137, 120), (145, 164), (43, 164)], 3)
    free_hand = feathered_polygon(sprite.size, [(39, 103), (73, 99), (72, 134), (35, 138)], 3)

    sprite = shift_region(sprite, left_braid, -braid_sway * 0.75, abs(braid_sway) * 0.12, -braid_sway * 0.15)
    sprite = shift_region(sprite, right_braid, braid_sway, abs(braid_sway) * 0.1, braid_sway * 0.12)
    sprite = shift_region(sprite, skirt, -braid_sway * 0.12, -skirt_lift, braid_sway * 0.04)
    sprite = shift_region(sprite, free_hand, -abs(hand_wave) * 0.15, -hand_wave * 0.35, -hand_wave * 0.7)

    canvas.alpha_composite(sprite, (round(body_x), round(body_y)))
    effects = Image.new("RGBA", canvas.size)
    add_expression(effects, mood, blink)
    draw_gem_glow(effects, gem)
    add_ground_effects(effects, dust)

    if hearts > 0:
        heart_specs = [(-2, 0, 8), (8, 0.45, 6), (-11, 0.72, 5), (15, 0.9, 4)]
        for index, (dx, delay, size) in enumerate(heart_specs):
            local = (heart_phase - delay) % 1.35
            visibility = max(0, 1 - local / 1.1) * hearts
            if visibility > 0.03:
                wobble = math.sin((local * 7 + index) * math.pi) * 3
                draw_heart(effects, 148 + dx + wobble, 83 - local * 33,
                           size * (0.7 + 0.45 * visibility), round(235 * visibility))

    canvas.alpha_composite(effects, (round(body_x), round(body_y)))
    return canvas


def frame_sequence(base: Image.Image, row: int, count: int) -> list[Image.Image]:
    frames = []
    for i in range(count):
        t = i / count
        wave = math.sin(2 * math.pi * t)
        if row == 0:  # idle: breathing, delayed hair/skirt response and a soft blink
            breath = ease_in_out((1 - math.cos(2 * math.pi * t)) / 2)
            frames.append(render_frame(base, body_y=-1.3 * breath, squash=-0.008 * breath,
                                       braid_sway=1.4 * wave, skirt_lift=0.7 * breath,
                                       blink=1 if i == count - 1 else 0, gem=0.3 + 0.18 * breath))
        elif row in (1, 2, 7):  # running: opposite body/hair phases and alternating footfall puffs
            direction = 1 if row != 2 else -1
            bounce = abs(math.sin(2 * math.pi * t))
            frames.append(render_frame(base, body_x=direction * 2.2 * wave, body_y=-3.6 * bounce,
                                       squash=0.025 * (1 - bounce), tilt=-direction * 2.3,
                                       braid_sway=-direction * (4.5 * wave + 1.5),
                                       skirt_lift=2.5 * bounce, gem=0.42 + 0.25 * bounce,
                                       dust=max(0, 1 - bounce * 1.8)))
        elif row == 3:  # wave: bashful lean, raised free hand and luminous heart cluster
            lift = math.sin(math.pi * min(1, t * 1.35))
            frames.append(render_frame(base, body_y=-2.5 * lift, body_x=1.2 * lift,
                                       tilt=1.5 * lift, braid_sway=2.5 * wave,
                                       skirt_lift=1.2 * lift, hand_wave=7 + 4 * wave,
                                       mood=0.75 + 0.25 * lift, blink=1 if i == 2 else 0,
                                       gem=0.65 + 0.35 * lift, hearts=1,
                                       heart_phase=(t * 1.4) % 1.35))
        elif row == 4:  # jump: anticipation, launch, apex, fall and cushioned landing
            poses = [
                dict(body_y=2, squash=0.055, braid_sway=1, skirt_lift=0, hand_wave=1, dust=0.25),
                dict(body_y=-8, squash=-0.025, braid_sway=-3, skirt_lift=3, hand_wave=6, dust=1),
                dict(body_y=-18, squash=-0.035, braid_sway=-6, skirt_lift=6, hand_wave=10),
                dict(body_y=-11, squash=-0.015, braid_sway=-2, skirt_lift=4, hand_wave=7),
                dict(body_y=1, squash=0.045, braid_sway=4, skirt_lift=1, hand_wave=2, dust=0.8),
            ]
            pose = poses[i]
            frames.append(render_frame(base, **pose, mood=0.9, blink=1 if i == 2 else 0,
                                       gem=0.8 + (0.2 if i == 2 else 0), hearts=0.9,
                                       heart_phase=(0.18 + i * 0.22) % 1.35))
        elif row == 5:  # failed: settle into a small disappointed droop
            droop = ease_in_out(min(1, t * 1.7))
            frames.append(render_frame(base, body_y=3 * droop, tilt=-2.2 * droop,
                                       braid_sway=1.5 * wave, skirt_lift=0.4,
                                       gem=0.12 + 0.08 * (1 - droop)))
        elif row == 6:  # waiting: gentle side-to-side fidget
            frames.append(render_frame(base, body_x=1.8 * wave, body_y=-abs(wave),
                                       tilt=1.2 * wave, braid_sway=-2.4 * wave,
                                       skirt_lift=0.8 * abs(wave), hand_wave=1.8 * wave,
                                       mood=0.25, gem=0.28 + 0.16 * abs(wave)))
        elif row == 8:  # review/success: happy bounce with a heart-and-magic flourish
            bounce = abs(math.sin(2 * math.pi * t))
            frames.append(render_frame(base, body_y=-5 * bounce, tilt=1.8 * wave,
                                       braid_sway=-4 * wave, skirt_lift=3 * bounce,
                                       hand_wave=5 + 3 * wave, mood=1,
                                       blink=1 if i in (2, 3) else 0, gem=0.7 + 0.3 * bounce,
                                       hearts=1, heart_phase=(t * 1.25) % 1.35,
                                       dust=max(0, 0.45 - bounce)))
        else:
            frames.append(render_frame(base, body_y=-1.5 * abs(wave), braid_sway=1.5 * wave,
                                       skirt_lift=0.6 * abs(wave), gem=0.3))
    return frames


def make_sheet(source: Image.Image) -> tuple[Image.Image, dict[int, list[Image.Image]]]:
    fitted = fit_source(source)
    base = Image.new("RGBA", (FRAME_W, FRAME_H))
    base.alpha_composite(fitted, ((FRAME_W - fitted.width) // 2, FRAME_H - fitted.height - 5))
    counts = {0: 6, 1: 8, 2: 8, 3: 4, 4: 5, 5: 8, 6: 6, 7: 6, 8: 6, 9: 8, 10: 8}
    sequences = {row: frame_sequence(base, row, count) for row, count in counts.items()}
    sheet = Image.new("RGBA", (FRAME_W * SHEET_COLS, FRAME_H * SHEET_ROWS))
    for row in range(SHEET_ROWS):
        frames = sequences[row]
        for col in range(SHEET_COLS):
            sheet.alpha_composite(frames[col % len(frames)], (col * FRAME_W, row * FRAME_H))
    return sheet, sequences


def make_preview(sequences: dict[int, list[Image.Image]], path: Path) -> None:
    labels = [(0, "idle"), (3, "wave + hearts"), (4, "jump"), (8, "happy success")]
    preview = Image.new("RGBA", (FRAME_W * 8, (FRAME_H + 24) * len(labels)), (245, 247, 252, 255))
    draw = ImageDraw.Draw(preview)
    for index, (row, label) in enumerate(labels):
        y = index * (FRAME_H + 24)
        draw.text((6, y + 5), label, fill=(35, 40, 55, 255))
        frames = sequences[row]
        for col in range(8):
            preview.alpha_composite(frames[col % len(frames)], (col * FRAME_W, y + 20))
    preview.convert("RGB").save(path, quality=94)


def make_gif(sequences: dict[int, list[Image.Image]], path: Path) -> None:
    order = [0, 0, 3, 3, 4, 4, 8, 8]
    frames = []
    for row in order:
        frames.extend(sequences[row])
    frames = [frame.convert("RGBA") for frame in frames]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=105,
                   loop=0, disposal=2, transparency=0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the coordinated Roxy-inspired Codex pet animation")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--sheet", required=True, type=Path)
    parser.add_argument("--preview", required=True, type=Path)
    parser.add_argument("--gif", required=True, type=Path)
    args = parser.parse_args()
    source = Image.open(args.source).convert("RGBA")
    sheet, sequences = make_sheet(source)
    args.sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.sheet, optimize=True)
    make_preview(sequences, args.preview)
    make_gif(sequences, args.gif)
    print(f"sheet={args.sheet} size={sheet.size}")
    print(f"preview={args.preview}")
    print(f"gif={args.gif}")


if __name__ == "__main__":
    main()
