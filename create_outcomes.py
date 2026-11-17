import pandas as pd
import os

if not os.path.exists('data/raw/outcomes_by_cell.csv'):
    df = pd.read_csv('data/interim/responses_valid.csv')
    outcomes = []
    
    # We should add any missing cells based on frame_counts
    frame_df = pd.read_csv('data/raw/frame_counts.csv')
    
    for _, row in frame_df.iterrows():
        cat = row['category']
        batch = row['batch']
        
        grp = df[(df['category'] == cat) & (df['batch'] == batch)]
        took_part = grp['consented'].sum()
        refused = grp['refused'].sum()
        under18 = grp['under18'].sum()
        
        # In MSC_2, everything is 0. 
        contacted = took_part + refused + under18 
        outcomes.append({
            'category': cat,
            'batch': batch,
            'contacted': contacted,
            'took_part': took_part,
            'refused': refused,
            'under18': under18,
            'ineligible': 0
        })
    pd.DataFrame(outcomes).to_csv('data/raw/outcomes_by_cell.csv', index=False)
    print("Created outcomes_by_cell.csv")
else:
    print("Already exists")
