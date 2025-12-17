import pandas as pd

df = pd.read_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_cards.csv', encoding='utf-8')
df = df.replace('%', '', regex=True)
df = df.apply(pd.to_numeric, errors='ignore')
df.to_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_cards_clean.csv', index=False, encoding='ascii', errors='ignore')