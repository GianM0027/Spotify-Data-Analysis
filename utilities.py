import json
import os
import shutil
import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
from constants import *


def get_username_from_data(account_data):
    identity = account_data.get("Identity", None)

    if isinstance(identity, dict):
        username = identity.get("displayName", None)
    else:
        username = None

    return username

def find_account_and_history_data(data_dir):
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

    username = get_username_from_data(account_data)
    print(f"All good {username}! Your data has been extracted correctly. Here are all the files that Spotify provided:\n")

    print(f"Your account data contains the following entries:\n {list(account_data.keys())}")
    print(f"\nYour history data contains the following entries:\n {list(history_data.keys())}")

    music_history = {key: data for key, data in history_data.items() if "Audio" in key}
    video_history = {key: data for key, data in history_data.items() if "Video" in key}

    return account_data, music_history, video_history




def print_most_listened_to(df: pd.DataFrame, k: int = 50):
    """
    This function takes a DataFrame with columns 'ms_played', 'master_metadata_track_name', and
    'master_metadata_album_artist_name' and extracts relevant information. It calculates the total
    listening time in minutes and identifies the most listened-to songs based on the provided 'most_listened'
    parameter. The resulting DataFrame is sorted in descending order of listening time.
    Note: The 'ms_played' column is expected to represent the duration of each song in milliseconds.

    :param df: dataframe of songs in JSON format
    :param n: The number of top songs to display. Defaults to 50.

    :return: A tuple with 2 elements:
                1) A dataFrame containing information about the most listened-to songs.
                2) The total listening time in minutes across all songs.
    """

    ms_played = "ms_played"
    track_name = "master_metadata_track_name"
    author = "master_metadata_album_artist_name"

    df = df.loc[:, [ms_played, track_name, author]]

    tot_minutes = round((df.loc[:, ms_played].sum() / 1000) / 60)  #to listened minutes

    grouped_df = df.groupby([track_name, author])[ms_played].sum().reset_index()

    # If you want to keep only unique songs with total listening time
    unique_songs_df = grouped_df.drop_duplicates(subset=track_name)

    unique_songs_df = unique_songs_df.sort_values(by=ms_played, ascending=False)
    unique_songs_df = unique_songs_df.iloc[:k, :]
    unique_songs_df[ms_played] = unique_songs_df[ms_played].apply(lambda x: (x / 1000) / 60)

    column_mapping = {ms_played: "minutes played", track_name: "Song", author: "Author"}
    unique_songs_df.rename(columns=column_mapping, inplace=True)
    unique_songs_df.index = range(1, k + 1)

    return unique_songs_df, tot_minutes





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
