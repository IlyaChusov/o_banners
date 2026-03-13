import json, os, sys
from .banners_work import main as b_main
from .logM import logM

def main(db, cursor, data, ad_links, subcategory_ids):
    # data = [{'folder_path': '/home/tartamonova/code/ya_market_parser/screenshots/yandex market app_20250421_224002.png', 'domain': 'yandex market app', 'ad_link': 'https://market.yandex.ru/special/proplan-dog-march25?fromSins=1&erid=nyi26TK8Sq2EHekN7M8qEKHaaAgNfNzR', 'file_name': 'yandex market app_20250421_224002.png', 'file_path': '/home/tartamonova/code/ya_market_parser/screenshots', 'banner_name': '', 'resource_type': 'mobile', 'depth': 2, 'site_type': 'marketplace', 'top_offset': 577, 'width': 1036, 'height': 584}]
    out_list = list()
    for banner in data:
        out_list.append("/home/gen/test/clone_arena/ii_module1/screens/" + banner['file_name'])
    ad_links_ = list()
    for link in ad_links:
        ad_links_.append(link)
    response = json.loads(b_main(out_list, ad_links_))
    if len(response) > 0:
        for i in range(0, len(data)):
            if len(response[i]) > 0:
                subcategory_id = response[i][1]
                category_id = 'null'
                subcategory = 'null'
                for row in subcategory_ids:
                    if str(row['subcategory_id']) == str(subcategory_id):
                        category_id = row['category_id']
                        break
                data[i]['brand'] = response[i][0]
                data[i]['category_id'] = category_id
                data[i]['subcategory_id'] = subcategory_id
                data[i]['percentage'] = response[i][2]

    return data
