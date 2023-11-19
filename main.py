from setting import Setting
from qccutil import QccUtil
from mysqlutil import MysqlUtil
from logutil import LogUtil
from stateutil import StateUtil
import time
import random


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


def get_request_interval_seconds():
    return random.randint(10, Setting.get().req_interval)


def get_company_info_by_request(qcc_util, company_id):
    print('get the information of the company {} by request'.format(company_id))
    while True:
        time.sleep(get_request_interval_seconds())
        is_success, company = qcc_util.get_company_info(company_id)
        if not is_success:
            print('have an error, continue after {} seconds'.format(Setting.get().error_wait_interval))
            time.sleep(Setting.get().error_wait_interval)
            Setting.get().reload()
            continue
        else:
            MysqlUtil.insert_company(company)
            return company


def get_case_list_by_request(qcc_util, state, company_id, page_number):
    print('get cases of the company {} in page {} by request'.format(company_id, page_number))
    while True:
        time.sleep(get_request_interval_seconds())
        is_success, case_list, has_next_case_page = qcc_util.get_case_list(
            page_number, company_id)
        if not is_success:
            print('retry to get the case list after {} seconds'.format(
                Setting.get().error_wait_interval))
            time.sleep(Setting.get().error_wait_interval)
            Setting.get().reload()
            continue
        else:
            break

    begin = 0
    if len(state.current_case_id) > 0:
        for i in range(len(case_list)):
            if state.current_case_id == case_list[i].case_id:
                begin = i
                break
    print('the case count is {}, collect from index {}'.format(len(case_list), begin))
    for index in range(begin, len(case_list)):
        case = case_list[index]
        print('collect case {}'.format(case.case_id))
        state.current_case_id = case.case_id
        StateUtil.get().save_state(state)

        unfulfilled_amount_min = Setting.get().unfulfilled_amount
        unfulfilled_amount_max = Setting.get().unfulfilled_amount_max
        unfulfilled_amount = int(float(case.unfulfilled_amount))
        if (unfulfilled_amount_min != 0 or unfulfilled_amount_max != 0)\
                and (unfulfilled_amount < unfulfilled_amount_min or unfulfilled_amount > unfulfilled_amount_max):
            print('{} is ignored, the unfulfilled amount is not in [{},{}]'.format(case.case_id,
                                                                                   unfulfilled_amount_min,
                                                                                   unfulfilled_amount_max))
            continue
        if MysqlUtil.is_company_exist(case.judgment_debtor):
            print('the company {} exist, not need to collect again'.format(case.judgment_debtor))
        else:
            get_company_info_by_request(qcc_util, case.judgment_debtor)

        if MysqlUtil.is_company_exist(case.judgment_creditor):
            print('the company {} exist, not need to collect again'.format(case.judgment_creditor))
        else:
            get_company_info_by_request(qcc_util, case.judgment_creditor)

        # if not collect_all and (
        #         ignore_case(case.case_id, judgment_debtor) or ignore_case(case.case_id, judgment_creditor)):
        #     index += 1
        #     continue

        MysqlUtil.insert_case(case)
        print('insert case {}'.format(case.case_id))
    return has_next_case_page


def get_company_list_by_request(qcc_util, state, filter_key, filter_region, page_number):
    print('get companies in page {} by request'.format(page_number))
    while True:
        time.sleep(get_request_interval_seconds())
        is_success, company_list, has_next_company_page = qcc_util.get_company_list(
            page_number, filter_key, filter_region)
        if not is_success:
            print('retry to get the company list after {} seconds'.format(Setting.get().error_wait_interval))
            time.sleep(Setting.get().error_wait_interval)
            Setting.get().reload()
            continue
        else:
            break

    company_begin_index = 0
    if len(state.current_company_id) > 0:
        for i in range(len(company_list)):
            if company_list[i] == state.current_company_id:
                company_begin_index = i
                break
    print('the company count is {}, collect from index {}'.format(len(company_list), company_begin_index))

    for i in range(company_begin_index, len(company_list)):
        company = company_list[i]
        if i > company_begin_index:
            state.set_current_company_id(company)
            StateUtil.get().save_state(state)

        has_next_case_page = True
        case_page_number = state.current_case_page_index
        while has_next_case_page:
            has_next_case_page = get_case_list_by_request(qcc_util, state, company, case_page_number)
            if has_next_case_page:
                case_page_number += 1
                state.set_current_case_page_index(case_page_number)
                StateUtil.get().save_state(state)
    return has_next_company_page


def main():
    filter_keys = Setting.get().filter.key
    filter_regions = Setting.get().filter.region
    for filter_key in filter_keys:
        for filter_region in filter_regions:
            print('filter key is {}, filter region is {}'.format(filter_key, filter_region))

            qcc_util = QccUtil()
            time.sleep(Setting.get().req_interval)
            if not qcc_util.get_basic_info():
                Setting.get().reload()
                return False

            state = StateUtil.get().get_state(filter_key, filter_region)
            print('continue to collect data from the following state')
            print(state)

            company_page_number = state.current_company_page_index
            has_next_company_page = True
            while has_next_company_page:
                has_next_company_page = get_company_list_by_request(qcc_util, state, filter_key,
                                                                    filter_region, company_page_number)
                if has_next_company_page:
                    company_page_number += 1
                    state.set_current_company_page_index(company_page_number)
                    StateUtil.get().save_state(state)
                else:
                    break
    return True


if __name__ == "__main__":
    LogUtil.enable()
    if MysqlUtil.connect() and MysqlUtil.create_table_if_need():
        while True:
            if not main():
                print('failed to collect all data, it will continue after 60 seconds')
                time.sleep(60)
            else:
                print('finish to collect all data')
                break
