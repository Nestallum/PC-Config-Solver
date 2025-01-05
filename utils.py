import os
import pandas as pd

def load_all_data(data_dir="data/"):
    """
    Loads all CSV files (CPUs, motherboards, RAM) as pandas DataFrames.
    Returns a dictionary with the data.
    """
    files = {
        "CPUs": "cpus.csv",
        "Motherboards": "motherboards.csv",
        "RAM": "ram.csv",
        "GPUs": "gpus.csv",
        "PSUs": "psus.csv",
        "Cases": "cases.csv"
    }

    data = {}
    for key, file_name in files.items():
        file_path = os.path.join(data_dir, file_name)
        data[key] = pd.read_csv(file_path)

    return data


# Example usage
if __name__ == "__main__":    
      # Load all data
    data = load_all_data()

    # Print data
    for key, df in data.items():
        print(f"{key}:\n", df, "\n")