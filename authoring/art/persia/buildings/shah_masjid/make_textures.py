"""Guarded ORIGINAL Shah glaze atlas. Default is read-only; --apply repaints.

Uses the retained deterministic base atlas, never photographs/game pixels.
No caller may bypass image/source hash checks. Run after Blender stops reading
the old images, then rebuild/reload all five maps before comparing renders.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import os
import tempfile

import numpy as np
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
OUT = ROOT / 'textures'
MAPS = ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask')
SEED = 270219
OVERRIDE_ID = 'shah-original-framed-glaze-v2'
PREDECESSOR_ID = 'shah-original-geometric-glaze-v1'
BASE_SOURCES = {
    '_shared/atlas_source.py': 'f575b88e729252c4c1fea0496e6f89d64af1fabca84f32658cc32307d315f445',
    '_shared/make_original_atlas.py': '0ea7d63c3030530407b8dfe74ff451c96401aa5173d6828472efeef2d923e36d',
}
BASE_IMAGES = {
    'albedo.png': 'c5b78b3872270969b18bc0c441b8676be18bfb5c1bdf6f40666a1b04bc7c69de',
    'normal.png': '7f4fb9c72434f0d26376267cca1ebf9a3775998d9acdda6546622d92fdb3018a',
    'roughness.png': 'd5a8c750171a1ce4c030748a0e48df18d6bf2aca697ec8b4bff0a5d948b21f2e',
    'metalness.png': 'bce134076e50c426dde197c9aa3f8e31e544a37bddd810750e2a28fc710b0804',
    'owner_mask.png': '1ce4c23b5f2a66f18d648dda6bc8c1ebb22a406c55c65ae2d00ad9c7e0c21774',
}
PREDECESSOR_IMAGES = dict(BASE_IMAGES, **{
    'albedo.png': 'bcaeb39645301444f39be1378f807f05c7d1afb431120c8caea9743ea52fa1cf',
    'normal.png': 'd1ca3593b24e055f4c42e8f203bc9bc0177dcd0561ead9370ba19d8901f8041e',
    'roughness.png': '02816982189d7f3d3f23ff8c39d9cc97f6045897a4462fb7d33e5d858443ae9a',
})
# Normalized coordinates inside the padded carving tile, also declared in the
# recipe. Wide interlaced facade field, narrow continuous frame, lighter shaft.
CARVING_REGIONS = {'field': [0., 0., .60, 1.], 'border': [.65, 0., .78, 1.],
                   'shaft': [.84, 0., 1., 1.], 'drum': [0., 0., .60, .16]}
PAINT_BOXES = {'roof': (1024, 512, 1536, 1024), 'carving': (1024, 1536, 1536, 2048)}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def current_hashes():
    return {name + '.png': digest(OUT / (name + '.png')) for name in MAPS}


def check_inputs():
    if (OUT / '.shah-atlas-pending.json').exists():
        raise RuntimeError('Incomplete previous atlas transaction; inspect .shah-atlas-pending.json and staged outputs before continuing')
    receipt = json.loads((OUT / 'original-atlas-source.json').read_text(encoding='utf-8'))
    if receipt.get('family') != 'shah_masjid' or receipt.get('seed') != SEED:
        raise RuntimeError('Unexpected family/seed; preserve these images and inspect provenance')
    for relative, expected in BASE_SOURCES.items():
        if digest(ROOT.parent / relative) != expected:
            raise RuntimeError('Base generator changed: ' + relative)
    known = BASE_IMAGES
    if receipt.get('override_id') == OVERRIDE_ID:
        if receipt.get('base_image_sha256') != BASE_IMAGES:
            raise RuntimeError('Override has an unknown base image provenance')
        known = receipt['image_sha256']
    elif receipt.get('override_id') == PREDECESSOR_ID:
        if receipt.get('base_image_sha256') != BASE_IMAGES or receipt.get('image_sha256') != PREDECESSOR_IMAGES:
            raise RuntimeError('Unknown predecessor pixels; do not repaint')
        known = PREDECESSOR_IMAGES
    elif receipt.get('image_sha256') != BASE_IMAGES or receipt.get('source_files') != BASE_SOURCES:
        raise RuntimeError('Unknown initial image receipt; do not overwrite')
    actual = current_hashes()
    if actual != known:
        changed = [name for name in known if actual.get(name) != known[name]]
        raise RuntimeError('Manual/external texture change: ' + ', '.join(changed))
    for name in MAPS:
        with Image.open(OUT / (name + '.png')) as image:
            if image.size != (2048, 2048) or image.mode != ('L' if name in ('roughness', 'metalness') else 'RGB'):
                raise RuntimeError('Wrong map size/mode: ' + name)
    layout = json.loads((OUT / 'atlas-layout.json').read_text(encoding='utf-8'))
    if layout['size'] != 2048 or layout['tile_size'] != 512 or layout['tiles']['roof'] != [2, 1] or layout['tiles']['carving'] != [2, 3]:
        raise RuntimeError('Unexpected atlas layout')
    return actual


def geometric_tile(kind):
    """Original dense interlacing, explicit frame strips and lighter banded glaze.

    All drawing is mathematical. Fine low-contrast straps replace filled pale
    stars; no lettering, copied panel, floral-photo sample or stock pixels.
    """
    def field(width, height, mode):
        yy, xx = np.mgrid[0:height, 0:width]
        u = xx / max(1, width - 1)
        v = 1 - yy / max(1, height - 1)
        grain = 1.1 * np.sin(2 * math.pi * (u * 24 + v * 17)) + .7 * np.cos(2 * math.pi * (u * 48 - v * 23))
        base = np.array({'dome': (43, 132, 142), 'field': (32, 73, 117),
                         'border': (34, 81, 121), 'shaft': (65, 137, 150)}[mode])
        pixels = np.clip(base + grain[:, :, None], 0, 255).astype('uint8')
        relief = np.full((height, width), 132, dtype='uint8')
        roughness = np.clip(98 + grain, 0, 255).astype('uint8')
        if mode in ('dome', 'field'):
            columns, rows = ((24, 16) if mode == 'dome' else (18, 26))
            aa = (u * columns + v * rows) % 1
            bb = (u * columns - v * rows) % 1
            da, db = np.minimum(aa, 1 - aa), np.minimum(bb, 1 - bb)
            # Continuous interlacing, with short dark interruptions at alternating
            # crossings. These are fine straps, never isolated filled stars.
            wa = da < .028
            wb = db < .028
            parity = (np.floor(u * columns + v * rows) + np.floor(u * columns - v * rows)) % 2
            interlace = (wa & ((db > .075) | (parity == 0))) | (wb & ((da > .075) | (parity == 1)))
            colour = (73, 151, 157) if mode == 'dome' else (67, 127, 151)
            pixels[interlace] = colour
            relief[interlace] = 131
            roughness[interlace] = 113
            # Small nested octagonal line cells enrich the field at restrained
            # contrast. Motif frequency is >3x the earlier large-star panel.
            fu = (u * columns) % 1 - .5
            fv = (v * rows) % 1 - .5
            polygon_distance = np.maximum(np.maximum(abs(fu), abs(fv)), (abs(fu) + abs(fv)) / 1.41421356)
            octagon = abs(polygon_distance - .37) < .018
            pixels[octagon] = (91, 158, 160) if mode == 'dome' else (86, 142, 158)
            roughness[octagon] = 109
            # Quiet darker neck/crown bands, geometric rather than epigraphic.
            if mode == 'dome':
                belt = (v < .065) | (v > .945)
                pixels[belt] = (39, 111, 134)
                edge = (abs(v - .065) < .006) | (abs(v - .945) < .006)
                pixels[edge] = (113, 167, 164)
        elif mode == 'border':
            # Cross-strip cream hairlines and turquoise inner rails frame the
            # pishtaq. Longitudinal chain is repeated along actual jamb/frieze.
            pixels[(u < .065) | (u > .935)] = (158, 180, 166)
            pixels[((u > .10) & (u < .20)) | ((u > .80) & (u < .90))] = (68, 144, 154)
            diamond = abs(abs(u - .5) / .25 + abs((v * 24) % 1 - .5) / .46 - 1) < .065
            pixels[diamond & (u > .22) & (u < .78)] = (128, 172, 167)
            roughness[diamond] = 112
        else:
            # The shaft stays visibly lighter than cobalt portal fields. Three
            # larger bands and narrow collars give an architectural hierarchy.
            band = (abs(v - .15) < .027) | (abs(v - .45) < .025) | (abs(v - .72) < .028) | (abs(v - .86) < .047)
            pixels[band] = (42, 94, 132)
            hairline = np.zeros_like(band)
            for value in (.115, .185, .417, .483, .684, .756, .805, .915):
                hairline |= abs(v - value) < .005
            pixels[hairline] = (153, 183, 170)
            diagonal = np.minimum((u * 12 + v * 30) % 1, 1 - (u * 12 + v * 30) % 1) < .025
            pixels[diagonal & ~band & ~hairline] = (81, 149, 157)
            relief[diagonal] = 131
            roughness[diagonal] = 112
        # Exact same longitude samples at both ends, including normals below.
        pixels[:, -1] = pixels[:, 0]
        relief[:, -1] = relief[:, 0]
        roughness[:, -1] = roughness[:, 0]
        return pixels, relief, roughness

    if kind == 'roof':
        rgb, hh, rr = field(472, 472, 'dome')
        ix = (np.arange(512) - 20) % 471
        iy = np.clip(np.arange(512) - 20, 0, 471)
        rgb, hh, rr = (array[iy[:, None], ix[None, :]] for array in (rgb, hh, rr))
    elif kind == 'carving':
        rgb = np.full((512, 512, 3), (34, 81, 121), dtype='uint8')
        hh = np.full((512, 512), 132, dtype='uint8')
        rr = np.full((512, 512), 99, dtype='uint8')
        # Eight-pixel gutters repeat U and clamp V within each dedicated region.
        for mode in ('field', 'border', 'shaft'):
            u0, v0, u1, v1 = CARVING_REGIONS[mode]
            x0, x1 = round(20 + 471 * u0), round(20 + 471 * u1)
            y0, y1 = round(20 + 471 * (1 - v1)), round(20 + 471 * (1 - v0))
            small = field(x1 - x0 + 1, y1 - y0 + 1, mode)
            xs = np.arange(max(0, x0 - 8), min(512, x1 + 9))
            ys = np.arange(max(0, y0 - 8), min(512, y1 + 9))
            local_x = (xs - x0) % max(1, x1 - x0)
            local_y = np.clip(ys - y0, 0, y1 - y0)
            for destination, source in zip((rgb, hh, rr), small):
                destination[ys[:, None], xs[None, :]] = source[local_y[:, None], local_x[None, :]]
    else:
        raise ValueError('Unknown original glaze tile: ' + kind)
    normalized = hh.astype(np.float32) / 255
    dy, dx = np.gradient(normalized)
    n = np.dstack((-dx * .30, -dy * .30, np.ones_like(normalized)))
    n /= np.linalg.norm(n, axis=2)[:, :, None]
    normal = np.clip(np.rint((n * .5 + .5) * 255), 0, 255).astype('uint8')
    return {'albedo': Image.fromarray(rgb), 'normal': Image.fromarray(normal),
            'roughness': Image.fromarray(rr), 'metalness': Image.new('L', (512, 512), 0),
            'owner_mask': Image.new('RGB', (512, 512), (0, 0, 0))}


def paint():
    before = check_inputs()
    source = SHARED / 'atlas_source.py'
    base = {'__name__': 'shah_base_atlas', '__file__': str(source)}
    exec(compile(source.read_text(encoding='utf-8'), str(source), 'exec'), base)
    with tempfile.TemporaryDirectory(prefix='persia_shah_original_atlas_') as temporary:
        base['generate'](Path(temporary), SEED)
        maps = {name: Image.open(Path(temporary) / 'textures' / (name + '.png')).copy() for name in MAPS}
    outside = Image.new('L', (2048, 2048), 255)
    for box in PAINT_BOXES.values():
        ImageDraw.Draw(outside).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=0)
    for name in MAPS:
        old = Image.open(OUT / (name + '.png'))
        difference = ImageChops.difference(old, maps[name]).convert('RGB')
        difference.paste((0, 0, 0), mask=ImageChops.invert(outside))
        if difference.getbbox():
            raise RuntimeError('Base regeneration changed a protected tile: ' + name)
    for kind, box in PAINT_BOXES.items():
        for name, tile in geometric_tile(kind).items():
            maps[name].paste(tile, box[:2])
    encoded = {}
    for name in MAPS:
        payload = io.BytesIO()
        maps[name].save(payload, format='PNG', optimize=True)
        encoded[name + '.png'] = payload.getvalue()
    after = {name: hashlib.sha256(payload).hexdigest() for name, payload in encoded.items()}
    receipt = {
        'schema': 'persia-original-atlas/2', 'family': 'shah_masjid', 'seed': SEED,
        'override_id': OVERRIDE_ID, 'size': [2048, 2048],
        'source_files': dict(BASE_SOURCES, **{'shah_masjid/make_textures.py': digest(__file__),
                                            'shah_masjid/recipe.py': digest(ROOT / 'recipe.py')}),
        'base_image_sha256': BASE_IMAGES, 'previous_image_sha256': before, 'image_sha256': after,
        'original_painted_pixels': True, 'stock_or_photographic_pixels_used': False,
        'tile_overrides': {'roof': 'restrained turquoise fine connected interlacing; no filled pale stars',
                           'carving': 'separate cobalt interlaced field, narrow framed border and lighter banded shaft regions'},
        'carving_regions_in_padded_tile_uv': CARVING_REGIONS,
        'material_contract': {'glaze_metalness': 0, 'glaze_owner_mask_rgb': [0, 0, 0],
                             'roughness': 'glaze approximately .38-.40, fine geometric straps approximately .43-.45',
                             'normal': 'shallow original tangent-space grout; not photographic surface relief'},
        'owner_colour': 'Neutral source textile plus R-only owner mask on owner tile only; fixed blue glaze is not owner colour.',
        'chronology': 'Completed seventeenth-century Royal Mosque influence; original geometry, no copied tile panel or invented calligraphy.',
        'manual_edit_policy': 'All five current PNG hashes must match this receipt before another apply. No force option.',
        'native_shader': 'unverified; source-only',
    }
    # Keep staged outputs and a pending transaction receipt if a process fails
    # between atomic per-file replacements. Base pixels remain reproducible
    # from the hash-locked generator and exact original seed.
    pending = OUT / '.shah-atlas-pending.json'
    if pending.exists():
        raise RuntimeError('Previous incomplete atlas transaction; inspect pending receipt before continuing')
    if current_hashes() != before:
        raise RuntimeError('Images changed during painting; no replacement performed')
    staged = []
    for name, payload in encoded.items():
        path = OUT / (name + '.shah-new')
        if path.exists():
            raise RuntimeError('Unconsumed staged atlas map: ' + path.name)
        path.write_bytes(payload)
        staged.append((path, OUT / name))
    pending.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    for source, destination in staged:
        os.replace(source, destination)
    os.replace(pending, OUT / 'original-atlas-source.json')
    assert current_hashes() == after
    print(json.dumps({'status': 'ORIGINAL_SHAH_ATLAS_WRITTEN', 'image_sha256': after}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Repaint retained live maps after stopping image users; default only checks.')
    parser.add_argument('--check', action='store_true', help='Explicit read-only provenance/dimensions check (the default).')
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error('Choose either --check or --apply')
    if args.apply:
        paint()
    else:
        print(json.dumps({'status': 'READ_ONLY_INPUT_CHECK_PASSED', 'image_sha256': check_inputs()}, indent=2))


if __name__ == '__main__':
    main()
