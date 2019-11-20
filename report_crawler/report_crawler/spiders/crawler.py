import datetime
import sqlite3

import scrapy
from scrapy_splash import SplashRequest


class Crawler(scrapy.Spider):
    name = 'reports'

    username = 'test1@consumerdirect.com'
    password = '12345678'

    http_user = 'documentservicesolutions'
    http_pass = 'grapackerown'

    connection = sqlite3.connect('./reports.db')
    cursor = connection.cursor()

    start_urls = ['https://stage-sc.consumerdirect.com/login/']
    report_url = 'https://stage-sc.consumerdirect.com/member/credit-report/3b/'

    def parse(self, response):
        csrf = response.xpath("//input[@name='_csrf']/@value").get()

        return scrapy.FormRequest.from_response(
            response,
            formdata={'_csrf': csrf, 'loginType': 'CUSTOMER', 'j_username': self.username, 'j_password': self.password},
            callback=self.goto_report
        )

    def goto_report(self, response):
        yield SplashRequest(url=self.report_url, endpoint='execute', callback=self.parse_report, args={
                                    'html': 1,
                                    'wait': 10,
                                })

    def parse_report(self, response):
        self.cursor.execute("""CREATE TABLE reports (debt_name, creditor, account_type, ecoa, account_number, push,
                        last_collector, collector_account, last_debt_status, bureaus, days_delinquent, balance_original, payment_amount,
                        credit_limit, graduation, last_update)""")
        self.connection.commit()

        tables = response.xpath("""//div[@id='TokenDisplay']//td[@class='crWhiteTradelineHeader']/ancestor::table[2]""")
        self.log('Tables:')
        # self.log(tables)
        self.log(f'Length: {len(tables)}')
        for table in tables:
            row = dict()
            row['debt_name'] = row['creditor'] = table.xpath("./descendant::b/text()").get()
            row['account_number'] = self.get_cell(table, "./descendant::b[contains(text(), 'Account #')]/ancestor::tr[@class='crLightTableBackground']/td[{}]/text()", [2, 3, 4])
            row['account_type'] = self.get_cell(table, "./descendant::b[contains(text(), 'Account Type')]/ancestor::tr[@class='crTableHeader']/td[{}]/text()", [2, 3, 4])
            row['ecoa'] = self.get_cell(table, "./descendant::b[contains(text(), 'Account Description')]/ancestor::tr[@class='crTableHeader']/td[{}]/text()", [2, 3, 4])
            row['push'] = False
            row['last_collector'] = None
            row['collector_account'] = None
            row['last_debt_status'] = None
            row['bureaus'] = None
            row['balance_original'] = ''
            row['payment_amount'] = float(self.get_cell(table, "./descendant::b[contains(text(), 'Payment Amount')]/ancestor::tr[@class='crTableHeader']/td[{}]/text()", [2, 3, 4]).replace('$', ''))
            row['last_update'] = datetime.datetime.now()
            row['graduation'] = self.get_cell(table, "./descendant::b[contains(text(), 'Account Description')]/ancestor::tr[@class='crLightTableBackground']/td[{}]/text()", [2, 3, 4])
            self.log('Graduation: ', row['graduation'])
            self.insert_row(row)
            self.log(row)

    def get_cell(self, table_el, row_xpath, params):
        for param in params:
            val = table_el.xpath(row_xpath.format(param)).get()
            if val:
                if '--' not in val:
                    return val.strip().lower()

    def insert_row(self, row):
        columns = ', '.join(row.keys())
        placeholders = ', '.join('?' * len(row))
        # self.log("INSERT INTO reports ({}) VALUES ({})".format(columns, placeholders))
        self.cursor.execute("INSERT INTO reports ({}) VALUES ({})".format(columns, placeholders), tuple(row.values()))
        self.connection.commit()
