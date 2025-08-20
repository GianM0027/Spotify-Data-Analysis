import json
import os
import shutil
import pandas as pd
import zipfile
from datetime import datetime
import matplotlib.pyplot as plt
from constants import *

def find_account_and_history_data(data_dir):
    #todo: handle case where account data is not loaded and return None

    # if data directory does not exist
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
        raise FileNotFoundError(
            f"Data directory was not found and has been created. "
            f"Please place your .zip files in {data_dir}"
        )

    # if data directory does exist
    temp_working_directory = os.path.join(data_dir, "temp")
    os.makedirs(temp_working_directory, exist_ok=True)

    # extract zip files in a temporary folder
    for file in os.listdir(data_dir):
        if file.endswith('.zip'):
            filename = os.path.join(data_dir, file)
            with zipfile.ZipFile(filename, 'r') as zip_file:
                zip_file.extractall(path=temp_working_directory)

    # populate the two dictionaries
    account_data, history_data = {}, {}

    for folder, target_dict in [
        (SPOTIFY_ACCOUNT_DATA_FILE_NAME, account_data),
        (SPOTIFY_STREAMING_FILE_NAME, history_data)
    ]:
        folder_path = os.path.join(temp_working_directory, folder)
        if not os.path.exists(folder_path):
            continue
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                file_path = os.path.join(folder_path, file)
                file_name = file.split('.json')[0]
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    target_dict[file_name] = json.load(json_file)

    # delete temporary folder
    shutil.rmtree(temp_working_directory)

    print(f"All good! Your data has been extracted correctly. Here are all the files that Spotify provided:\n")

    print(f"Your account data contains the following entries:\n {list(account_data.keys())}")
    print(f"\nYour history data contains the following entries:\n {list(history_data.keys())}")

    music_history = {key: data for key, data in history_data.items() if "Audio" in key}
    video_history = {key: data for key, data in history_data.items() if "Video" in key}

    return account_data, music_history, video_history

def plot_monthly_minutes(df: pd.DataFrame, year: int):
    """
    Plots a bar chart of total minutes of music listened for each month of a specific year.
    """
    ms_played = "ms_played"
    d = "ts"
    format_str = "%Y-%m-%d"

    # Convert timestamps and compute minutes
    df[d] = pd.to_datetime(df[d], format=format_str)
    df['minutes'] = df[ms_played] / 1000 / 60

    # Filter by year and aggregate by month
    monthly = df[df[d].dt.year == year].groupby(df[d].dt.month)['minutes'].sum()
    months = [datetime(1900, m, 1).strftime('%b') for m in range(1, 13)]
    values = [monthly.get(m, 0) for m in range(1, 13)]

    # Plot
    plt.figure(figsize=(10,6))
    plt.bar(months, values, color='coral')
    plt.xlabel("Month")
    plt.ylabel("Minutes of Music Listened")
    plt.title(f"Minutes of Music Listened in {year}")
    plt.tight_layout()
    plt.grid(alpha=0.3)
    plt.show()
