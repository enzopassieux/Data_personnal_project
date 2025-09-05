import pandas as pd

# Charger le CSV principal (avec les données)
df_data = pd.read_csv("inputs/ogd-smn_chz_t_recent.csv", sep=';')

# Charger le CSV des métadonnées
df_meta = pd.read_csv("inputs/ogd-smn_meta_parameters.csv", sep=';', encoding='latin1')

# Créer le mapping shortname -> description française
mapping = dict(zip(df_meta['parameter_shortname'], df_meta['parameter_description_fr']))

# Remplacer les noms des colonnes dans df_data
df_data.rename(columns=mapping, inplace=True)


# Colonnes à conserver
colonnes = [
    "station_abbr",
    "reference_timestamp",
    "Température de l'air à 2 m du sol; valeur instantanée",
    "Vitesse du vent; moyenne sur 10 minutes en km/h",
    "Précipitations; sommation sur 10 minutes",
    "Hauteur de neige (mesurée automatiquement); valeur instantanée",
    "Durée d'ensoleillement; sommation sur 10 minutes"
]

# Filtrer le DataFrame
df_selection = df_data[colonnes]

# Renommer les colonnes
df_selection = df_selection.rename(columns={
    'station_abbr': 'gare',
    'reference_timestamp': 'date'
})

# Vérifier le résultat
print(df_selection.head())

# Vérifier le résultat
print(df_selection.columns)
