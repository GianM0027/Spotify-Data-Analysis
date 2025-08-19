import warnings
import pandas as pd


class HistoryDataManager:
    def __init__(self, history_data):
        self._history_data = self._history_data_to_df(history_data)

    def __call__(self, *args, **kwargs):
        return self._history_data

    def __getattr__(self, name):
        return getattr(self._history_data, name)

    def __getitem__(self, key):
        return self._history_data[key]

    def __len__(self):
        return len(self._history_data)

    def __iter__(self):
        return iter(self._history_data)

    def __repr__(self):
        return repr(self._history_data)

    def _history_data_to_df(self, history_data):
        json_data = []
        for music_file in history_data.keys():
            json_data.extend(history_data[music_file])

        if len(json_data) == 0:
            warnings.warn("It seems like you have not listened to any songs")

        return self._create_extended_df(json_data)

    def _create_extended_df(self, json_data):
        """
        Creates a dataframe from a list of data (songs/videos) in Spotify JSON format.
        """
        df = pd.DataFrame(json_data)

        # Drop columns where all values are the same
        df = df.drop(columns=df.columns[df.nunique() == 1])

        # Extract date and time from ts column
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
            df['date'] = df['ts'].dt.date
            df['time'] = df['ts'].dt.time
            # Reorder
            df = df[['date', 'time'] + [c for c in df.columns if c not in ('ts', 'date', 'time')]]

        return df
