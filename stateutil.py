import json
import os


class CompanyPageIndex:
    def __init__(self):
        self.filter_key = ''
        self.filter_region = {}
        self.page_index = 0


class StateUtil:
    __instance = None

    @staticmethod
    def get():
        if StateUtil.__instance is None:
            StateUtil.__instance = StateUtil()
        return StateUtil.__instance

    def __init__(self):
        self.company_page_index = []
        self.__load()

    def __load(self):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_file_path, r'configs\states.json')
        with open(config_file_path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            root = json.loads(json_data)

            for item in root['company_list']:
                page_index = CompanyPageIndex()
                page_index.filter_key = item['filter_key']
                page_index.filter_region = item['filter_region']
                page_index.page_index = item['page_index']
                self.company_page_index.append(page_index)

    def save(self):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_file_path, r'configs\states.json')
        with open(config_file_path, "w", encoding='utf-8') as file:
            root = {'company_list': []}
            for item in self.company_page_index:
                company_list_item = {'filter_key': item.filter_key, 'filter_region': item.filter_region, 'page_index': item.page_index}
                root['company_list'].append(company_list_item)
            json.dump(root, file)

    def get_page_index(self, filter_key, filter_region):
        for item in self.company_page_index:
            if item.filter_key == filter_key and item.filter_region['pr'] == filter_region['pr'] and item.filter_region['cc'] == filter_region['cc']:
                return item.page_index
        return 0

    def set_page_index(self, filter_key, filter_region, page_index):
        for item in self.company_page_index:
            if item.filter_key == filter_key and item.filter_region['pr'] == filter_region['pr'] and item.filter_region['cc'] == filter_region['cc']:
                item.page_index = page_index
                self.save()
                return

        new_page_index = CompanyPageIndex()
        new_page_index.page_index = page_index
        new_page_index.filter_key = filter_key
        new_page_index.filter_region = filter_region
        self.company_page_index.append(new_page_index)
        self.save()

    def reset(self):
        self.company_page_index.clear()
        self.save()