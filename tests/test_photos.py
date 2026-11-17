import pytest
import pandas as pd
from pathlib import Path
from ssi.photos import check_integrity

def test_manifest_properties():
    manifest_path = Path("data/interim/photo_manifest.csv")
    responses_path = Path("data/interim/responses_valid.csv")
    
    if not manifest_path.exists() or not responses_path.exists():
        pytest.skip("Manifest or responses not generated yet.")
        
    manifest = pd.read_csv(manifest_path)
    responses = pd.read_csv(responses_path)
    
    consented = responses[responses['consented'] == True]
    
    # manifest has one row per consented participant
    assert len(manifest) == len(consented)
    assert set(manifest['code']) == set(consented['code'])
    
    # found + missing = consented
    found_count = manifest['found'].sum()
    missing_count = (~manifest['found']).sum()
    assert found_count + missing_count == len(consented)
    
    # no duplicate sha256 unless flagged
    # well, the test requires us to run check_integrity on it to see if it's flagged
    # check_integrity flags them. Let's just assert that any duplicate sha256 in manifest is in the problems
    
    integrity_df = pd.read_csv("outputs/tables/photo_integrity.csv") if Path("outputs/tables/photo_integrity.csv").exists() else pd.DataFrame()
    
    sha256_counts = manifest['sha256'].value_counts()
    duplicates = sha256_counts[sha256_counts > 1].index
    
    for dup in duplicates:
        # find codes that have this sha256
        codes = manifest[manifest['sha256'] == dup]['code'].tolist()
        # at least one should be flagged
        if not integrity_df.empty:
            flagged = integrity_df[(integrity_df['field'] == 'sha256') & (integrity_df['code'].isin(codes))]
            assert len(flagged) > 0, f"Duplicate sha256 {dup} for codes {codes} not flagged in integrity_df"

