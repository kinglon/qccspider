from setting import Setting
from qccutil import QccUtil
from mysqlutil import MysqlUtil
import time


def ignore_case(company):
    if company.status.find('在营') == -1 and company.status.find('开业') == -1 and company.status.find('在册') == -1:
        print('ignore case because the status of the company is {}'.format(company.status))
        return True

    all_company = True
    for item in company.share_holders:
        if item.name.find('公司') == -1:
            all_company = False
            break
    if all_company:
        print('ignore case because the share holders of the company {} are all companies'.format(company.company_name))
        return True

    return False


def main():
    if not MysqlUtil.connect():
        return

    if not MysqlUtil.create_table_if_need():
        return

    filter_keys = Setting.get().filter.key
    filter_regions = Setting.get().filter.region
    for filter_key in filter_keys:
        for filter_region in filter_regions:
            print('filter key is {}, filter region is {}'.format(filter_key, filter_region))
            qcc_util = QccUtil()
            time.sleep(Setting.get().req_interval)
            if not qcc_util.get_basic_info():
                return

            has_next_company_page = True
            company_page_number = 0
            while has_next_company_page:
                time.sleep(Setting.get().req_interval)
                company_page_number += 1
                is_success, company_list, has_next_company_page = qcc_util.get_company_list(
                    company_page_number, filter_key, filter_region)
                if not is_success:
                    return

                for company in company_list:
                    has_next_case_page = True
                    case_page_number = 0
                    while has_next_case_page:
                        time.sleep(Setting.get().req_interval)
                        case_page_number += 1
                        is_success, case_list, has_next_case_page = qcc_util.get_case_list(
                            case_page_number, company.company_id)
                        if not is_success:
                            return

                        for case in case_list:
                            if case.unfulfilled_amount < 1000000:
                                print('ignore case because the unfulfilled amount of the case {} is less than 1000000'.format(case.case_id))
                                continue

                            time.sleep(Setting.get().req_interval)
                            is_success, judgment_debtor = qcc_util.get_company_info(case.judgment_debtor)
                            if not is_success:
                                return
                            time.sleep(Setting.get().req_interval)
                            is_success, judgment_creditor = qcc_util.get_company_info(case.judgment_creditor)
                            if not is_success:
                                return

                            if ignore_case(judgment_debtor) or ignore_case(judgment_creditor):
                                return

                            MysqlUtil.insert_company(judgment_debtor)
                            MysqlUtil.insert_company(judgment_creditor)
                            MysqlUtil.insert_case(case)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
