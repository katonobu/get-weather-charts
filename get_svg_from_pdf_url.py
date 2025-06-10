import re
import datetime
import fitz  # PyMuPDF
import requests
import unicodedata

def get_svg_from_pdf_url(pdf_url):
    result_obj = {
         "result":False,
         "url":pdf_url,
         "response_ok":False,
         "page_count":0,
         "pages":[]
    }

    # PDFをダウンロード（バイナリデータ取得）
    response = requests.get(pdf_url)
    result_obj.update({"response_ok":response.ok})
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる

    # メモリ上のバイナリデータからPDFを開く
    doc = fitz.open(stream=response.content, filetype="pdf")

    result_obj["page_count"] = doc.page_count
    # 各ページをSVG（ベクタ）としてエクスポート
    for page_index in range(doc.page_count):
        page = doc[page_index]
        page_obj = {
             "svg":page.get_svg_image(),
             "texts":page.get_text("text")
        }
        result_obj["pages"].append(page_obj)
    doc.close()
    result_obj.update({"result":True})
    return result_obj


def get_released_datetime(texts):
    text_lines = texts.split("\n")
    if text_lines[0].startswith("短期予報解説資料"):
        released_at_str = text_lines[0].split()[-1]
        normalized_str = unicodedata.normalize("NFKC", released_at_str)
        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日\d{1,2}時\d{2}分発表$", normalized_str):
            released_at = datetime.datetime.strptime(normalized_str, "%Y年%m月%d日%H時%M分発表")
    return released_at

def get_svg_from_url(svg_url):
    result_obj = {
         "result":False,
         "url":svg_url,
         "response_ok":False,
         "svg":None
    }

    response = requests.get(svg_url)
    result_obj.update({"response_ok":response.ok})
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    result_obj.update({"svg":response.content})
    result_obj.update({"result":True})
    return result_obj

