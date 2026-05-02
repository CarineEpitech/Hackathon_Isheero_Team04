from pathlib import Path
import pandas as pd

# Chemin absolu basé sur l'emplacement du script
ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "data/raw/benin_raw.csv"

df = pd.read_csv(DATA_PATH, nrows=5)

print(f"Nombre de colonnes : {df.shape[1]}")
print("\nListe des colonnes :")
for i, col in enumerate(df.columns.tolist(), 1):
    print(f"  {i:02d}. {col}")