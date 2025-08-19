from datetime import datetime


class AccountData(dict):
    def __init__(self, account_data=None, **kwargs):
        if account_data is None:
            account_data = {}
        super().__init__(account_data, **kwargs)

        # file names
        self._identity_file_name = "Identity"
        self._playlists_file_name = "Playlist1"
        self._user_data_file_name = "Userdata"

        # key names
        self._username_key = "displayName"                      # in self._identity_file_name
        self._first_name_key = "firstName"                      # in self._user_data_file_name
        self._last_name_key = "lastName"                        # in self._user_data_file_name
        self._account_creation_time_key = "creationTime"        # in self._user_data_file_name
        self._birthday_key = "birthdate"                        # in self._user_data_file_name
        self._playlists_key = "playlists"                       # in self._playlists_file_name

    def get_voice_from_file(self, file_name, key):
        identity = self.get(file_name, {})

        if identity is None:
            raise FileNotFoundError(f"Attention! File '{file_name}' not found!")

        value = identity.get(key, None)
        return value

    def print_account_info(self):
        username = self.get_voice_from_file(self._identity_file_name, self._username_key)
        name = self.get_voice_from_file(self._user_data_file_name, self._first_name_key)
        surname = self.get_voice_from_file(self._user_data_file_name, self._last_name_key)
        user_reference = f"{name} {surname}" if name and surname else username

        account_creation_data = self.get_voice_from_file(self._user_data_file_name, self._account_creation_time_key)
        account_creation_data = self._string_to_date(account_creation_data)
        user_birthday = self.get_voice_from_file(self._user_data_file_name, self._birthday_key)
        user_birthday = self._string_to_date(user_birthday)
        birthday_greetings = self._check_if_user_birthday(user_birthday)

        playlist_list = self.get_voice_from_file(self._playlists_file_name, self._playlists_key)

        # USER INFO
        print("#"*50, end="")
        print(f"\nHello {user_reference}! Here are some info about you and your account")
        print(f" - You created this account on {account_creation_data.strftime('%d-%m-%Y')}.")
        print(f" - Your birthday is on {user_birthday.strftime('%d-%m-%Y')}. {birthday_greetings}\n")

        # PLAYLIST INFO
        print("#"*50, end="")
        if len(playlist_list) > 0:
            print("\nIt looks like you created some playlists:")

            for playlist in playlist_list:
                description = "\t-\t "+ playlist['description'] if playlist['description'] else ""
                print(f"- {playlist['name']} {description}")
        else:
            print("\nIt looks like you did not create any playlists. Very bad :(")


    def _string_to_date(self, string_date):
        return datetime.strptime(string_date, "%Y-%m-%d").date()

    def _check_if_user_birthday(self, user_birthday):
        greetings = "Oh wait... It's today! Well, happy birthday then!!!🎉🎉🎉"

        if datetime.now().date().month == user_birthday.month and datetime.now().date().day == user_birthday.day:
            return greetings

        return ""
