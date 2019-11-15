import asyncio
import urllib

from aiohttp import ClientSession, BasicAuth


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
            print(await response.text())


async def test():
    await get_report('test1@consumerdirect.com', '12345678')

asyncio.get_event_loop().run_until_complete(test())
