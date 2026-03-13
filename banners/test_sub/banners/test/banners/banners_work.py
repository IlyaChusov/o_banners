# CLIENT new
# banners_work.py
import rpyc, sys, json, time, os, traceback
from .logM import logM

def clear(string):
    string = str(string)
    string = string.replace("'", '')
    string = string.replace('"', '')
    string = string.replace(';', ',')
    return string

def exitt():
    print(json.dumps([None, None]))
    sys.exit()

def process_ready_banner(db, cursor, banner):
    banner_id = str(banner['id'])
    brand = banner['brand']
    cursor.execute('SELECT id_orig FROM main WHERE id=' + banner_id)
    res = cursor.fetchall()
    id_orig = str(res[0]['id_orig'])
    cursor.execute('''
            UPDATE main
            SET
                brand = %s,
                category_id = %s,
                subcategory_id = %s,
                confidence = %s
            WHERE id = %s OR id_orig = %s
    ''', (brand, banner['category_id'], banner['subcategory_id'], banner['confidence'], banner_id, id_orig))
    i = 0
    id = banner_id
    while id != id_orig and i < 10:
        cursor.execute('SELECT id_orig FROM main WHERE id=' + id_orig)
        res2 = cursor.fetchall()
        id = id_orig
        id_orig = str(res2[0]['id_orig'])
        cursor.execute('''
            UPDATE main
            SET
                brand = %s,
                category = %s,
                subcategory = %s,
                confidence = %s
            WHERE id_orig = %s
            ''', (brand, banner['category_id'], banner['subcategory_id'], banner['confidence'], id_orig))
        i = i + 1
    cursor.execute('''INSERT INTO banners_to_send VALUES (%s, %s)''', (banner_id, 1))
    db.commit()
    cursor.execute("DELETE FROM new_banners WHERE id = %s", (banner_id,))
    db.commit()

# def main(arguments, ad_links):
def main(db, cursor, data, subcategory_ids):
    out_str = ''
    try:
        if len(data) < 1:
            exitt()
        if '.py' in data[0]:
            data.pop(0)
            if len(data) < 1:
                exitt()
        dir = '/home/gen/test/clone_arena/ii_module1/screens/'
        if 'home' in data[0]:
            dir = ''
        for banner in data:
            banner['file_name'] = dir + banner['file_name']
        logM('старт обработки группы баннеров: ' + str(len(data)) + ' шт')
        print('старт обработки группы баннеров: ' + str(len(data)) + ' шт')
        start_all_time = time.time()
        conn = rpyc.connect('localhost', 12345, config={"sync_request_timeout": len(data) * 180})
        c = conn.root
        out_list = list()
        i = 0
        str_arg = ''
        for arg in data:
            str_arg = str_arg + '\n' + str(arg)
        logM('размер data: ' + str(len(data)))
        # logM('размер ad_links: ' + str(len(ad_links)))
        logM('data: ' + str_arg)
        # logM('ad_links: ' + str_link)
        for banner in data:
            banner_name = banner['file_name']
            ad_link = banner['ad_link']
            logM('обработка баннера ' + banner_name + ' начата, ad_link: ' + ad_link)
            print('обработка баннера ' + banner_name + ' начата, ad_link: ' + ad_link)
            start_time = time.time()
            print(banner)
            neuro_answer = clear(c.get_brand_and_category_id(banner_name, ad_link)).split('§')
            i = i + 1
            brand = neuro_answer[0]
            subcategory_id = neuro_answer[1]
            confidence = neuro_answer[2]
            for row in subcategory_ids:
                if str(row['subcategory_id']) == str(subcategory_id):
                    category_id = row['category_id']
                    break
            banner['brand'] = brand
            banner['category_id'] = category_id
            banner['subcategory_id'] = subcategory_id
            banner['confidence'] = confidence
            print('отправляю баннер ' + banner_name + ' на обработку, banner info:')
            print(banner)
            process_ready_banner(db, cursor, banner)
            # out_list.append([brand, subcategory_id, percentage])
            res_time = str(round(time.time() - start_time, 1))
            short_b_n = os.path.basename(banner_name)
            print('баннер ' + short_b_n + ' отработал, время: ' + res_time + ' секунды')
            logM('баннер ' + short_b_n + ' отработал, время: ' + res_time + ' секунды')
        res_all_time = str(round(time.time() - start_all_time, 1))
        logM('окончена обработка группы баннеров, время: ' + res_all_time)
        print('окончена обработка группы баннеров, время: ' + res_all_time)
        conn.close()
        # out_str = json.dumps(out_list, ensure_ascii=False)
        # print(out_str)
    except Exception as e:
        print(traceback.format_exc())
        logM(print(traceback.format_exc()))
        # print(f"Ошибка нейросети:  {str(e)}")
        # logM(f"Ошибка нейросети:  {str(e)}")
    # return out_str

if __name__ == "__main__":
    main(sys.argv)
