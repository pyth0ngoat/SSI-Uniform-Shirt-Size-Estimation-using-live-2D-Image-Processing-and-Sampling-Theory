import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import pandas as pd

def create_contact_sheets(manifest_csv: str, output_dir: str):
    df = pd.read_csv(manifest_csv)
    df = df[df['found'] == True]
    
    tile_size = 160
    margin = 20
    text_height = 20
    
    # 5 cols, 6 rows = 30 per page
    cols = 5
    rows = 6
    per_page = cols * rows
    
    page_width = cols * (tile_size + margin) + margin
    page_height = rows * (tile_size + text_height + margin) + margin
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    items = df.to_dict('records')
    num_pages = math.ceil(len(items) / per_page)
    
    for page in range(num_pages):
        img = Image.new('RGB', (page_width, page_height), 'white')
        draw = ImageDraw.Draw(img)
        
        start_idx = page * per_page
        page_items = items[start_idx:start_idx + per_page]
        
        for i, item in enumerate(page_items):
            col = i % cols
            row = i // cols
            
            x = margin + col * (tile_size + margin)
            y = margin + row * (tile_size + text_height + margin)
            
            try:
                photo = Image.open(item['file_path'])
                exif = photo.getexif()
                if exif and 0x0112 in exif:
                    photo = ImageOps.exif_transpose(photo)
                
                # Resize and crop to square
                photo = ImageOps.fit(photo, (tile_size, tile_size), Image.Resampling.LANCZOS)
                img.paste(photo, (x, y))
            except Exception as e:
                draw.rectangle([x, y, x+tile_size, y+tile_size], fill='red')
                
            code = item['code']
            # Simple text
            draw.text((x + 5, y + tile_size + 2), code, fill='black')
            
        out_path = output_dir / f"contact_sheet_page_{page + 1}.png"
        img.save(out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    create_contact_sheets("data/interim/photo_manifest.csv", "data/photos_raw")

