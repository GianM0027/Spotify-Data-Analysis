import pandas as pd
import numpy as np

import plotly.express as px

from tqdm import tqdm

from datetime import datetime



def create_extended_df(jsongs):
    """
    It creates a dataframe from a list of songs in spotify JSON format

    :param jsongs: np.darray of songs in JSON format
    :return: dataframe with numerical indexes where each row represent a song (with repetitions), each column is
                an information regarding that song
    """

    extended_df = pd.DataFrame(index=np.arange(len(jsongs)), columns=jsongs[0].keys())

    # creating initial df
    for column in tqdm(extended_df.columns, desc="From JSON to DataFrame"):
        for index, value in extended_df[column].items():
            extended_df.at[index, column] = jsongs[index].get(column)

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


def create_df_no_duplicates(extended_df):

    df_no_duplicates = extended_df.drop_duplicates(subset="master_metadata_track_name") # removing duplicates from extended dataframe

    df_no_duplicates = df_no_duplicates.set_index(df_no_duplicates.loc[:, "master_metadata_track_name"]) # indexes of the new df are the name of the songs

    df_no_duplicates = df_no_duplicates.drop("master_metadata_track_name", axis=1) # drop the old column with the name of the songs

    # add a column for counting the occurrences and drop the useless columns

    return df_no_duplicates


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


def print_most_listened(df, most_listened = 50):
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

    return (unique_songs_df), tot_minutes


def plot_months_minutes(df):
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