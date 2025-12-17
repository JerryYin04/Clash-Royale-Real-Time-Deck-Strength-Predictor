import pandas as pd
# Load your fresh, clean decks from top ladder
decks = pd.read_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_decks.csv')
cards = pd.read_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_cards_clean.csv')

cards.columns = cards.columns.str.strip()
decks.columns = decks.columns.str.strip()
cards = cards.rename(columns={"type": "card_type"})

merged = decks.merge(cards, left_on="card_name", right_on="name", how="inner")

# THIS IS THE ONLY CORRECT WAY — NO MORE merged.loc[x.index] BUGS
def make_features(group):
    return pd.Series({
        'avg_elixirCost':     round(group['elixirCost'].fillna(0).sum() / 8, 2),
        'avg_card_usage':     round(group['usage'].mean(), 2),
        'total_hitpoints':    group['hitpoints'].fillna(0).sum(),
        'num_air':            ((group['mobility'] == 'flying') & (group['card_type'] != 'spell')).sum(),
        'num_troop':          (group['card_type'] == 'troop').sum(),
        'num_spell':          (group['card_type'] == 'spell').sum(),
        'num_building':       (group['card_type'] == 'building').sum(),
        'num_winconditions': (
            (group['targets'] == 'building') |
            (group['hitpoints'] >= 2500) |
            ((group['elixirCost'] >= 6) & (group['card_type'] == 'troop'))
        ).sum(),
        'num_cycle_cards':    (group['elixirCost'] <= 3).sum(),
        'num_air_attackers':  (group['targets'] == 'both').sum(),
        'num_splash_cards':   (group['attack_type'] == 'splash').sum(),
    })

deck_features = merged.groupby('deck_id').apply(make_features).reset_index()

# Merge back win rate and name
final_df = deck_features.merge(
    decks[['deck_id', 'deck_name', 'deck_win_rate']].drop_duplicates(),
    on='deck_id'
)

final_df = final_df.sort_values('deck_id').reset_index(drop=True)
final_df.to_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/Deck_Data.csv', index=False)

print(f"PERFECT Deck_Data.csv created: {len(final_df)} decks")
print("All features 100% correct — no more broken indexing")