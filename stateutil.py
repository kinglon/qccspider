import json
import os


class StateItem:
    def __init__(self):
        self.filter_key = ''
        self.filter_region = {"pr": "", "cc": ""}
        self.current_company_page_index = 1
        self.current_company_id = ""
        self.current_case_page_index = 1
        self.current_case_id = ""

    def __str__(self):
        return 'the state is filter key: {}, filter region: {}, company page index: {}, company id: {}, case page index: {}, case id: {}'\
                .format(self.filter_key, self.filter_region, self.current_company_page_index, self.current_company_id,
                        self.current_case_page_index, self.current_case_id)

    def set_current_company_page_index(self, page_index):
        self.current_company_page_index = page_index
        self.current_company_id = ''
        self.current_case_page_index = 1
        self.current_case_id = ""

    def set_current_company_id(self, company_id):
        self.current_company_id = company_id
        self.current_case_page_index = 1
        self.current_case_id = ""

    def set_current_case_page_index(self, page_index):
        self.current_case_page_index = page_index
        self.current_case_id = ""


class StateUtil:
    __instance = None

    @staticmethod
    def get():
        if StateUtil.__instance is None:
            StateUtil.__instance = StateUtil()
        return StateUtil.__instance

    def __init__(self):
        self.states = []
        self.__load()

    def __load(self):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_file_path, r'configs\states.json')
        with open(config_file_path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            root = json.loads(json_data)

            for item in root['state']:
                state_item = StateItem()
                state_item.filter_key = item['filter_key']
                if state_item.filter_key == '':
                    continue
                state_item.filter_region = item['filter_region']
                state_item.current_company_page_index = item['current_company_page_index']
                state_item.current_company_id = item['current_company_id']
                state_item.current_case_page_index = item['current_case_page_index']
                state_item.current_case_id = item['current_case_id']
                self.states.append(state_item)

    def save(self):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_file_path, r'configs\states.json')
        with open(config_file_path, "w", encoding='utf-8') as file:
            root = {'state': []}
            for item in self.states:
                state_item = {'filter_key': item.filter_key,
                              'filter_region': item.filter_region,
                              'current_company_page_index': item.current_company_page_index,
                              'current_company_id': item.current_company_id,
                              'current_case_page_index': item.current_case_page_index,
                              'current_case_id': item.current_case_id}
                root['state'].append(state_item)
            json.dump(root, file, indent=4)

    def get_state(self, filter_key, filter_region):
        for item in self.states:
            if item.filter_key == filter_key and item.filter_region['pr'] == filter_region['pr'] and item.filter_region['cc'] == filter_region['cc']:
                return item

        state = StateItem()
        state.filter_key = filter_key
        state.filter_region['pr'] = filter_region['pr']
        state.filter_region['cc'] = filter_region['cc']
        return state

    def save_state(self, state):
        for item in self.states:
            if item.filter_key == state.filter_key and item.filter_region['pr'] == state.filter_region['pr']\
                    and item.filter_region['cc'] == state.filter_region['cc']:
                self.states.remove(item)
                break

        self.states.append(state)
        self.save()

    def reset(self):
        self.states.clear()
        self.save()
