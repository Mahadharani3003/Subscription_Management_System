# -*- coding: utf-8 -*-
"""Generate a sleek 128x128 icon.png for Brightloop using pure Python struct and zlib."""
import struct
import zlib
import os

def create_png():
    width = 128
    height = 128
    
    raw_data = bytearray()
    
    # Palette colors: modern indigo gradient (#4F46E5 to #7C3AED)
    for y in range(height):
        raw_data.append(0) # filter byte: none
        for x in range(width):
            # Rounded rect background
            dx = min(x, width - 1 - x)
            dy = min(y, height - 1 - y)
            dist_corner = 0
            radius = 24
            if dx < radius and dy < radius:
                dist_corner = ((radius - dx)**2 + (radius - dy)**2)**0.5
            
            if dist_corner > radius:
                # Transparent outside rounded corner
                raw_data.extend([0, 0, 0, 0])
                continue
                
            # Circular recurring arrows / Loop glyph
            cx = x - 64
            cy = y - 64
            dist_center = (cx**2 + cy**2)**0.5
            
            # Gradient background
            r = int(79 + (y / height) * 45)
            g = int(70 + (y / height) * 10)
            b = int(229 + (y / height) * 15)
            alpha = 255
            
            # White recurring loop ring
            if 28 <= dist_center <= 42:
                # Loop ring with an open gap at top-right
                angle = (cx, cy)
                if not (cx > 0 and cy < -10):
                    r, g, b = 255, 255, 255
            
            # Center bright dot / node
            if dist_center <= 12:
                r, g, b = 56, 189, 248 # Cyan accent (#38BDF8)
                
            raw_data.extend([r, g, b, alpha])
            
    compressed = zlib.compress(raw_data)
    
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png.extend(struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc))
    
    # IDAT
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    png.extend(struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc))
    
    # IEND
    iend_crc = zlib.crc32(b'IEND')
    png.extend(struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc))
    
    out_dir = os.path.join(os.path.dirname(__file__), 'brightloop_subscription', 'static', 'description')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'icon.png')
    with open(out_path, 'wb') as f:
        f.write(png)
    print(" [OK] Generated icon.png at", out_path)

if __name__ == '__main__':
    create_png()
