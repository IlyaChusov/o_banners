# APPIUM WORK
# new server
import paramiko, rpyc
import json, os, sys
import banners_work

# *запуск yandex_market.parser_ya_market*
# data - ответ yandex_market.parser_ya_market
def main(data):
    # data = [{'folder_path': '/home/tartamonova/code/ya_market_parser/screenshots/yandex market app_20250421_224002.png', 'domain': 'yandex market app', 'ad_link': 'https://market.yandex.ru/special/proplan-dog-march25?fromSins=1&erid=nyi26TK8Sq2EHekN7M8qEKHaaAgNfNzR', 'file_name': 'yandex market app_20250421_224002.png', 'file_path': '/home/tartamonova/code/ya_market_parser/screenshots', 'banner_name': '', 'resource_type': 'mobile', 'depth': 2, 'site_type': 'marketplace', 'top_offset': 577, 'width': 1036, 'height': 584}]
    out_list = list()
    for banner in data:
        out_list.append(banner['file_path'] + '/' + banner['file_name'])

    response = json.loads(banners_work.main(out_list))
    if len(response) > 0:
        # print('not pepega')
        for i in range(0, len(data)):
            if len(response[i]) > 0:
                data[i]['brand'] = response[i][0]
                data[i]['subcategory'] = response[i][1]

    data_json = json.dumps(data, ensure_ascii=False)
    conn = rpyc.connect("localhost", 12345)
    c = conn.root
    response = c.pass_data_to_old_server(data_json)
    if (len(response) != 0):
        print(response[0])
    else:
        print('appium work are done')
