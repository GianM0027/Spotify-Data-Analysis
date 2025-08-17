import json
import os
import shutil

import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
from tqdm import tqdm
from datetime import datetime
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

def create_extended_df(jData):
    """
    Creates a dataframe from a list of data (songs/videos) in Spotify JSON format.

    Parameters:
    jData: List or array of songs in JSON format

    Returns:
    DataFrame with each row representing a song (with repetitions), each column is information about that song
    """
    # Convert the JSON data to DataFrame directly
    df = pd.DataFrame(jData)

    # Remove columns where all values are the same
    nunique = df.nunique()
    cols_to_drop = nunique[nunique == 1].index
    df = df.drop(columns=cols_to_drop)

    # Extract date and time from timestamp column
    if 'ts' in df.columns:
        df['time'] = df['ts'].str[11:-1]  # Extract time part
        df['ts'] = df['ts'].str[:10]  # Keep only date part

        # Reorder columns to put time right after ts
        cols = df.columns.tolist()
        ts_idx = cols.index('ts')
        cols.remove('time')
        cols.insert(ts_idx + 1, 'time')
        df = df[cols]

    return df


def listening_period(dates):
    """
    It finds the date of the first and last listened song in the dataframe

    :param dates: list of dates
    :return: start date, end date, number of days in between
    """
    start_date = dates[0]
    end_date = dates[0]

    for date in dates:
        if start_date > date:
            start_date = date
        if end_date < date:
            end_date = date

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    return start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"), (end_date - start_date).days


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


def plot_months_minutes(df: pd.DataFrame):
    """
    Plots a bar chart representing the total minutes of music listened for each month over multiple years.
    """

    ms_played = "ms_played"
    d = "ts"
    format_str = "%Y-%m-%d"
    df = df.loc[:, [d, ms_played]]

    list_dates_minutes = {}

    for index, row in df.iterrows():
        date = datetime.strptime(row[d], format_str)
        minutes = (row[ms_played] / 1000) / 60

        if list_dates_minutes.get(date.year, -1) == -1:
            list_dates_minutes[date.year] = {date.month: minutes}
        elif list_dates_minutes[date.year].get(date.month, -1) == -1:
            list_dates_minutes[date.year][date.month] = minutes
        else:
            list_dates_minutes[date.year][date.month] += minutes

        for year, months in list_dates_minutes.items():
            list_dates_minutes[year] = {key: months[key] for key in sorted(months.keys())}

        for months in list_dates_minutes.values():
            for i in range(1, 13):
                if months.get(i, -1) == -1:
                    months[i] = 0

    df = pd.DataFrame.from_dict(list_dates_minutes, orient="index")

    df_melted = df.reset_index().melt(
        id_vars='index',
        var_name='Month',
        value_name='Minutes'
    ).rename(columns={'index': 'Year'})

    # Ensure Year is treated as categorical → gives a discrete legend
    df_melted['Year'] = df_melted['Year'].astype(str)

    # Create a new column combining year and month
    df_melted['YearMonth'] = df_melted['Year'] + '-' + df_melted['Month'].astype(str)

    # Create the bar chart with discrete legend
    fig = px.bar(
        df_melted,
        x='YearMonth',
        y='Minutes',
        labels={'YearMonth': 'Month-Year', 'Minutes': 'Minutes of Music Listened'},
        title='Minutes of Music Listened by Month',
        color="Year",   # categorical → discrete legend
        color_discrete_sequence=px.colors.qualitative.Set2  # optional: nicer colors
    )

    fig.show()
