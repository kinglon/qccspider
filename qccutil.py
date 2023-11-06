import hashlib
import hmac
import requests
import json
import datetime
from setting import Setting
from dataitem import Case
from dataitem import Company
from dataitem import ShareHolder


class QccUtil:
    def __init__(self):
        self.host = 'https://www.qcc.com'
        self.pid = ''
        self.tid = ''

    # 获取PID和TID
    def get_basic_info(self):
        try:
            url = self.host + '/web/search/advance?hasState=true&hasSearch=true&p=1'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Referer': self.host + '/web/search/advance?hasState=true&hasSearch=true&p=2'
            }
            self.__append_headers(headers)
            response = requests.get(url, headers=headers)
            if not response.ok:
                print("failed to get the basic info, error is ", response)
                return False
            else:
                html_content = response.text
                start_index = html_content.find("window.pid='") + len("window.pid='")
                end_index = html_content.find("'", start_index)
                self.pid = html_content[start_index:end_index]

                start_index = html_content.find("window.tid='") + len("window.tid='")
                end_index = html_content.find("'", start_index)
                self.tid = html_content[start_index:end_index]
                print("pid is {}, tid is {}".format(self.pid, self.tid))
                return True
        except requests.exceptions.RequestException as e:
            print("failed to get the basic info, error is ", e)
            return False

    # 按过滤条件搜索公司，返回 issuccess, companyid list, has next page
    def get_company_list(self, page_number, key, region):
        error_result = (False, [], False)
        try:
            uri = '/api/search/searchMulti'
            url = self.host + uri
            filter_string = '{"f":["VMN","N_SBKP2","ZX"],"r":[{"pr":"%s","cc":[%s]}]}' % (region['pr'], region['cc'])
            body = {'searchKey': key, 'pageIndex': page_number, 'pageSize': 20, 'filter': filter_string}
            body = json.dumps(body, ensure_ascii=False)
            body = body.replace(' ','')
            hash1, hash2 = QccUtil.calc_hash(uri, body, self.tid)
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Referer': self.host + '/web/search/advance?hasState=true&hasSearch=true',
                'X-Pid': self.pid,
                hash1: hash2
            }
            self.__append_headers(headers)
            response = requests.post(url, headers=headers, data=body.encode('utf-8'))
            if not response.ok:
                print("failed to get the company list info, error is ", response)
                return error_result
            else:
                company_list = []
                root = json.loads(response.content.decode('utf-8'))
                for company in root['Result']:
                    print(company['KeyNo'] + '   ' + company['Name'])
                    company_list.append(company['KeyNo'])
                total_records = root['Paging']['TotalRecords']
                page_size = root['Paging']['PageSize']
                page_index = root['Paging']['PageIndex']
                page_count = (total_records-1) // page_size + 1
                has_next_page = page_index < min(page_count, Setting.get().max_page_index)
                return True, company_list, has_next_page
        except requests.exceptions.RequestException as e:
            print("failed to get the company list, error is ", e)
            return error_result

    # 获取终本案件列表，返回 issuccess, case list, has next page
    def get_case_list(self, page_number, company_id):
        error_result = (False, [], False)
        try:
            uri = '/api/datalist/endexecutioncaselist?isNewAgg=true&keyNo={}&pageIndex={}'.format(company_id, page_number)
            url = self.host + uri
            hash1, hash2 = QccUtil.calc_hash(uri, '{}', self.tid)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Referer': self.host + '/csusong/34ecbc151474af17678d3fc817fcc956.html',
                'X-Pid': self.pid,
                hash1: hash2
            }
            self.__append_headers(headers)
            response = requests.get(url, headers=headers)
            if not response.ok:
                print("failed to get the case list info, error is ", response)
                return error_result
            else:
                case_list = []
                root = json.loads(response.content.decode('utf-8'))
                for case_json in root['data']:
                    if len(case_json['NameAndKeyNo']) == 0 or len(case_json['SqrInfo']) == 0:
                        continue
                    judgment_debtor: str = case_json['NameAndKeyNo'][0]['Name']
                    if judgment_debtor.find('有限公司') == -1:
                        continue
                    judgment_creditor: str = case_json['SqrInfo'][0]['Name']
                    if judgment_creditor.find('有限公司') == -1:
                        continue

                    case = Case()
                    case.case_id = case_json['CaseNo']
                    local_time = datetime.datetime.fromtimestamp(case_json['EndDate'])
                    case.finality_date = local_time.strftime("%Y-%m-%d")
                    case.executing_court = case_json['Court']
                    case.judgment_debtor = case_json['NameAndKeyNo'][0]['KeyNo']
                    case.judgment_creditor = case_json['SqrInfo'][0]['KeyNo']
                    case.unfulfilled_amount = case_json['FailureAct']
                    print('case: {}'.format(case.case_id))
                    case_list.append(case)

                has_next_page = False
                if 'total' in root['pageInfo']:
                    total_records = root['pageInfo']['total']
                    page_size = root['pageInfo']['pageSize']
                    page_index = root['pageInfo']['pageIndex']
                    page_count = (total_records - 1) // page_size + 1
                    has_next_page = page_index < page_count
                return True, case_list, has_next_page
        except requests.exceptions.RequestException as e:
            print("failed to get the case list, error is ", e)
            return error_result

    # 获取公司信息，返回 issuccess, company对象
    def get_company_info(self, company_id):
        error_result = (False, None)
        try:
            uri = '/firm/{}.html'.format(company_id)
            url = self.host + uri
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Referer': self.host + '/csusong/34ecbc151474af17678d3fc817fcc956.html',
            }
            self.__append_headers(headers)
            response = requests.get(url, headers=headers)
            if not response.ok:
                print("failed to get the company info info, error is ", response)
                return error_result
            else:
                html_content = response.content.decode('utf-8')
                start_index = html_content.find('window.__INITIAL_STATE__=') + len('window.__INITIAL_STATE__=')
                end_index = html_content.find('};', start_index) + 1
                json_string = html_content[start_index: end_index]
                root = json.loads(json_string)

                company = Company()
                company.company_id = company_id
                company.company_name = root['company']['companyDetail']['Name']
                company.phone_number = self.__get_company_phone_number(root)
                company.lr = self.__get_company_lr(root)
                company.region = self.__get_company_region(root)
                company.rc = root['company']['companyDetail']['RegistCapi']
                rec_cap = root['company']['companyDetail']['RecCap']
                if rec_cap is not None:
                    company.pc = rec_cap
                company.status = root['company']['companyDetail']['Status']
                partners = root['company']['companyDetail']['Partners']
                for partner in partners:
                    share_holder = ShareHolder()
                    share_holder.company_id = company_id
                    share_holder.name = partner['StockName']
                    share_holder.rate = partner['StockPercent']
                    company.share_holders.append(share_holder)

                return True, company
        except requests.exceptions.RequestException as e:
            print("failed to get the company information, error is ", e)
            return error_result

    @staticmethod
    def __encode_string(input_string):
        code_table = {0: 'W', 1: 'l', 2: 'k', 3: 'B', 4: 'Q', 5: 'g', 6: 'f', 7: 'i', 8: 'i', 9: 'r', 10: 'v', 11: '6',
                      12: 'A', 13: 'K', 14: 'N', 15: 'k', 16: '4', 17: 'L', 18: '1', 19: '8'}
        output_string = ""
        for ch in input_string:
            pos = ord(ch) % 20
            output_string += code_table[pos]
        return output_string

    @staticmethod
    def calc_hash(uri, body, tid):
        uri = uri.lower()
        body = body.lower()
        uri_encode = QccUtil.__encode_string(uri + uri)
        message = uri + body
        hmac_digest = hmac.new(uri_encode.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha512).digest()
        hmac_digest = hmac_digest.hex()
        hash1 = hmac_digest[8:28]

        message = uri + 'pathString' + body + tid
        hmac_digest = hmac.new(uri_encode.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha512).digest()
        hash2 = hmac_digest.hex()
        return hash1, hash2

    def __append_headers(self, headers):
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        headers['Cookie'] = ''
        for key, value in Setting.get().cookie.items():
            headers['Cookie'] += '{}={};'.format(key, value)
        headers['Origin'] = self.host
        headers['Sec-Ch-Ua-Platform'] = '"Windows"'
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        return headers

    # 根据名字在JSON中查找节点
    @staticmethod
    def find_node_by_name(name, data):
        if isinstance(data, dict):
            if name in data:
                return data[name]
            for value in data.values():
                result = QccUtil.find_node_by_name(name, value)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = QccUtil.find_node_by_name(name, item)
                if result is not None:
                    return result

        return None

    @staticmethod
    def __is_mobile_number(phone_number):
        if len(phone_number) == 11 and phone_number[0] == '1':
            return True
        return False

    def __get_company_phone_number(self, root):
        phone_list = []
        contact_info_node = QccUtil.find_node_by_name('ContactInfo', root)
        phone = contact_info_node['PhoneNumber']
        if QccUtil.__is_mobile_number(phone):
            phone_list.append(phone)
        his_tel_list_node = QccUtil.find_node_by_name('HisTelList', root)
        for item in his_tel_list_node:
            phone = item['Tel']
            if self.__is_mobile_number(phone):
                phone_list.append(phone)
        return str(phone_list)

    # 获取公司的法定代表人
    @staticmethod
    def __get_company_lr(root):
        lr = []
        oper_list_node = root['company']['companyDetail']['MultipleOper']['OperList']
        for item in oper_list_node:
            lr.append(item['Name'])
        return str(lr)

    # 获取公司所属地区
    @staticmethod
    def __get_company_region(root):
        area = root['company']['companyDetail']['Area']
        return area['Province'] + area['City'] + area['County']


def test():
    uri = '/api/datalist/endexecutioncaselist?isnewagg=true&keyno=34ecbc151474af17678d3fc817fcc956&pageindex=1'
    body = '{}'
    tid = '8870f3fecc389da61e700132ffbb6365'
    qcc_util = QccUtil()
    hash1, hash2 = qcc_util.calc_hash(uri, body, tid)
    print(hash1)
    print(hash2)


if __name__ == "__main__":
    test()
