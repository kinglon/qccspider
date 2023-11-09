from setting import Setting
from qccutil import QccUtil
from mysqlutil import MysqlUtil
from logutil import LogUtil
from stateutil import StateUtil
import time


def ignore_case(case_id, company):
    if company.status.find('在营') == -1 and company.status.find('开业') == -1 and company.status.find('在册') == -1:
        print('{} is ignored, the status of the company is {}'.format(case_id, company.status))
        return True

    all_company = True
    for item in company.share_holders:
        if item.name.find('公司') == -1:
            all_company = False
            break
    if all_company:
        print('{} is ignored, all share holders of {} are companies'.format(case_id, company.company_name))
        return True

    return False


def main():
    if not MysqlUtil.connect():
        return False

    if not MysqlUtil.create_table_if_need():
        return False

    collect_all = Setting.get().collect_all
    filter_keys = Setting.get().filter.key
    filter_regions = Setting.get().filter.region
    for filter_key in filter_keys:
        for filter_region in filter_regions:
            print('filter key is {}, filter region is {}'.format(filter_key, filter_region))

            qcc_util = QccUtil()
            time.sleep(Setting.get().req_interval)
            if not qcc_util.get_basic_info():
                return False

            company_page_number = StateUtil.get().get_page_index(filter_key, filter_region)
            print('continue to collect data from page {}'.format(company_page_number))

            has_next_company_page = True
            while has_next_company_page:
                StateUtil.get().set_page_index(filter_key, filter_region, company_page_number)
                time.sleep(Setting.get().req_interval)
                company_page_number += 1
                is_success, company_list, has_next_company_page = qcc_util.get_company_list(
                    company_page_number, filter_key, filter_region)
                if not is_success:
                    print('retry to get the company list after {} seconds'.format(Setting.get().error_wait_interval))
                    time.sleep(Setting.get().error_wait_interval)
                    has_next_company_page = True
                    company_page_number -= 1
                    continue

                for company in company_list:
                    has_next_case_page = True
                    case_page_number = 0
                    while has_next_case_page:
                        time.sleep(Setting.get().req_interval)
                        case_page_number += 1
                        is_success, case_list, has_next_case_page = qcc_util.get_case_list(
                            case_page_number, company)
                        if not is_success:
                            print('retry to get the case list after {} seconds'.format(
                                Setting.get().error_wait_interval))
                            time.sleep(Setting.get().error_wait_interval)
                            has_next_case_page = True
                            case_page_number -= 1
                            continue

                        index = 0
                        while index < len(case_list):
                            case = case_list[index]
                            if not collect_all and int(case.unfulfilled_amount) < Setting.get().unfulfilled_amount:
                                print('{} is ignored, the unfulfilled amount is less than 1000000'.format(case.case_id))
                                index += 1
                                continue

                            time.sleep(Setting.get().req_interval)
                            is_success, judgment_debtor = qcc_util.get_company_info(case.judgment_debtor)
                            if not is_success:
                                print('have an error, continue after {} seconds'.format(Setting.get().error_wait_interval))
                                time.sleep(Setting.get().error_wait_interval)
                                continue

                            time.sleep(Setting.get().req_interval)
                            is_success, judgment_creditor = qcc_util.get_company_info(case.judgment_creditor)
                            if not is_success:
                                print('have an error, continue after {} seconds'.format(Setting.get().error_wait_interval))
                                time.sleep(Setting.get().error_wait_interval)
                                continue

                            if not collect_all and (ignore_case(case.case_id, judgment_debtor) or ignore_case(case.case_id, judgment_creditor)):
                                index += 1
                                continue

                            MysqlUtil.insert_company(judgment_debtor)
                            MysqlUtil.insert_company(judgment_creditor)
                            MysqlUtil.insert_case(case)
                            print('insert {}'.format(case.case_id))
                            index += 1
    return True


if __name__ == "__main__":
    LogUtil.enable()
    while True:
        if not main():
            print('failed to collect all data, it will continue after 60 seconds')
            time.sleep(60)
        else:
            print('finish to collect all data')
            print('continue to collect all data after {} hours'.format(Setting.get().next_interval/3600))
            StateUtil.get().reset()
            time.sleep(Setting.get().next_interval)
