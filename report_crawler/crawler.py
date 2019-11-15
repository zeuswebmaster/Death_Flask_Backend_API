import asyncio
from aiohttp import ClientSession, BasicAuth

from bs4 import BeautifulSoup as BS4


async def get_report(username, password):
    # BASIC AUTH
    ba = BasicAuth('documentservicesolutions', 'grapackerown')

    async with ClientSession() as session:
        async with session.get('https://stage-sc.consumerdirect.com/login/',
                               auth=ba) as response:
            csrf_token = (await response.text()).split('_csrf" value="')[1].split('"/>')[0]

        form_data = {
            '_csrf': csrf_token,
            'loginType': 'CUSTOMER',
            'j_username': username,
            'j_password': password
        }
        async with session.post('https://stage-sc.consumerdirect.com/login',
                                data=form_data,
                                auth=ba) as response:
            await response.read()

        async with session.get('https://stage-sc.consumerdirect.com/member/credit-report/3b/',
                               auth=ba) as response:
            pdt = (await response.text()).split('cc2-test.sd.demo.truelink.com/dsply.aspx?pdt=')[1].split('&xsl')[0]

        async with session.get('https://cc2-test.sd.demo.truelink.com/dsply.aspx?'
                               f'pdt={pdt}&'
                               'xsl=CC2CONSUMERDIRECT_3BREPORTVANTAGE3SCORE_JS',
                               auth=ba) as response:
            soup = BS4((await response.text()), 'html.parser')


def scrap_table(html):
    soup = BS4(html, 'html.parser')
    print(len(soup.findAll('p')))


async def test():
    with open('smc.html', 'r', encoding='latin-1') as file:
        scrap_table(file)

asyncio.get_event_loop().run_until_complete(test())
