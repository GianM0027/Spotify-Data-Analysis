from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from data_managers.history_data_manager import HistoryDataManager


class AudioHistory(HistoryDataManager):
    def __init__(self, history_data):
        super().__init__(history_data)

        self.date_key = "date"
        self.milliseconds_played_key = "ms_played"
        self.track_name_key = "master_metadata_track_name"
        self.author_key = "master_metadata_album_artist_name"

    def listening_period(self):
        """
        It finds the date of the first and last listened song in the dataframe

        :return: start date, end date, number of days in between
        """

        start_date = self[self.date_key].min()
        end_date = self[self.date_key].max()

        return start_date, end_date, (end_date - start_date).days

    def plot_yearly_minutes(self):
        """
        Plots a bar chart of total minutes of music listened per year.
        """
        yearly_minutes = self.copy()
        yearly_minutes[self.date_key] = pd.to_datetime(yearly_minutes[self.date_key], errors='coerce')
        yearly_minutes['minutes'] = self[self.milliseconds_played_key] / 1000 / 60
        yearly = yearly_minutes.groupby(yearly_minutes[self.date_key].dt.year)['minutes'].sum()

        plt.figure(figsize=(10, 6))
        plt.bar(yearly.index.astype(str), yearly.values, color='skyblue')
        plt.xlabel("Year")
        plt.ylabel("Minutes of Music Listened")
        plt.title("Total Minutes of Music Listened per Year")
        plt.tight_layout()
        plt.grid(alpha=0.3)
        plt.show()

    def plot_monthly_minutes(self, year: int):
        """
        Plots a bar chart of total minutes of music listened for each month of a specific year.
        """
        df = self._history_data.copy()  # work on a copy
        df[self.date_key] = pd.to_datetime(df[self.date_key], errors='coerce')  # ensure datetime
        df['minutes'] = df[self.milliseconds_played_key] / 1000 / 60

        # Filter by year and aggregate by month
        monthly = df[df[self.date_key].dt.year == year].groupby(df[self.date_key].dt.month)['minutes'].sum()

        # Prepare month labels and values
        months = [datetime(1900, m, 1).strftime('%b') for m in range(1, 13)]
        values = [monthly.get(m, 0) for m in range(1, 13)]

        # Plot
        plt.figure(figsize=(10, 6))
        plt.bar(months, values, color='coral')
        plt.xlabel("Month")
        plt.ylabel("Minutes of Music Listened")
        plt.title(f"Minutes of Music Listened in {year}")
        plt.tight_layout()
        plt.grid(alpha=0.3)
        plt.show()

    def print_listening_stats(self):
        start_date, end_date, days = self.listening_period()

        tot_songs = len(self)
        unique_songs = len(self.drop_duplicates(subset="master_metadata_track_name"))

        print(f"Between {start_date} and {end_date} ({days} days) you listened to:")
        print(f"- {tot_songs} songs (in total)")
        print(f"- {unique_songs} different songs")

    def filter_data_by_time(self, time_start: datetime = None, time_end: datetime = None):
        df = self.copy()
        df[self.date_key] = pd.to_datetime(df[self.date_key], errors="coerce")

        # time_start is None, time_end is None -> return entire dataframe
        if not time_start and not time_end:
            return df

        # time_start is date, time_end is none -> return self.copy con date > time_start
        elif time_start and not time_end:
            return df[df[self.date_key] > time_start]

        # time_start is None, time_end is date -> return self.copy con date < time_end
        elif not time_start and time_end:
            return df[df[self.date_key] < time_end]

        # time_start is date, time_end is date -> return self.copy con time_start < date < time_end
        elif time_start and time_end:
            return df[(df[self.date_key] < time_end) & (df[self.date_key] > time_start)]

        else:
            raise RuntimeError("Error when filtering data by time!")


    def print_most_listened_to(self, time_start: datetime = None, time_end: datetime = None):
        # retrieve data in the interval required
        filtered_df = self.filter_data_by_time(time_start, time_end)

        df_to_display = filtered_df.loc[:, [self.milliseconds_played_key, self.track_name_key, self.author_key]]

        tot_minutes = round((df_to_display.loc[:, self.milliseconds_played_key].sum() / 1000) / 60)

        grouped = df_to_display.groupby([self.track_name_key, self.author_key])
        summed = grouped[self.milliseconds_played_key].sum()
        grouped_df = summed.reset_index()

        # Only unique songs with total listening time
        unique_songs_df = grouped_df.drop_duplicates(subset=self.track_name_key)

        unique_songs_df = unique_songs_df.sort_values(by=self.milliseconds_played_key, ascending=False)
        unique_songs_df[self.milliseconds_played_key] = unique_songs_df[self.milliseconds_played_key].apply(lambda x: (x / 1000) / 60)

        column_mapping = {self.milliseconds_played_key: "minutes played",
                          self.track_name_key: "Song",
                          self.author_key: "Author"}
        unique_songs_df.rename(columns=column_mapping, inplace=True)
        unique_songs_df.reset_index(inplace=True)
        unique_songs_df.drop("index", axis=1, inplace=True)

        return unique_songs_df, tot_minutes