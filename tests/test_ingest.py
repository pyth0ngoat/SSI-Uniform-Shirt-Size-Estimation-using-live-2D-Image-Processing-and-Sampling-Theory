import pytest
import pandas as pd
from pathlib import Path
import yaml
from ssi.config import load_config
from ssi.ingest import load_responses, validate_responses, run_ingest

@pytest.fixture
def config():
    return load_config()

@pytest.fixture
def golden():
    with open("tests/golden.yaml", "r") as f:
        return yaml.safe_load(f)

def test_ingest_golden(config, golden):
    raw_dir = Path("data/raw")
    xlsx_path = raw_dir / "responses_export.xlsx.xlsx"
    if not xlsx_path.exists():
        xlsx_path = raw_dir / "responses_export.xlsx"
    df = load_responses(xlsx_path, config)
    
    assert len(df) == golden["rows_total"]
    assert df["consented"].sum() == golden["consented"]
    assert df["refused"].sum() == golden["refused"]
    assert df["under18"].sum() == golden["under18"]

    consented_df = df[df["consented"]]
    
    # Category counts
    cat_counts = consented_df["category"].value_counts().to_dict()
    assert cat_counts.get("BOYS", 0) == golden["consented_by_category"]["BOYS"]
    assert cat_counts.get("GIRLS", 0) == golden["consented_by_category"]["GIRLS"]

    # Batch counts
    batch_counts = consented_df["batch"].value_counts().to_dict()
    for b, c in golden["consented_by_batch"].items():
        assert batch_counts.get(b, 0) == c
        
    # Size counts BOYS
    boys = consented_df[consented_df["category"] == "BOYS"]
    size_boys = boys["size_reported"].value_counts().to_dict()
    for s, c in golden["size_counts_boys"].items():
        assert size_boys.get(s, 0) == c
        
    # Size counts GIRLS
    girls = consented_df[consented_df["category"] == "GIRLS"]
    size_girls = girls["size_reported"].value_counts().to_dict()
    for s, c in golden["size_counts_girls"].items():
        assert size_girls.get(s, 0) == c

    # How in counts
    how_in = consented_df["how_in_short"].value_counts().to_dict()
    assert how_in.get("primary", 0) == golden["how_in_consented"]["primary"]
    assert how_in.get("reserve", 0) == golden["how_in_consented"]["reserve"]

def test_corrupted_data(config):
    raw_dir = Path("data/raw")
    xlsx_path = raw_dir / "responses_export.xlsx.xlsx"
    if not xlsx_path.exists():
        xlsx_path = raw_dir / "responses_export.xlsx"
    df = load_responses(xlsx_path, config)
    
    # Corrupt data
    corrupt = df.iloc[0:1].copy()
    corrupt["code"] = df.iloc[1]["code"] # duplicate code
    corrupt["height_cm"] = 17 # out of range
    corrupt["size_reported"] = 41 # invalid size
    corrupt["photo_link"] = pd.NA # missing photo
    corrupt["consented"] = True
    
    df_corrupted = pd.concat([df, corrupt], ignore_index=True)
    probs = validate_responses(df_corrupted, config)
    
    errors = probs[probs["severity"] == "ERROR"]
    
    assert (errors["field"] == "code").any() # duplicate
    assert (errors["field"] == "height_cm").any() # height out of range
    assert (errors["field"] == "size_reported").any() # invalid size
    assert (errors["field"] == "photo_link").any() # missing photo
