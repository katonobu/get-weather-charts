import os
import datetime
import shutil
from get_svg_from_pdf_url import get_svg_from_pdf_url, get_released_datetime, get_svg_from_url

if __name__ == "__main__":
    import markdown

    jst_hour_diff = 9
    release_duration_hour = 6
    release_duration_minutes = 40

    md_text = ""

    # 短期予報解説資料を取得
    tanki_obj = get_svg_from_pdf_url("https://www.data.jma.go.jp/yoho/data/jishin/kaisetsu_tanki_latest.pdf")
    # textが抽出されていたら
    if tanki_obj["result"] and 0 < len(tanki_obj["pages"]) and "texts" in tanki_obj["pages"][0]:
        # textから発表日時を取得
        title_str = tanki_obj["pages"][0]["texts"].split("\n")[0]
        md_text += f'# {title_str.split()[0].replace("1","")}\n'
        md_text += f'## {title_str.split()[1]}\n'
        released_datetime = get_released_datetime(tanki_obj["pages"][0]["texts"])
        print(released_datetime)

        # 参照元の観測時刻のUTC時刻を生成
        td = datetime.timedelta(hours = jst_hour_diff+release_duration_hour, minutes=release_duration_minutes)
        utc_snapshot_datetime = released_datetime - td
        get_utc_time_str = utc_snapshot_datetime.strftime("%Y%m%d%H%M")
        print(utc_snapshot_datetime)

        output_base_dir = os.path.join(os.path.dirname(__file__), released_datetime.strftime('%Y%m%d_%H%M'))
        if not os.path.exists(output_base_dir):
            # 発表時刻名のディレクトリを掘る
            os.makedirs(output_base_dir, exist_ok=True)

            md_text += f'## リンク\n'
            md_text += '<ul>'

            if "svg" in tanki_obj["pages"][0]:
                # 短期予報のsvgを保存
                tanki_yoho_svg_path_name = os.path.join(output_base_dir, "tanki_yoho.svg")
                with open(tanki_yoho_svg_path_name, "w", encoding="utf-8") as f:
                    f.write(tanki_obj["pages"][0]["svg"])
                md_text += '<li><a href="tanki_yoho.svg" target="_blank">短期予報解説資料</a></li>\n'

            # 実況天気図（アジア太平洋域）
            zikkyo_chijo_svg_url = f'https://www.data.jma.go.jp/yoho/data/wxchart/quick/{released_datetime.strftime("%Y%m")}/ASAS_MONO_{get_utc_time_str}.svgz'
            zikkyo_chijo_obj = get_svg_from_url(zikkyo_chijo_svg_url)
            if zikkyo_chijo_obj["result"] and "svg" in zikkyo_chijo_obj:
                zikkyo_chijo_svg_path_name = os.path.join(output_base_dir, "zikkyo_chijo.svg")
                with open(zikkyo_chijo_svg_path_name, "w", encoding="utf-8") as f:
                    f.write(zikkyo_chijo_obj["svg"].decode(encoding='utf-8'))
                md_text += '<li><a href="zikkyo_chijo.svg" target="_blank">実況天気図（アジア太平洋域）</a></li>\n'

            get_utc_hour_str = get_utc_time_str[8:10]
            url_filename_objs = [
                {
                    "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq35_{get_utc_hour_str}.pdf',
                    "name":"300_500_hpa.svg",
                    "title":"アジア500hPa・300hPa高度・気温・風・等風速線天気図"
                },
                {
                    "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq78_{get_utc_hour_str}.pdf',
                    "name":"800_750_hpa.svg",
                    "title":"アジア850hPa・700hPa高度・気温・風・湿数天気図"
                },
                {
                    "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/axfe578_{get_utc_hour_str}.pdf',
                    "name":"850_700_500.svg",
                    "title":"極東850hPa気温・風、700hPa上昇流／500hPa高度・渦度天気図"
                },
                {
                    "url":f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/axjp140_{get_utc_hour_str}.pdf',
                    "name":"cross_section.svg",
                    "title":"高層断面図（風・気温・露点等）東経130度／140度解析"
                }
            ]
            gazo_md_text = ""
            for url_file_obj in url_filename_objs:
                obj = get_svg_from_pdf_url(url_file_obj["url"])
                if obj["result"] and 0 < len(obj["pages"]) and "svg" in obj["pages"][0]:
                    obj["pages"][0]["svg"]
                    svg_path_name = os.path.join(output_base_dir, url_file_obj["name"])
                    with open(svg_path_name, "w", encoding="utf-8") as f:
                        f.write(obj["pages"][0]["svg"])
                    md_text += f'<li><a href="{url_file_obj["name"]}" target="_blank">{url_file_obj["title"]}</a></li>\n'
                    gazo_md_text += f'![{url_file_obj["title"]}]({url_file_obj["name"]})\n'
                
            md_text += '</ul>'
            md_text += f'## 画像\n'
            md_text += '![短期予報解説資料](tanki_yoho.svg)\n'
            md_text += '![実況天気図（アジア太平洋域）](zikkyo_chijo.svg)\n'
            md_text += gazo_md_text


            html_text = markdown.markdown(md_text)
            html_path_name = os.path.join(output_base_dir, "index.html")
            with open(html_path_name, "w", encoding="utf-8") as f:
                f.write(html_text)

            shutil.make_archive("output", format='zip', root_dir=output_base_dir)