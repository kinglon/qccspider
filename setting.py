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

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    @staticmethod
    def get():
        return Setting.__instance

    def __init__(self):
        self.req_interval = 5
        self.max_page_index = 250
        self.cookie = {}
        self.filter = Filter()
        self.mysql = MySqlSetting()
        self.__load()

    def __load(self):
        current_file_path = os.path.abspath(__file__)
        config_file_path = os.path.join(current_file_path, r'configs\configs.json')
        with open(config_file_path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            root = json.loads(json_data)

            self.req_interval = root['req_interval']
            self.max_page_index = root['max_page_index']

            self.cookie['acw_tc'] = root['cookie']['acw_tc']
            self.cookie['QCCSESSID'] = root['cookie']['QCCSESSID']
            self.cookie['qcc_did'] = root['cookie']['qcc_did']

            for item in root['filter']['key']:
                self.filter.key.append(item)
            for item in root['filter']['region']:
                self.filter.region.append(item)

            self.mysql.host = root['mysql']['host']
            self.mysql.port = root['mysql']['port']
            self.mysql.admin = root['mysql']['admin']
            self.mysql.password = root['mysql']['password']
