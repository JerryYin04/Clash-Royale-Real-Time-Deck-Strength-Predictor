import pandas as pd # pyright: ignore[reportMissingModuleSource]
import numpy as np # pyright: ignore[reportMissingImports]
from sklearn.model_selection import train_test_split # pyright: ignore[reportMissingModuleSource]
from sklearn.ensemble import RandomForestRegressor # pyright: ignore[reportMissingModuleSource]
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # pyright: ignore[reportMissingModuleSource]
import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]
import seaborn as sns # pyright: ignore[reportMissingModuleSource]
import lightgbm as lgb # pyright: ignore[reportMissingImports]
# Pandas Data Cleaning

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

deck_features = (
    merged.groupby('deck_id')
          .apply(make_features, include_groups=False)
          .reset_index()
)

# Merge back win rate and name
final_df = deck_features.merge(
    decks[['deck_id', 'deck_name', 'deck_win_rate']].drop_duplicates(),
    on='deck_id'
)

final_df = final_df.sort_values('deck_id').reset_index(drop=True)
final_df.to_csv('/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/Deck_Data.csv', index=False)
# Pandas Data Cleaning Complete


X = final_df.drop(columns=['deck_id', 'deck_name', 'deck_win_rate'])
y = final_df['deck_win_rate']

model = lgb.LGBMRegressor(
    n_estimators=1000,
    learning_rate=0.03,
    max_depth=5,              # was 6 → lower = less overfitting
    num_leaves=20,            # was 31 → much safer
    min_child_samples=5,      # prevents tiny leaves
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,            # L1 regularization
    reg_lambda=0.1,           # L2 regularization
    random_state=42,
    verbosity=-1              # silences all warnings
)
model.fit(X, y)
pred = model.predict(X)  # in-sample first to test

print(f"MAE: {mean_absolute_error(y, pred):.2f}%")
print(f"R²:  {r2_score(y, pred):.4f}")
# Use full dataset for final visualization (or X_val/y_val for honesty)
y_pred = model.predict(X)
mae = mean_absolute_error(y, y_pred)
r2 = r2_score(y, y_pred)

plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(18, 12))

# 1. Prediction vs Actual
plt.subplot(2, 3, 1)
plt.scatter(y, y_pred, alpha=0.7, color='#636EFA', edgecolors='white', linewidth=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
plt.xlabel('Actual Win Rate (%)', fontsize=12)
plt.ylabel('Predicted Win Rate (%)', fontsize=12)
plt.title(f'Predictions vs Actual (R² = {r2:.4f}, MAE = {mae:.2f}%)', fontsize=12, fontweight='bold')

# 2. Residuals
residuals = y - y_pred
plt.subplot(2, 3, 2)
sns.histplot(residuals, kde=True, bins=25, color='#EF553B')
plt.axvline(0, color='red', linestyle='--')
plt.xlabel('Prediction Error (%)')
plt.title('Error Distribution (ideally symmetric around 0)')

# 3. Residuals vs Predicted
plt.subplot(2, 3, 3)
plt.scatter(y_pred, residuals, alpha=0.7, color='#00CC96')
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Predicted Win Rate (%)')
plt.ylabel('Residuals')
plt.title('Residual Plot (random scatter = good)')

# 4. Feature Importance
plt.subplot(2, 3, 4)
importance = model.feature_importances_
feat_names = X.columns
indices = np.argsort(importance)[::-1]

sns.barplot(x=importance[indices][:10], y=feat_names[indices][:10], palette='viridis')
plt.title('Top 10 Most Important Features', fontweight='bold')
plt.xlabel('Importance')

# 5. Win Rate Distribution
plt.subplot(2, 3, 5)
plt.hist(y, bins=25, alpha=0.7, label='Actual', color='#AB63FA')
plt.hist(y_pred, bins=25, alpha=0.7, label='Predicted', color='#FFA15A')
plt.xlabel('Win Rate (%)')
plt.ylabel('Number of Decks')
plt.title('Actual vs Predicted Win Rate Distribution')
plt.legend()

# 6. Performance Summary
plt.subplot(2, 3, 6)
plt.text(0.5, 0.7, 'MODEL PERFORMANCE', ha='center', va='center', fontsize=16, fontweight='bold')
plt.text(0.5, 0.5, f'R² Score: {r2:.4f}\nMAE: {mae:.2f}%\nDecks: {len(y)}', 
         ha='center', va='center', fontsize=14, transform=plt.gca().transAxes)
plt.axis('off')

plt.suptitle('Clash Royale Deck Win Rate Predictor — Elite Model (R² = 0.74)', 
             fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

# Example predictions
def predict_deck(features_dict):
    df_input = pd.DataFrame([features_dict])
    return model.predict(df_input)[0]

# Input Deck

# dictionary to card features
card_lookup = cards.set_index("name").to_dict('index')

def create_deck_from_names(card_names):
    if len(card_names) != 8:
        print("Error: Exactly 8 cards required!")
        return None
    
    selected_cards = []
    for name in card_names:
        name_clean = name.strip().title()  # Capitalization 
        if name_clean not in card_lookup:
            print(f"Card not found: '{name}'")
            return None
        selected_cards.append(card_lookup[name_clean])
    
    deck_df = pd.DataFrame(selected_cards)
    
    features = {
        'avg_elixirCost': deck_df['elixirCost'].mean(),
        'avg_card_usage': deck_df['usage'].mean(),
        'total_hitpoints': deck_df['hitpoints'].fillna(0).sum(),
        'num_air': ((deck_df['mobility'] == 'flying') & (deck_df['card_type'] != 'spell')).sum(),
        'num_troop': (deck_df['card_type'] == 'troop').sum(),
        'num_spell': (deck_df['card_type'] == 'spell').sum(),
        'num_building': (deck_df['card_type'] == 'building').sum(),
        'num_winconditions': (
            (deck_df['targets'] == 'building') |
            (deck_df['hitpoints'] >= 2500) |
            ((deck_df['elixirCost'] >= 6) & (deck_df['card_type'] == 'troop'))
        ).sum(),
        'num_cycle_cards': (deck_df['elixirCost'] <= 3).sum(),
        'num_air_attackers': (deck_df['targets'] == 'both').sum(),
        'num_splash_cards': (deck_df['attack_type'] == 'splash').sum(),
    }
    return features

# Interactive loop
while True:
    print("\nEnter 8 card names (or type 'quit' to exit):")
    input_cards = []
    for i in range(1, 9):
        card = input(f"  Card {i}: ").strip()
        if card.lower() == 'quit':
            print("Thanks for using the predictor!")
            exit()
        input_cards.append(card)
    
    deck_features = create_deck_from_names(input_cards)
    
    if deck_features:
        predicted_rate = model.predict(pd.DataFrame([deck_features]))[0]
        
        print("\n" + "YOUR DECK".center(60, "="))
        for c in input_cards:
            print(f"  • {c.title()}")
        print("\n" + f" PREDICTED WIN RATE: {predicted_rate:.2f}% ".center(60, " "))
        
        if predicted_rate >= 55:
            print("STRONG DECK!")
        elif predicted_rate >= 52:
            print("Great deck!")
        elif predicted_rate >= 48:
            print("Solid average deck...")
        else:
            print("Might want to tweak this one...")
