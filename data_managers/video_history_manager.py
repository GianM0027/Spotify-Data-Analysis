from data_managers.history_data_manager import HistoryDataManager


class VideoHistory(HistoryDataManager):
    def __init__(self, history_data):
        super().__init__(history_data)