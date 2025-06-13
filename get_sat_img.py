import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def get_element(driver, xpath, retry_count = 10, retry_interval = 1):
    """指定されたXPathの要素を取得する。見つからない場合はNoneを返す。"""
    for count in range(retry_count):
        try:
            element = driver.find_element("xpath", xpath)
            if element:
                if 0 < count:
                    print("O")
                return element
        except Exception as e:
            print(f"Error finding elements with xpath '{xpath}': {e}")
        time.sleep(retry_interval)
        print('.', end="", flush=True)

def wait_with_dots(message, retry_count=10, retry_interval=1):
    """指定されたメッセージを表示し、指定回数だけドットを出力する。"""
    print(message, end="", flush=True)
    for _ in range(retry_count):
        time.sleep(retry_interval)
        print('.', end="", flush=True)
    print("O")

def get_sat_img(url, driver, output_dir, file_name_suffix = None, req_click_count = 0, max_prev_click_count=6, retry_interval=1):
    result_obj = {
        "result":False,
        "url":url,
        "output_dir":output_dir,
        "file_name_suffix":file_name_suffix,
        "max_prev_click_count":max_prev_click_count,
        "req_click_count":req_click_count,
    }
    output_file_paths = []
    driver.get(url)
    driver.refresh()

    # ページの読み込み待機
    wait_with_dots("Waiting for page to load", retry_count=5, retry_interval=retry_interval)

    # 要素が見つかるまで待機
    selected_time_ele = get_element(driver, '//*[@id="unitmap-slidervalue"]/div/span')
    selected_date_time_ele = get_element(driver, '//*[@id="unitmap-infotime"]')
    if selected_time_ele is None or selected_date_time_ele is None:
        print("can't find button or selected time or selected date time element.")
        result_obj.update({"result": False, "error": "Element not found"})
        return result_obj

    selected_time = selected_time_ele.text
    selected_date_time = selected_date_time_ele.text
    result_obj.update({"init_time":selected_time})
    print(selected_time, selected_date_time)
    click_count = 0
    found_click_count = 0
    for _ in range(max_prev_click_count):
        # 左キー押下
        driver.find_element("tag name", "body").send_keys(Keys.LEFT)
        click_count += 1

        if req_click_count <= click_count:
            print("Clicked")
            wait_with_dots("Prev button clicked, waiting for page to load", retry_count=5, retry_interval=1)
            selected_time_ele = get_element(driver, '//*[@id="unitmap-slidervalue"]/div/span')
            selected_date_time_ele = get_element(driver, '//*[@id="unitmap-infotime"]')
            if selected_time_ele is None or selected_date_time_ele is None:
                print("can't find button or selected time or selected date time element.")
                result_obj.update({"result": False, "error": "Element not found after clicking"})
                return result_obj

            selected_time = selected_time_ele.text
            selected_date_time = selected_date_time_ele.text
            print(selected_time, selected_date_time)
            if selected_time.endswith("09:00:00") or selected_time.endswith("21:00:00"):
                found_click_count = click_count
                [year,remain] = selected_date_time.split("年")
                [month, remain] = remain.split("月")
                [day, remain] = remain.split("日")
                [hour, remain] = remain.split("時")
                [minute, remain] = remain.split("分")
                [sec, remain] = remain.split("秒")
                date_time_str = f'{year}{int(month,10):02d}{int(day,10):02d}{int(hour,10):02d}{int(minute,10):02d}{int(sec,10):02d}'
                if file_name_suffix:
                    date_time_str += f'_{file_name_suffix}'
                file_name = os.path.join(output_dir, f'{date_time_str}.png')
                wait_with_dots("Before capture, wait for 5sec", retry_count=5, retry_interval=1)
#                //*[@id="unitmap-header"]/nav/div[4]/div[3]                
                print(f'save to {file_name}')
                driver.save_screenshot(file_name)
                output_file_paths.append(file_name)
                break
        else:
            print('.', end="", flush=True)
            time.sleep(1)
    result_obj.update({
        "result": True,
        "output_file_paths": output_file_paths,
        "last_time":selected_time,
        "found_click_count": found_click_count
    })
    return result_obj

def ele_name_to_japanese(elem):
    ele_to_j_obj = {
        "vis":"可視画像",
        "ir":"赤外画像",
        "vap":"水蒸気画像",
        "color":"カラー画像",
        "strengthen":"雲頂強調画像",
    }
    if elem in ele_to_j_obj:
        return ele_to_j_obj[elem]
    else:
        return elem

def get_sat_imgs(output_dir, is_headless = False, elems = None, max_click_count=24):
    # 取得対象種別指定
    acceptable_elems = ["vis","ir", "vap", "color", "strengthen"]
    if elems is None:
        # 指定がないときには全部取得する
        elems = acceptable_elems

    # Chromeのオプション設定
    chrome_options = Options()
    if is_headless:
        print("Running in headless mode")
        chrome_options.add_argument("--headless")  # GUIなしで動作
    else:
        print("Running in GUI mode")
    chrome_options.add_argument("--window-size=1280,1000")  # 幅1280px, 高さ1000px

    # ChromeDriverのセットアップ
    driver = webdriver.Chrome(options=chrome_options)

    os.makedirs(output_dir, exist_ok=True)

    result_obj = {
        "result": False,
        "elements": elems,
        "is_headless": is_headless,
        "output_dir": output_dir,
        "capture_results": []
    }
    req_click_count = 0
    for elem in elems:
        url = f"https://www.jma.go.jp/bosai/map.html#5/34.5/137/&elem={elem}&contents=himawari"
        if elem not in acceptable_elems:
            print(f"Invalid element: {elem}. Skipping...")
            result_obj["capture_results"].append({
                "result":False,
                "url":url,
                "acceptable_elems":acceptable_elems,
                "error": "Invalid element",
            })
            continue
        result = get_sat_img(url, driver, output_dir, elem, req_click_count, max_click_count)
        if result["result"] and result["found_click_count"] > 0:
            req_click_count = result["found_click_count"]
            print(f"Captured image for {elem} at {result['last_time']}")
        result_obj["capture_results"].append(result)
    result_obj["result"] = all(res["result"] for res in result_obj["capture_results"])
    # 終了処理
    driver.quit()
    return result_obj

if __name__ == "__main__":
    import os
    import json
    import time

    # 現在時刻文字列の出力ディレクトリ作成
    now_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_dir = os.path.join(os.path.dirname(__file__), 'output', f'{now_str}_{os.path.basename(__file__)}')
    os.makedirs(output_dir, exist_ok=True)

    result_obj = get_sat_imgs(
        output_dir,
#        True,  # True # Headless mode
    )
    print(json.dumps(result_obj, ensure_ascii=False, indent=2))
