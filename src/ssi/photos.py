import pandas as pd
from pathlib import Path
import hashlib
from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

def ahash(image, hash_size=8):
    image = image.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    val = 0
    for i, p in enumerate(pixels):
        if p > avg:
            val += 1 << i
    return val

def hamming_distance(hash1, hash2):
    return bin(hash1 ^ hash2).count('1')

def build_manifest(responses_csv_path: str, photos_dir: str, photo_name_map_csv: str = None) -> pd.DataFrame:
    df = pd.read_csv(responses_csv_path)
    consented_df = df[df['consented']].copy()
    
    name_map = {}
    if photo_name_map_csv and Path(photo_name_map_csv).exists():
        map_df = pd.read_csv(photo_name_map_csv)
        name_map = dict(zip(map_df['code'], map_df['file_name']))
        
    photos_dir = Path(photos_dir)
    manifest_rows = []
    
    exts = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
    all_files = [f for f in photos_dir.rglob("*.*") if f.suffix.lower() in exts]
    
    heic_needed = []
    
    for _, row in consented_df.iterrows():
        code = row['code']
        found = False
        file_path = None
        width = height = fmt = file_size_kb = sha256 = phash_val = None
        exif_orientation_applied = False
        
        expected_names = []
        if code in name_map:
            expected_names.append(name_map[code])
        for ext in exts:
            expected_names.append(f"{code}{ext}")
            expected_names.append(f"{code}{ext}".upper())

        for f in all_files:
            if f.name in expected_names or (code in name_map and f.name == name_map[code]):
                file_path = f
                found = True
                break

        if not found:
            for f in all_files:
                if f.stem.upper() == code:
                    file_path = f
                    found = True
                    break
        
        if found:
            if file_path.suffix.lower() == '.heic' and not HEIF_SUPPORT:
                heic_needed.append(file_path.name)
                found = False 
                file_path = None
            else:
                try:
                    file_size_kb = file_path.stat().st_size / 1024
                    
                    with open(file_path, "rb") as f:
                        sha256 = hashlib.sha256(f.read()).hexdigest()
                        
                    img = Image.open(file_path)
                    fmt = img.format
                    
                    exif = img.getexif()
                    if exif and 0x0112 in exif:
                        exif_orientation_applied = True
                        img = ImageOps.exif_transpose(img)
                        
                    width, height = img.size
                    phash_val = ahash(img)
                    
                except Exception as e:
                    found = False
                    width = height = fmt = file_size_kb = sha256 = phash_val = None
                    file_path = None
        
        manifest_rows.append({
            'code': code,
            'file_path': str(file_path) if file_path else None,
            'found': found,
            'width': width,
            'height': height,
            'format': fmt,
            'file_size_kb': file_size_kb,
            'exif_orientation_applied': exif_orientation_applied,
            'sha256': sha256,
            'phash': phash_val
        })

    if heic_needed:
        print("WARNING: pillow-heif not installed. Following HEIC files need converting:", heic_needed)

    return pd.DataFrame(manifest_rows)

def check_integrity(manifest_df: pd.DataFrame) -> pd.DataFrame:
    problems = []
    
    sha256_seen = {}
    phash_seen = {}
    
    for _, row in manifest_df.iterrows():
        code = row['code']
        
        if not row['found']:
            problems.append({'code': code, 'field': 'file', 'problem': 'Missing or unreadable', 'severity': 'ERROR'})
            continue
            
        width, height = row['width'], row['height']
        if width is None or height is None:
            problems.append({'code': code, 'field': 'file', 'problem': 'Unreadable size', 'severity': 'ERROR'})
            continue
            
        if min(width, height) < 480:
            problems.append({'code': code, 'field': 'resolution', 'problem': f'Min side < 480 px (is {min(width, height)})', 'severity': 'ERROR'})
            
        if width >= height:
            problems.append({'code': code, 'field': 'orientation', 'problem': 'Landscape orientation', 'severity': 'WARNING'})
            
        sha = row['sha256']
        if sha in sha256_seen:
            problems.append({'code': code, 'field': 'sha256', 'problem': f'Duplicate of {sha256_seen[sha]}', 'severity': 'ERROR'})
        else:
            sha256_seen[sha] = code
            
        phash_val = row['phash']
        if pd.notna(phash_val):
            phash_val = int(phash_val)
            for seen_hash, seen_code in phash_seen.items():
                if hamming_distance(phash_val, seen_hash) <= 4:
                    problems.append({'code': code, 'field': 'phash', 'problem': f'Near-duplicate of {seen_code}', 'severity': 'WARNING'})
            phash_seen[phash_val] = code
            
    return pd.DataFrame(problems, columns=['code', 'field', 'problem', 'severity'])

def run_photos():
    responses_csv = "data/interim/responses_valid.csv"
    photos_dir = "data/photos_raw"
    photo_name_map = "data/raw/photo_name_map.csv"
    manifest_csv = "data/interim/photo_manifest.csv"
    integrity_csv = "outputs/tables/photo_integrity.csv"
    
    manifest_df = build_manifest(responses_csv, photos_dir, photo_name_map)
    export_df = manifest_df.drop(columns=['phash'], errors='ignore')
    export_df.to_csv(manifest_csv, index=False)
    
    integrity_df = check_integrity(manifest_df)
    if not integrity_df.empty:
        integrity_df.to_csv(integrity_csv, index=False)
    else:
        pd.DataFrame(columns=['code', 'field', 'problem', 'severity']).to_csv(integrity_csv, index=False)
        
    expected = len(manifest_df)
    found = manifest_df['found'].sum()
    missing_codes = manifest_df[~manifest_df['found']]['code'].tolist()
    
    unreadable = 0
    duplicates = 0
    landscape = 0
    if not integrity_df.empty:
        unreadable = len(integrity_df[integrity_df['problem'] == 'Unreadable size'])
        duplicates = len(integrity_df[integrity_df['field'].isin(['sha256', 'phash'])])
        landscape = len(integrity_df[integrity_df['field'] == 'orientation'])
        
    print(f"Photos expected: {expected}")
    print(f"Photos found: {found}")
    print(f"Missing codes: {missing_codes}")
    print(f"Unreadable: {unreadable}")
    print(f"Duplicates (exact or near): {duplicates}")
    print(f"Landscape: {landscape}")
    
if __name__ == "__main__":
    run_photos()

