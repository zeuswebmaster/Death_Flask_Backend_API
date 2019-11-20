import scrapy
from scrapy_splash import SplashRequest


class Crawler(scrapy.Spider):
    name = 'reports'

    username = 'test1@consumerdirect.com'
    password = '12345678'

    http_user = 'documentservicesolutions'
    http_pass = 'grapackerown'

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
        # tables = response.xpath("//div[@id='TokenDisplay']//td[@class='crWhiteTradelineHeader']/ancestor::table[2]").extract()
        tables = response.xpath("""//*[@id="TokenDisplay"]//table[@bordercolor="#eeeeee"]""").extract()
        self.log('Tables:')
        self.log(tables)
        self.log(f'Length: {len(tables)}')
        for table in tables:
            debt_name = creditor = table.xpath("./descendant::td[@class='crWhiteTradelineHeader'][2]/b/text()").get()
            self.log(debt_name)
