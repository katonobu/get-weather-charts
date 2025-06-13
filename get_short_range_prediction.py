import os
import json
import datetime
import shutil
from get_svg_from_pdf_url import get_svg_from_pdf_url, get_svg_from_url, extract_date
from get_sat_img import get_sat_imgs, ele_name_to_japanese
from get_lader_png import get_lader_png

if __name__ == "__main__":
    import markdown

    jst_hour_diff = 9
    release_duration_hour = 6
    release_duration_minutes = 40

    md_text = '<a id="top"></a>\n'
    print(f'Start at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # 短期予報解説資料を取得
    print("Getting 短期予報解説資料...")
    tanki_obj = get_svg_from_pdf_url("https://www.data.jma.go.jp/yoho/data/jishin/kaisetsu_tanki_latest.pdf")
    # textが抽出されていたら
    if tanki_obj["result"] and 0 < len(tanki_obj["pages"]) and "texts" in tanki_obj["pages"][0]:
        # textから発表日時を取得
        title_str = tanki_obj["pages"][0]["texts"].split("\n")[0]
        md_text += f'# {title_str.split()[0].replace("1","")}\n'
        reported_at_str = title_str.split()[1]
        md_text += f'## {reported_at_str}\n'
        released_datetime = extract_date(reported_at_str)
        print(f'Published at {released_datetime}(JST)')

        # 参照元の観測時刻のUTC時刻を生成
        td = datetime.timedelta(hours = jst_hour_diff+release_duration_hour, minutes=release_duration_minutes)
        utc_snapshot_datetime = released_datetime - td
        get_utc_time_str = utc_snapshot_datetime.strftime("%Y%m%d%H%M")
        print(f'Based     on {utc_snapshot_datetime}(UTC)')

        output_base_dir = os.path.join(os.path.dirname(__file__), released_datetime.strftime('%Y%m%d_%H%M'))

        # 発表時刻名のディレクトリを掘る
        os.makedirs(output_base_dir, exist_ok=True)

        # 短期予報解説資料取得
        md_text += f'## 画像個別リンク\n'
        md_text += '<ul>\n'

        if "svg" in tanki_obj["pages"][0]:
            # 短期予報のsvgを保存
            tanki_yoho_svg_path_name = os.path.join(output_base_dir, "kaisetsu_tanki.svg")
            with open(tanki_yoho_svg_path_name, "w", encoding="utf-8") as f:
                f.write(tanki_obj["pages"][0]["svg"])
            md_text += '<li><a href="kaisetsu_tanki.svg" target="_blank">短期予報解説資料</a></li>\n'

        # 実況天気図（アジア太平洋域）
        zikkyo_chijo_svg_url = f'https://www.data.jma.go.jp/yoho/data/wxchart/quick/{released_datetime.strftime("%Y%m")}/ASAS_MONO_{get_utc_time_str}.svgz'
        print("  Getting ASAS 実況天気図（アジア太平洋域）...")
        zikkyo_chijo_obj = get_svg_from_url(zikkyo_chijo_svg_url)
        if zikkyo_chijo_obj["result"] and "svg" in zikkyo_chijo_obj:
            zikkyo_chijo_svg_path_name = os.path.join(output_base_dir, "ASAS.svg")
            with open(zikkyo_chijo_svg_path_name, "w", encoding="utf-8") as f:
                f.write(zikkyo_chijo_obj["svg"].decode(encoding='utf-8'))
            md_text += '<li><a href="ASAS.svg" target="_blank">実況天気図（アジア太平洋域）</a></li>\n'

        # 各種天気図/予報図を取得
        get_utc_hour_str = get_utc_time_str[8:10]
        url_filename_objs = [
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq35_{get_utc_hour_str}.pdf',
                "name":"AUPQ35.svg",
                "title":"アジア500hPa・300hPa高度・気温・風・等風速線天気図"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq78_{get_utc_hour_str}.pdf',
                "name":"AUPQ78.svg",
                "title":"アジア850hPa・700hPa高度・気温・風・湿数天気図"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/axfe578_{get_utc_hour_str}.pdf',
                "name":"AXFE578.svg",
                "title":"極東850hPa気温・風、700hPa上昇流／500hPa高度・渦度天気図"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/axjp140_{get_utc_hour_str}.pdf',
                "name":"AXJP130_AXJP140.svg",
                "title":"高層断面図（風・気温・露点等）東経130度／140度解析"
            },
            {
                "url":'https://www.data.jma.go.jp/yoho/data/wxchart/quick/FSAS24_MONO_ASIA.pdf',
                "name":"FSAS24.svg",
                "title":"アジア太平洋域 24時間"
            },
            {
                "url":'https://www.data.jma.go.jp/yoho/data/wxchart/quick/FSAS48_MONO_ASIA.pdf',
                "name":"FSAS48.svg",
                "title":"アジア太平洋域 48時間"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe502_{get_utc_hour_str}.pdf',
                "name":"FXFE502.svg",
                "title":"極東地上気圧・風・降水量／500hPa高度・渦度予想図 12・24時間"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe504_{get_utc_hour_str}.pdf',
                "name":"FXFE504.svg",
                "title":"極東地上気圧・風・降水量／500hPa高度・渦度予想図 36・48時間"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe5782_{get_utc_hour_str}.pdf',
                "name":"FXFE5782.svg",
                "title":"極東850hPa気温・風、700hPa上昇流／700hPa湿数、500hPa気温予想図 12・24時間"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe5784_{get_utc_hour_str}.pdf',
                "name":"FXFE5784.svg",
                "title":"極東850hPa気温・風、700hPa上昇流／700hPa湿数、500hPa気温予想図 36・48時間"
            },
            {
                "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxjp854_{get_utc_hour_str}.pdf',
                "name":"FXJP854.svg",
                "title":"日本850hPa相当温位・風予想図 12・24・36・48時間"
            },
        ]
        gazo_md_text = ""
        for url_file_obj in url_filename_objs:
            print(f'  Getting {url_file_obj["name"].replace(".svg","").replace(".png","")} {url_file_obj["title"]}...')
            obj = get_svg_from_pdf_url(url_file_obj["url"])
            if obj["result"] and 0 < len(obj["pages"]) and "svg" in obj["pages"][0]:
                obj["pages"][0]["svg"]
                svg_path_name = os.path.join(output_base_dir, url_file_obj["name"])
                with open(svg_path_name, "w", encoding="utf-8") as f:
                    f.write(obj["pages"][0]["svg"])
                md_text += f'<li><a href="{url_file_obj["name"]}" target="_blank">{url_file_obj["title"]}</a></li>\n'
                gazo_md_text += f'[ページトップ](#top)\n'
                gazo_md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="{url_file_obj["name"].replace(".svg","")}" src="{url_file_obj["name"]}"></img>\n'

        # レーダー画像取得
        rain_lader_png_path = get_lader_png(get_utc_time_str[:10], output_base_dir)
        md_text += f'<li><a href="{os.path.basename(rain_lader_png_path)}" target="_blank">レーダー画像</a></li>\n'
        gazo_md_text += f'[ページトップ](#top)\n'
        gazo_md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="rain_lader_png" src="{os.path.basename(rain_lader_png_path)}"></img>\n'

        # 衛星画像取得
        result_obj = get_sat_imgs(
            output_base_dir,
            True,  # True # Headless mode
        )
        with open(os.path.join(output_base_dir, "get_sat_imgs_result.json"), "w", encoding="utf-8") as f:
            json.dump(result_obj, f, ensure_ascii=False, indent=2)


        for capture_result in result_obj["capture_results"]:
            output_file_path = capture_result["output_file_paths"][0]
            file_name = os.path.basename(output_file_path)
            md_text += f'<li><a href="{file_name}" target="_blank">{ele_name_to_japanese(capture_result["file_name_suffix"])}</a></li>\n'
            gazo_md_text += f'[ページトップ](#top)\n'
            gazo_md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="sat_{capture_result["file_name_suffix"]}" src="{file_name}"></img>\n'            

        md_text += '</ul>'

        md_text += '## ページ内画像リンク\n'
        md_text += '- [短期予報解説資料](#tanki_yoho)\n'
        md_text += '- [実況天気図（アジア太平洋域）](#zikkyo_chijo)\n'
        for item in url_filename_objs:
            md_text += f'- [{item["title"]}](#{item["name"].replace(".svg","").replace(".png","")})\n'
        md_text += f'- [レーダー画像](#rain_lader_png)\n'
        for capture_result in result_obj["capture_results"]:
            md_text += f'- [{ele_name_to_japanese(capture_result["file_name_suffix"])}](#sat_{capture_result["file_name_suffix"]})\n'

        md_text += f'## 画像\n'
        md_text += f'[ページトップ](#top)\n'
        md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="tanki_yoho" src="kaisetsu_tanki.svg"></img>\n'
        md_text += f'[ページトップ](#top)\n'
        md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="zikkyo_chijo" src="ASAS.svg"></img>\n'
        md_text += gazo_md_text
        md_text += f'[ページトップ](#top)\n'

        html_text = markdown.markdown(md_text)
        html_path_name = os.path.join(output_base_dir, "index.html")
        with open(html_path_name, "w", encoding="utf-8") as f:
            f.write(html_text)

        shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_base_dir), base_dir=os.path.basename(output_base_dir))
        print(f'Output saved to {output_base_dir} and output.zip')
        print(f'Finished at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        exit(0)
    else:
        print("Failed to get 短期予報解説資料 or no text found.")
        exit(1)