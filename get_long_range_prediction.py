import os
import datetime
import shutil
from get_svg_from_pdf_url import get_svg_from_pdf_url, get_svg_from_url, extract_date

if __name__ == "__main__":
    import markdown

    jst_hour_diff = 9

    md_text = '<a id="top"></a>\n'

    # 週間天気予報解説資料を取得
    weekly_obj = get_svg_from_pdf_url("https://www.data.jma.go.jp/yoho/data/jishin/kaisetsu_shukan_latest.pdf")
    # textが抽出されていたら
    if weekly_obj["result"] and 0 < len(weekly_obj["pages"]) and "texts" in weekly_obj["pages"][0]:
        # textから発表日時を取得
        title_str = weekly_obj["pages"][0]["texts"].split("\n")[0]
        md_text += f'# {title_str}\n'
        reported_at_str = weekly_obj["pages"][0]["texts"].split("\n")[1]
        md_text += f'## {reported_at_str}\n'
        released_datetime = extract_date(reported_at_str)
        print(released_datetime)

        output_base_dir = os.path.join(os.path.dirname(__file__), released_datetime.strftime('%Y%m%d_%H%M'))
        if True:
#        if not os.path.exists(output_base_dir):
            # 発表時刻名のディレクトリを掘る
            os.makedirs(output_base_dir, exist_ok=True)

            md_text += f'## 画像個別リンク\n'
            md_text += '<ul>\n'

            for idx, page in enumerate(weekly_obj["pages"]):
                if "svg" in page:
                    # ページごとにsvgを保存
                    page_svg_path_name = os.path.join(output_base_dir, f'syukan_yoho_{idx + 1}.svg')
                    with open(page_svg_path_name, "w", encoding="utf-8") as f:
                        f.write(page["svg"])
                    md_text += f'  <li><a href="syukan_yoho_{idx + 1}.svg" target="_blank">週間天気予報解説資料ページ{idx + 1}</a></li>\n'

            url_filename_objs = [
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fzcx50.png',
                    "name":"FZCX50.png",
                    "title":"週間予報支援図（アンサンブル）"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxxn519.png',
                    "name":"FXXN519.png",
                    "title":"週間予報支援図"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe5782_00.pdf',
                    "name":"FXFE5782.svg",
                    "title":"極東850hPa気温・風、700hPa上昇流／700hPa湿数、500hPa気温予想図 12・24時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe5784_00.pdf',
                    "name":"FXFE5784.svg",
                    "title":"極東850hPa気温・風、700hPa上昇流／700hPa湿数、500hPa気温予想図 36・48時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe577_00.pdf',
                    "name":"FXFE577.svg",
                    "title":"極東850hPa気温・風、700hPa上昇流／700hPa湿数、500hPa気温予想図 72時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/feas502_12.pdf',
                    "name":"FEAS02_FEAS502.svg",
                    "title":"アジア地上気圧、850hPa気温／500hPa高度・渦度予想図 24時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/feas504_12.pdf',
                    "name":"FEAS04_FEAS504.svg",
                    "title":"アジア地上気圧、850hPa気温／500hPa高度・渦度予想図 48時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/feas507_12.pdf',
                    "name":"FEAS07_FEAS507.svg",
                    "title":"アジア地上気圧、850hPa気温／500hPa高度・渦度予想図 72時間"
                },
                {
                    "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxjp854_00.pdf',
                    "name":"FXJP854.svg",
                    "title":"日本850hPa相当温位・風予想図 12・24・36・48時間"
                },
            ]

            gazo_md_text = ""
            for url_file_obj in url_filename_objs:
                if url_file_obj["url"].endswith(".pdf"):
                    obj = get_svg_from_pdf_url(url_file_obj["url"])
                    if obj["result"] and 0 < len(obj["pages"]) and "svg" in obj["pages"][0]:
                        obj["pages"][0]["svg"]
                        svg_path_name = os.path.join(output_base_dir, url_file_obj["name"])
                        with open(svg_path_name, "w", encoding="utf-8") as f:
                            f.write(obj["pages"][0]["svg"])
                        md_text += f'<li><a href="{url_file_obj["name"]}" target="_blank">{url_file_obj["title"]}</a></li>\n'
                        gazo_md_text += f'[ページトップ](#top)\n'
                        gazo_md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="{url_file_obj["name"].replace(".svg","")}" src="{url_file_obj["name"]}"></img>\n'
                elif url_file_obj["url"].endswith(".png"):
                    # PNGファイルは直接保存
                    png_path_name = os.path.join(output_base_dir, url_file_obj["name"])
                    with open(png_path_name, "wb") as f:
                        f.write(get_svg_from_url(url_file_obj["url"])["svg"])
                    md_text += f'<li><a href="{url_file_obj["name"]}" target="_blank">{url_file_obj["title"]}</a></li>\n'
                    gazo_md_text += f'[ページトップ](#top)\n'
                    gazo_md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="{url_file_obj["name"].replace(".png","")}" src="{url_file_obj["name"]}"></img>\n'

            md_text += '</ul>'

            md_text += '## ページ内画像リンク\n'
            md_text += '- [週間天気予報解説資料ページ1](#syukan_yoho_1)\n'
            md_text += '- [週間天気予報解説資料ページ2](#syukan_yoho_2)\n'
            for item in url_filename_objs:
                md_text += f'- [{item["title"]}](#{item["name"].replace(".svg","").replace(".png","")})\n'

            md_text += f'## 画像\n'
            md_text += f'[ページトップ](#top)\n'
            md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="syukan_yoho_1" src="syukan_yoho_1.svg"></img>\n'
            md_text += f'[ページトップ](#top)\n'
            md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" id="syukan_yoho_2" src="syukan_yoho_2.svg"></img>\n'
            md_text += gazo_md_text
            md_text += f'[ページトップ](#top)\n'

            html_text = markdown.markdown(md_text)
            html_path_name = os.path.join(output_base_dir, "index.html")
            with open(html_path_name, "w", encoding="utf-8") as f:
                f.write(html_text)

            shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_base_dir), base_dir=os.path.basename(output_base_dir))