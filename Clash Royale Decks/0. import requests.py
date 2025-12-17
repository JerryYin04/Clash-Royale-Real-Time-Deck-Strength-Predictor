import requests # pyright: ignore[reportMissingModuleSource]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
import numpy as np  # pyright: ignore[reportMissingImports]
import time
from collections import defaultdict

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImNhNTAyOWU0LTRmMjAtNDY4My1iMjVjLWJiMzBhYjljYjA1NCIsImlhdCI6MTc2Mzc1NTI5NSwic3ViIjoiZGV2ZWxvcGVyLzI0ZGM4ZmI4LWUzNzQtY2VjYi1lZGU1LWQ4ZDRhM2Q3MzU3YyIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI0NS43OS4yMTguNzkiLCIxMzEuMTc5Ljk0LjkxIl0sInR5cGUiOiJjbGllbnQifV19.-ER65x3zf6aWlnJQ5MdxSuc-dox8l5z8EkF059SHM3qqm9BpK_x5nfAitxdBSSl-Xi_8YgmzYB1wEB2xmNZL3g'                       # Your working key
BASE_URL = 'https://proxy.royaleapi.dev/v1'     # Proxy 
headers = {'Authorization': f'Bearer {API_KEY}'}

# 200 TOP LADDER PLAYER TAGS (from RoyaleAPI leaderboards, Nov 2025)
TOP_PLAYERS = [
    '8022RY8YU', 'RUQ0JU2P', 'VCQUY9Y8U', '2Q2QCYLPR', '208R8PQJP9', 
    'G0CYJ00J', 'YUQYJV08', '20LGRRLGYL', 'P8P0Q8CJ', 'C89G2280Q', 
    'LLYGJL0R', 'CVVCU2JJ8', 'RJ2UPC900', '9890JJJV', '9R2RQPV9Q', 
    '2RCR8PJV', 'QQUJ2Y2C', 'CRLJ2JQVG', 'Y022GRCJQ', 'GUPVGVQQV', 
    'V02VR8JVP', 'UVGR0URPQ', 'G9YV9GR8R', 'V8CYPRG89', 'CRUGCURRP', 
    'UL9JUUG90', 'UYL8820RJ', 'UJRR9RJUL', 'C2RL0PYLV', 'LP8PLVJCU', 
    '898Y8PGJ9', 'G0LP8UVQ8', 'VC9PYQ028', 'YJPLQRR09', '200LG22CQC', 
    'VL8VY0QJU', 'GGV9YLQY', '9CPCC890', '2U0LLGPUJ', 'LPRR9P', 
    '2CYR8LCUP', 'YYYQ2Y9LP', 'U2LYQJQVY', 'UL0JRU8JY', '20PYQL0PLC', 
    '800GQP89P', 'CJLUUCJUG', 'VCG2JVJ8C', 'JQ2V2JJ8G', '290VGG28', 
    'VR90898', '2CJPLUL2J', 'VGJPL2R8P', '2LG8QP000', 'CL0CGQLQL', 
    'UCL0UCPYC', 'V0G2JGUUR', '9RG0VPUVY', 'U8J0GQ02U', 'PG88V9GVY', 
    'VY909229L', 'U9VVGU229', 'JUV2PUJR8', 'Y90P8VUQY', '2GGR2GPQ0', 
    'G8GUQGYU8', 'YUYR99U', '2G2PGY8UU', '9RQ8YRYQL', 'GYRLULV80', 
    'YJYJYVGLR', 'LJQVVVQGR', 'RJ88Y8U08', 'C0V0UQ9UY', '2VYLGPPUV', 
    'CRJUPR08', '20PVYJJL8P', 'V9C89L9LQ', 'VRYRUY8V0', '9JVCJ92V9', 
    'PYPGQUPGP', 'VYPGYJJGY', '2VYJYJ09', 'CR9R0V9PY', 'V9QVYG98Y', 
    'GU2YR209R', 'YP9VPGUUG', 'Y2YYC2RVV', 'J98VRG0QY', '9CJ9QQG0R', 
    '2LQ2YP98', 'J02VCV2C0', 'V2YPU2VRR', 'UYUVCY298', '2LUY2Q98', 
    'LUJR90C2', 'JPPC9URJ', '8JJ80J28', 'RU9VQV9C', 'PJL8PCGCP', 
    'QCR2VCQYU', 'PYPGQUPGP', '208RCR2CC0', '2CYR8LCUP', 'U2LYQJQVY', 
    'LJRUJR0Y0', '2LQ2YP98', 'JQ2V2JJ8G', 'UGU2QLJVL', '298LLPGQP', 
    '2LUY2Q98', 'JQP8R9JR', 'V9QVYG98Y', 'PJL8PCGCP', 'UV2GL9PVQ', 
    'L0JPVCRRQ','LGJLLC2YG', '98Q8LPQ9', 'V9JLYVJCQ', 'G2RUR0PL2', 
    'PP2C9LVG', 'CQUL0UV0', '22L8UUV0Q', '28UCRV0U9', 'PCJL80VC', 
    'R892YCVQL', 'QJ99JYYVC', '82PPJQYVP', 'U8RYGC8GU', 'QG9LCJ29', 
    'P0LQQ0L0', 'VPPJ9Y9YR', 'Q0C8LC8', '2PPRU8QU0', 'GR9L9V2LU', 
    '2GVJY9CR', 'LQJJJL8R', 'PCJ29YJJ', 'R09228V', 'YYYLGRP0J', 
    '8QUVYC0G', 'QVGJUJLC', 'QV2PYL', 'YCYQV2CY0', '2822UQRYL', 
    'VJVJRPPUY', '290UQY8C', 'U9R9C2G88', 'VG8LCL0QY', 'JYC0PU8C', 
    'U8PYC2Q2P', 'UR0JY9VLC', '2GQCV0UVQ', 'CLQGQ8JVU', 'QP80QGQ0V', 
    'PRYLGLRQU', 'UU0PJ829', 'UC0QJ2CU9', '2GGP982PP', 'Q2JJJRRYC', 
    '9JPPG9QRG', '908G0G8Y', '2Y20C8U0C', 'V0UP09P', 'UYUVCY298', 
    'ULGQUY89L', 'VCR2LQP88', 'LP0LR9LRU', 'G89PLJYRY', '8VGQQ80UU', 
    'YQVCQVCRQ', 'GJ9VPRVQG', 'GVVU2P8QQ', 'JJ0P22Y0Y', 'U2G8P8CV2', 
    '2VYLGPPUV', 'U8QGUPL2L', 'YJPPGL00', '9PRUJR099', 'U890Q9UQ', 
    'YYYQ2Y9LP', 'VQ8VVLVV8', 'UGUQR20V9', 'CRYUCRVUG', '2LV9VRY8G', 
    '2PLLPVURP', 'JVP8UY0R8', 'JRLVPG88L', 'VR8YGR8YL', 'R998YLQ0L', 
    '2JQ0GRRJ8', 'UQQCLV989', 'PCUP9YLVG', 'C0CYVCVYC', 'PYCGV92P', 
    'RU9VQV9C', '2QRR89CUG', '80ULUJLYY', 'CJCCVGQVQ', 'VP08G9PJQ'
]

all_battles = []

print("Collecting battles from 200 real top players (with pagination for more decks)...\n")

for i, tag in enumerate(TOP_PLAYERS, 1):
    print(f"[{i}/{len(TOP_PLAYERS)}] #{tag}")
    
    after = None
    battles_collected = 0
    for page in range(10):  # 10 pages = 300 battles
        url = f'{BASE_URL}/players/%23{tag}/battlelog?limit=30'
        if after:
            url += f'&after={after}'
        r = requests.get(url, headers=headers)
        
        if r.status_code != 200:
            print(f"   → Failed ({r.status_code})")
            break

        battles = r.json()
        if not battles:  
            break

        for battle in battles:
            # Compare crowns (player vs opponent)
            player_crowns = battle['team'][0]['crowns']
            opponent_crowns = battle['opponent'][0]['crowns']
            win = 1 if player_crowns > opponent_crowns else 0

            # Deck extraction (8 cards)
            cards = [c['name'] for c in battle['team'][0]['cards']]
            deck_str = ', '.join(sorted(cards))  # Sorted for deduplication

            all_battles.append({
                'player_tag': tag,
                'deck_id': hash(deck_str),
                'cards': deck_str,
                'win': win,  
                'player_crowns': player_crowns,
                'opponent_crowns': opponent_crowns
            })
        
        battles_collected += len(battles)
        after = battles[-1]['battleTime'] if battles else None  # Paginate to next
        time.sleep(0.4)
    
    print(f"   → {battles_collected} battles")

print(f"\nCollected {len(all_battles)} battles from top players")

# ──────────────────────── PROCESS TO DECKS ────────────────────────
df = pd.DataFrame(all_battles)

# Use consistent deck identifier (hash → string for safety)
df['deck_key'] = df['cards']
deck_stats = df.groupby('deck_key').agg(
    total_matches=('win', 'count'),
    wins=('win', 'sum'),
    cards=('cards', 'first')
).reset_index()

# Raw win rate
deck_stats['raw_wr'] = deck_stats['wins'] / deck_stats['total_matches'] * 100

# Keep only decks with ≥20 matches (best balance: noise vs quantity)
deck_stats = deck_stats[deck_stats['total_matches'] >= 20].copy()
print(f"Kept {len(deck_stats)} decks with ≥18 matches")


# Sort by win rate and reassign clean IDs
deck_stats = deck_stats.sort_values('deck_win_rate', ascending=False).reset_index(drop=True)
deck_stats['deck_id'] = range(1, len(deck_stats) + 1)
deck_stats['deck_name'] = 'Deck ' + deck_stats['deck_id'].astype(str)

# Explode to one row per card
deck_stats['card_name'] = deck_stats['cards'].str.split(', ')
final_decks = deck_stats.explode('card_name')

# Final clean dataset
final_decks = final_decks[['deck_id', 'deck_name', 'card_name', 'deck_win_rate']].copy()

# Save
final_decks.to_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_decks.csv', index=False)

print(f"\nSUCCESS! Saved {len(deck_stats)} high-quality decks (≥18 matches each)")
print(f"   → Total rows: {len(final_decks)} (8 per deck)")
print(f"   → Win rate range: {final_decks['deck_win_rate'].min():.1f}% – {final_decks['deck_win_rate'].max():.1f}%")
print("\nFirst 10 rows:")
print(final_decks.head(10)[['deck_id', 'deck_name', 'card_name', 'deck_win_rate']].to_string(index=False))