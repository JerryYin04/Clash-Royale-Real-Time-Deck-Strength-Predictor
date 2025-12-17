import pandas as pd # pyright: ignore[reportMissingModuleSource]

# Your file path
file_path = '/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_decks.csv'

# Load data
print("Loading data...")
df = pd.read_csv(file_path)

print(f"Before filtering: {len(df)} rows, {df['deck_id'].nunique()} unique decks")

# Count cards per deck_id
card_counts = df.groupby('deck_id').size()

# Keep only deck_ids with EXACTLY 8 cards
valid_decks = card_counts[card_counts == 8].index

# Filter
filtered_df = df[df['deck_id'].isin(valid_decks)].copy()

# Sort for clean order
filtered_df = filtered_df.sort_values(['deck_id', 'card_name']).reset_index(drop=True)

# OVERWRITE the original file
filtered_df.to_csv(file_path, index=False)

# Report
removed_decks = len(card_counts) - len(valid_decks)
print(f"\nDONE! Original file overwritten.")
print(f"   → Removed {removed_decks} incomplete/broken decks")
print(f"   → Kept {len(valid_decks)} perfect 8-card decks")
print(f"   → Now: {len(filtered_df)} rows ({len(valid_decks)} × 8)")
print(f"   → All averages will now be clean (divided by 8)")

print("\nFirst 8 rows (deck_id 1):")
print(filtered_df.head(8)[['deck_id', 'deck_name', 'card_name']].to_string(index=False))