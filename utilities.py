import pandas as pd
import numpy as np

import plotly.express as px

from tqdm import tqdm

from datetime import datetime



def create_extended_df(jData):
    """
    It creates a dataframe from a list of data (songs/videos) in spotify JSON format

    :param jData: np.darray of songs in JSON format
    :return: dataframe with numerical indexes where each row represent a song (with repetitions), each column is
                an information regarding that song
    """

    extended_df = pd.DataFrame(index=np.arange(len(jData)), columns=jData[0].keys())

    # creating initial df
    for column in tqdm(extended_df.columns, desc="From JSON to DataFrame"):
        for index, value in extended_df[column].items():
            extended_df.at[index, column] = jData[index].get(column)

    #drop the column if all the rows are equal (no information)
    for column in tqdm(extended_df.columns, desc="Removing columns without relevant information"):
        if extended_df[column].nunique() == 1:
            extended_df = extended_df.drop(column, axis=1)

    #create two columns for date and time
    times = np.array([])
    for i in tqdm(range(len(extended_df)), desc="Formatting Dates and Time"):
        times = np.append(times, extended_df.loc[i, "ts"][11:-1])
        extended_df.loc[i, "ts"] = extended_df.loc[i, "ts"][:10]
    extended_df.insert(1, "time", times)

    return extended_df

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

    return start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"), (end_date-start_date).days

def print_most_listened_to(df: pd.DataFrame, most_listened: int = 50):
    """
    This function takes a DataFrame with columns 'ms_played', 'master_metadata_track_name', and
    'master_metadata_album_artist_name' and extracts relevant information. It calculates the total
    listening time in minutes and identifies the most listened-to songs based on the provided 'most_listened'
    parameter. The resulting DataFrame is sorted in descending order of listening time.
    Note: The 'ms_played' column is expected to represent the duration of each song in milliseconds.

    :param df: dataframe of songs in JSON format
    :param most_listened: The number of top songs to display. Defaults to 50.

    :return: A tuple with 2 elements:
                1) A dataFrame containing information about the most listened-to songs.
                2) The total listening time in minutes across all songs.
    """

    ms_played = "ms_played"
    track_name = "master_metadata_track_name"
    author = "master_metadata_album_artist_name"

    df = df.loc[:, [ms_played, track_name, author]]

    tot_minutes = round((df.loc[:,ms_played].sum()/1000)/60) #to listened minutes

    grouped_df = df.groupby([track_name, author])[ms_played].sum().reset_index()

    # If you want to keep only unique songs with total listening time
    unique_songs_df = grouped_df.drop_duplicates(subset=track_name)

    unique_songs_df = unique_songs_df.sort_values(by=ms_played, ascending=False)
    unique_songs_df = unique_songs_df.iloc[:most_listened, :]
    unique_songs_df[ms_played] = unique_songs_df[ms_played].apply(lambda x: (x/1000)/60)

    column_mapping = {ms_played: "minutes played", track_name: "Song", author: "Author"}
    unique_songs_df.rename(columns=column_mapping, inplace=True)
    unique_songs_df.index = range(1,most_listened+1)

    return unique_songs_df, tot_minutes


def plot_months_minutes(df: pd.DataFrame):
    """
    Plots a bar chart representing the total minutes of music listened for each month over multiple years.
    This function takes a DataFrame with timestamp and duration information and generates a bar chart using Plotly Express.
    The chart displays the total minutes of music listened for each month over multiple years. The input DataFrame is expected
    to have columns 'ts' representing the timestamp and 'ms_played' representing the duration of music played in milliseconds.
    
    Note: The timestamp 'ts' is expected to be in the format '%Y-%m-%d'. 
    The function utilizes Plotly Express for creating interactive plots with html. 

    :param df: The input DataFrame containing columns 'ts' (timestamp) and 'ms_played' (duration in milliseconds).
    :return: None
    """

    ms_played = "ms_played"
    d = "ts"
    format_str = "%Y-%m-%d"
    df = df.loc[:, [d, ms_played]]

    list_dates_minutes = {}

    for index, row in df.iterrows():
        date = datetime.strptime(row[d], format_str)
        minutes = (row[ms_played]/1000)/60

        if list_dates_minutes.get(date.year, -1) == -1:
            list_dates_minutes[date.year] = {date.month: minutes}
        elif list_dates_minutes[date.year].get(date.month, -1) == -1:
            list_dates_minutes[date.year][date.month] = minutes
        else:
            list_dates_minutes[date.year][date.month] += minutes

        for year, months in list_dates_minutes.items():
            list_dates_minutes[year] = {key: months[key] for key in sorted(months.keys())}

        for months in list_dates_minutes.values():
            for i in range(1,13):
                if months.get(i, -1) == -1:
                    months[i] = 0

    df = pd.DataFrame.from_dict(list_dates_minutes, orient="index")

    df_melted = df.reset_index().melt(id_vars='index', var_name='Month', value_name='Minutes').rename(columns={'index': 'Year'})

    # Create a new column combining year and month
    df_melted['YearMonth'] = df_melted['Year'].astype(str) + '-' + df_melted['Month'].astype(str)

    # Create the histogram using Plotly Express
    fig = px.bar(df_melted, x='YearMonth', y='Minutes',
                 labels={'YearMonth': 'Month-Year ', 'Minutes': 'Minutes of Music Listened '},
                 title='Minutes of Music Listened by Month',
                 color="Year")

    fig.show()