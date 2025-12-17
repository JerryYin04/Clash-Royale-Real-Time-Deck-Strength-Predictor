import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
csv_path = "/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/Deck_Data.csv"   
try:
    df = pd.read_csv(csv_path)
    print(f"✓ Successfully loaded {csv_path}")
    print(f"   → {df.shape[0]} decks, {df.shape[1]} columns\n")
except FileNotFoundError:
    print(f"ERROR: Could not find {csv_path}")
    print("   Make sure Deck_Data.csv is in the same folder as this script!")
    exit()

print("First 5 rows:")
print(df.head(), "\n")

# Feature columns (adjust if your CSV has slightly different names)
feature_columns = [
    'avg_elixirCost', 'avg_card_usage', 'total_hitpoints',
    'num_air', 'num_troop', 'num_spell', 'num_building',
    'num_winconditions', 'num_cycle_cards', 'num_air_attackers', 'num_splash_cards'
]

# Check if all columns exist
missing_cols = [col for col in feature_columns if col not in df.columns]
if missing_cols:
    print(f"Missing columns: {missing_cols}")
    print(f"Available columns: {list(df.columns)}")
    exit()

X = df[feature_columns]
y = df['deck_win_rate']

print(f"Using {len(feature_columns)} features → predicting 'deck_win_rate'\n")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training: {X_train.shape[0]} decks | Testing: {X_test.shape[0]} decks\n")

# Train model
print("Training Random Forest...")
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=12,
    min_samples_split=5
)
model.fit(X_train, y_train)
print("Training complete!\n")

# Predictions & evaluation
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("="*50)
print("MODEL RESULTS")
print("="*50)
print(f"Mean Absolute Error (MAE) : {mae:.2f}%")
print(f"Root Mean Squared Error   : {rmse:.2f}%")
print(f"R² Score                  : {r2:.4f}")
print("="*50)

# Feature importance
importance = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importance Ranking:")
print(importance.round(4).to_string(index=False))

# Plot everything
plt.figure(figsize=(15, 10))

plt.subplot(2, 2, 1)
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel("Actual Win Rate (%)")
plt.ylabel("Predicted Win Rate (%)")
plt.title("Predictions vs Actual")
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 2)
sns.barplot(data=importance, x='Importance', y='Feature', palette='magma')
plt.title("Feature Importance")

plt.subplot(2, 2, 3)
errors = y_test - y_pred
plt.hist(errors, bins=20, edgecolor='black', color='orange', alpha=0.7)
plt.axvline(0, color='red', linestyle='--')
plt.xlabel("Prediction Error (%)")
plt.title("Error Distribution")

plt.subplot(2, 2, 4)
plt.scatter(y_pred, errors, alpha=0.6, color='green')
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted Win Rate")
plt.ylabel("Residuals")
plt.title("Residual Plot")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Example predictions
def predict_deck(features_dict):
    df_input = pd.DataFrame([features_dict])
    return model.predict(df_input)[0]

# Try your own decks!
cycle_deck = {'avg_elixirCost': 2.8, 'avg_card_usage': 13, 'total_hitpoints': 6000,
              'num_air': 2, 'num_troop': 7, 'num_spell': 3, 'num_building': 1,
              'num_winconditions': 1, 'num_cycle_cards': 8,
              'num_air_attackers': 5, 'num_splash_cards': 2}

print(f"\nCycle Deck predicted win rate: {predict_deck(cycle_deck):.1f}%")

print("\nAll done! Your model is ready!")