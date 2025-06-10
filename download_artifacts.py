import os
import glob
import requests
import tempfile
import zipfile
import shutil
import markdown
import webbrowser

# 設定項目
GITHUB_TOKEN = "github_pat_access_token"  # ここにGitHubのアクセストークンを設定
OWNER = "katonobu"
REPO = "get-weather-charts"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/artifacts"

# APIリクエストのヘッダー
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# APIリクエストを送信
response = requests.get(API_URL, headers=headers)

# レスポンスを処理
if response.status_code == 200:
    artifacts = response.json().get("artifacts", [])
    if artifacts:
        with tempfile.TemporaryDirectory() as temp_dir:
#            print(temp_dir)
            for artifact in artifacts:
#                print(json.dumps(artifact, indent=2, ensure_ascii=False))
                print(artifact["created_at"])
                archive_url = artifact["archive_download_url"]

                # ZIPファイルをダウンロード
                response = requests.get(archive_url, headers=headers, stream=True)
                if response.status_code == 200:
                    zip_path = os.path.join(temp_dir, f'{artifact["id"]}.zip')
                    with open(zip_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                    with zipfile.ZipFile(os.path.join(temp_dir, "output.zip"), "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                    os.remove(os.path.join(temp_dir, "output.zip"))
            dirs = [item for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isdir(item)]
#            print(json.dumps(dirs, indent=2, ensure_ascii=False))
            md_text = "# 一覧\n\n"
            for dir in dirs:
                title = os.path.basename(dir)
                shutil.copytree(dir, os.path.join(os.path.dirname(__file__), "weather_charts", title), dirs_exist_ok=True)
                md_text += f'- [{title}](./{title}/index.html)\n'
            # weather_chartsディレクトリにindex.htmlを作成
            html_text = markdown.markdown(md_text)
            top_html_path = os.path.join(os.path.dirname(__file__), "weather_charts", "index.html")
            with open(top_html_path, "w", encoding="utf-8") as f:
                f.write(html_text)
            print(f'{len(dirs)} artifacts downloaded and extracted successfully.')
            # デフォルトブラウザでHTMLファイルを開く
            webbrowser.open("file://" + os.path.abspath(top_html_path))

    else:
        print("No artifacts found.")
else:
    print(f"Error: {response.status_code}, {response.text}")

print("Done.")