from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Chargement du fichier DVF
df = pd.read_csv("DVF_78.csv", delimiter="|")

# On retire les lignes incomplètes pour éviter les erreurs
df = df.dropna(subset=[
    "code_postal",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "valeur_fonciere"
])

@app.get("/ventes")
def get_ventes(code_postal: str, surface: float, pieces: int):
    # Filtrer par code postal
    ventes = df[df["code_postal"] == int(code_postal)]

    # Filtrer sur surface ±10%
    ventes = ventes[
        (ventes["surface_reelle_bati"] >= surface * 0.9) &
        (ventes["surface_reelle_bati"] <= surface * 1.1)
    ]

    # Filtrer sur nombre de pièces ±1
    ventes = ventes[
        (ventes["nombre_pieces_principales"] >= pieces - 1) &
        (ventes["nombre_pieces_principales"] <= pieces + 1)
    ]

    # Trier par date la plus récente
    ventes = ventes.sort_values(by="date_mutation", ascending=False)

    # Ne garder que les colonnes utiles
    ventes = ventes[[
        "adresse_numero",
        "adresse_nom_voie",
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "valeur_fonciere",
        "date_mutation",
        "type_local"
    ]].head(5)

    # Transformer en JSON
    resultats = []
    for _, row in ventes.iterrows():
        adresse = f"{int(row['adresse_numero'])} {row['adresse_nom_voie']}" if not pd.isna(row["adresse_numero"]) else row["adresse_nom_voie"]
        resultats.append({
            "adresse": adresse,
            "surface": row["surface_reelle_bati"],
            "pieces": row["nombre_pieces_principales"],
            "type": row["type_local"],
            "prix": row["valeur_fonciere"],
            "date": row["date_mutation"]
        })

    return resultats
