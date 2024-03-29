import json
import os


class Filter:
    def __init__(self):
        self.key = []
        self.region = []


class MySqlSetting:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 3309
        self.user = 'admin'
        self.password = '123456'
        self.database = 'qcc'


class Setting:
    __instance = None

    @staticmethod
    def get():
        if Setting.__instance is None:
            Setting.__instance = Setting()
        return Setting.__instance

    def __init__(self):
        self.req_interval = 5
        self.error_wait_interval = 500
        self.next_interval = 24*3600
        self.max_page_index = 250
        self.unfulfilled_amount = 0
        self.unfulfilled_amount_max = 0
        self.collect_all = False
        self.cookie = []
        self.filter = Filter()
        self.mysql = MySqlSetting()
        self.__load()

    def reload(self):
        self.__load()

    def __load(self):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_file_path, r'configs\configs.json')
        with open(config_file_path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            root = json.loads(json_data)

            self.req_interval = root['req_interval']
            self.error_wait_interval = root['error_wait_interval']
            self.next_interval = root['next_interval'] * 3600
            self.max_page_index = root['max_page_index']
            self.unfulfilled_amount = root['unfulfilled_amount']
            self.unfulfilled_amount_max = root['unfulfilled_amount_max']
            self.collect_all = root['collect_all']
            self.cookie = root['cookie']

            self.filter.key.clear()
            for item in root['filter']['key']:
                self.filter.key.append(item)
            self.filter.region.clear()
            for item in root['filter']['region']:
                self.filter.region.append(item)

            self.mysql.host = root['mysql']['host']
            self.mysql.port = root['mysql']['port']
            self.mysql.user = root['mysql']['user']
            self.mysql.password = root['mysql']['password']
