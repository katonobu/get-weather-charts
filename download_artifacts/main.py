import os
import glob
import datetime
import requests
import tempfile
import zipfile
import shutil

from io_util import get_github_token, get_artifact_ids, copy_output, append_artifact_info

def download_artifacts():
    # 設定項目
    # 右上のSettings > Developer settings > Fine-grained personal access tokens からトークンを取得
    # Repository access で Only select repositoriesを選択して、DropDownlistでget-weather-chartsを選択
    # Permissions で Actions > Read-only を選択
    GITHUB_TOKEN = get_github_token()
    OWNER = "katonobu"
    REPO = "get-weather-charts"
    API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/artifacts"

    # APIリクエストのヘッダー
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    download_artifact_names = ["long-range-output-zip", "short-range-output-zip"]

    artifact_ids = get_artifact_ids()

    # APIリクエストを送信
    response = requests.get(API_URL, headers=headers)

    # レスポンスを処理
    if response.status_code == 200:
        loaded_artifacts = response.json().get("artifacts", [])
        if loaded_artifacts:
            artifacts = sorted(loaded_artifacts, key=lambda x: datetime.datetime.strptime(x['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f'{len(artifacts)} artifacts found. Downloading and extracting...')
                for artifact in artifacts:#[:min(10, len(artifacts))]:
    #                print(json.dumps(artifact, indent=2, ensure_ascii=False))
                    if artifact["name"] in download_artifact_names and "id" in artifact and "archive_download_url" in artifact:
                        # アーティファクトのIDがまだ保存されていない場合
                        if artifact["id"] not in artifact_ids:

                            print(f'{artifact["name"]} : {artifact["created_at"]} ({artifact["size_in_bytes"]} bytes) id:{artifact["id"]}')
                            archive_url = artifact["archive_download_url"]

                            # ZIPファイルをダウンロード
                            response = requests.get(archive_url, headers=headers, stream=True)
                            if response.status_code == 200:
                                zip_path = os.path.join(temp_dir, f'{artifact["id"]}.zip')
                                with open(zip_path, "wb") as file:
                                    count = 0
                                    for chunk in response.iter_content(chunk_size=8192):
                                        file.write(chunk)
                                        count += 1
                                        if count % 64 == 0:
                                            print('.', flush=True)
                                        else:
                                            print('.', end="", flush=True)
                                    print("O")
                                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                                    zip_ref.extractall(temp_dir)
                                with zipfile.ZipFile(os.path.join(temp_dir, "output.zip"), "r") as zip_ref:
                                    zip_ref.extractall(temp_dir)
                                downloaded_dirs = [item for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isdir(item)]
                                if len(downloaded_dirs) == 1:
                                    src_dir = downloaded_dirs[0]
                                    print(f'copying output from {src_dir}...')
                                    # 結果を出力先にコピー
                                    copy_result_obj = copy_output(src_dir)

                                    # 新しいアーティファクトのIDを追加
                                    append_artifact_info(artifact, src_dir, copy_result_obj)
                                else:
                                    print('Unexpected number of extracted directories.')
                                    break
                                # delete dirs
                                [shutil.rmtree(dir) for dir in downloaded_dirs if os.path.isdir(dir)]
                                # delete files
                                [os.remove(item) for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isfile(item)]
                                pass
                            else:
                                print(f"Error downloading {artifact['name']}: {response.status_code}, {response.text}")
                                continue
                        else:
                            print(f'Skipping {artifact["name"]} {artifact["created_at"]} id:{artifact["id"]} (already downloaded).')
                    else:
                        print(f'Skipping {artifact["name"]} (not in download list or missing ID/archive URL).')

        else:
            print("No artifacts found.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    print("Done.")

if __name__ == "__main__":
    download_artifacts()