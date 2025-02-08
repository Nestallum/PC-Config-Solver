import os
import pandas as pd

def load_all_data(data_dir="data"):
    """
    Loads all CSV files (CPUs, motherboards, RAM) as pandas DataFrames.
    Returns a dictionary with the data.
    """
    files = {
        "CPU": "cpus.csv",
        "Motherboard": "motherboards.csv",
        "RAM": "ram.csv",
        "GPU": "gpus.csv",
        "PSU": "psus.csv",
        "Case": "cases.csv"
    }

    data = {}
    for key, file_name in files.items():
        file_path = os.path.join(data_dir, file_name)
        data[key] = pd.read_csv(file_path)

    return data

def save_final_configuration(selected_config, data):
        """
        Sauvegarde la configuration finale dans un fichier CSV, incluant toutes les colonnes possibles
        et en supprimant les doublons.
        """
        # Récupérer toutes les colonnes uniques de tous les composants
        all_columns = set()
        for df in data.values():
            all_columns.update(df.columns)

        # Assurer l'ordre souhaité des colonnes
        component_columns = ["Component", "id", "name"]  # Mettre "Component", "id" et "name" en premier
        other_columns = sorted(all_columns - set(component_columns))  # Trier les autres colonnes
        final_columns = component_columns + other_columns  # Fusionner dans l'ordre voulu

        # Construire la configuration sous forme de DataFrame
        config_list = []
        for component, component_id in selected_config.items():
            component_data = data[component].loc[data[component]["id"] == component_id].to_dict(orient="records")[0]

            # Ajouter toutes les colonnes manquantes avec "N/A"
            complete_data = {col: component_data.get(col, "N/A") for col in final_columns}
            complete_data["Component"] = component  # Ajouter une colonne pour identifier le type de composant
            config_list.append(complete_data)

        # Convertir en DataFrame et ordonner les colonnes correctement
        df = pd.DataFrame(config_list, columns=final_columns).drop_duplicates()

        # Sauvegarde dans un fichier CSV
        df.to_csv("final_configuration.csv", index=False)
        print("📂 La configuration finale a été sauvegardée dans 'final_configuration.csv'.")

# Printing DataFrames
if __name__ == "__main__":    
    # Load all data
    data = load_all_data()

    # Print data
    for key, df in data.items():
        print(f"{key}:\n", df, "\n")