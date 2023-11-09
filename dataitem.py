class Company:
    def __init__(self):
        # 公司ID
        self.company_id = ''

        # 公司名字
        self.company_name = ''

        # 手机号码
        self.phone_number = ''

        # 法定代表人
        self.lr = ''

        # 所属地区
        self.region = ''

        # 注册资本
        self.rc = ''

        # 实缴资本
        self.pc = ''

        # 登记状态
        self.status = ''

        # 股东信息
        self.share_holders = []


class ShareHolder:
    def __init__(self):
        # 公司ID
        self.company_id = ''

        # 股东名字
        self.name = ''

        # 持股比例
        self.rate = ''


class Case:
    def __init__(self):
        # 案号
        self.case_id = ''

        # 采集时间戳 UTC
        self.collect_time = 0

        # 被执行人（公司ID）
        self.judgment_debtor = ''

        # 疑似申请执行人（公司ID）
        self.judgment_creditor = ''

        # 未履行金额
        self.unfulfilled_amount = ''

        # 执行法院
        self.executing_court = ''

        # 终本日期
        self.finality_date = ''
