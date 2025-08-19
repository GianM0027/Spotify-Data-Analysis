from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from data_managers.history_data_manager import HistoryDataManager


class AudioHistory(HistoryDataManager):
    def __init__(self, history_data):
        super().__init__(history_data)

    def listening_period(self):
        """
        It finds the date of the first and last listened song in the dataframe

        :return: start date, end date, number of days in between
        """

        start_date = self["date"].min()
        end_date = self["date"].max()

        return start_date, end_date, (end_date - start_date).days

    def plot_yearly_minutes(self):
        """
        Plots a bar chart of total minutes of music listened per year.
        """
        yearly_minutes = self.copy()
        yearly_minutes['date'] = pd.to_datetime(yearly_minutes['date'], errors='coerce')
        yearly_minutes['minutes'] = self['ms_played'] / 1000 / 60
        yearly = yearly_minutes.groupby(yearly_minutes['date'].dt.year)['minutes'].sum()

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
        df['date'] = pd.to_datetime(df['date'], errors='coerce')  # ensure datetime
        df['minutes'] = df['ms_played'] / 1000 / 60

        # Filter by year and aggregate by month
        monthly = df[df['date'].dt.year == year].groupby(df['date'].dt.month)['minutes'].sum()

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

