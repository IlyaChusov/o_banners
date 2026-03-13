import sys
from .banners_work import main as b_main
from utils.db_utils import mysql_connect
from .logM import logM

def main():
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    
    # Выбираем записи, где comment не 'mobile app' и не 'в работе'
    cursor.execute("SELECT * FROM new_banners WHERE comment NOT IN ('mobile app', 'в работе')")
    new_banners = cursor.fetchall()
    
    try:
        for banner in new_banners:
            logM(str(banner['id']))
            cursor.execute('SELECT ad_link FROM main WHERE id=' + str(banner['id']))
            ad_link = cursor.fetchall()
            if len(ad_link) == 0:
                logM('no ad_link for banner ' + str(banner['id']))
            else:
                logM("ad_link['ad_link']: " + ad_link[0]['ad_link'])
                banner['ad_link'] = ad_link[0]['ad_link']
                # ad_links.append(ad_link[0]['ad_link'])
    except Exception as e:
        logM(f"Ошибка process_banners:  {str(e)}")
    cursor.execute("SELECT * FROM category_subcategory_view")
    subcategory_ids = cursor.fetchall()
    
    if len(new_banners) == 0:
        cursor.close()
        db.close()
        sys.exit(0)
    
    # Помечаем выбранные записи как "в работе"
    banner_ids = [str(banner['id']) for banner in new_banners]
    if banner_ids:
        cursor.execute(f"""
            UPDATE new_banners
            SET comment = 'в работе'
            WHERE id IN ({','.join(banner_ids)})
        """)
        db.commit()
    
    # Обрабатываем баннеры
    res = b_main(db, cursor, new_banners, subcategory_ids)
    
    db.commit()
    cursor.close()
    db.close()
    return True

if __name__ == '__main__':
    main()
