import keyring

# 汎用資格情報から指定したサービス名、ユーザ名のパスワードを取得する

URL ="https://github.com/katonobu/get-weather-charts"
USER = "github-token"

def get_github_token():
    """keyringからGitHubのアクセストークンを取得する"""
    return keyring.get_password(URL, USER)

if __name__ == "__main__":
    if get_github_token() is None:
        print("GitHub token not found in keyring. Please enter your GitHub token:")
        token = input().strip()
        keyring.set_password(URL, USER, token)
        print("GitHub token saved in keyring.")
    else:
        print("GitHub token already set in keyring.")
        token = get_github_token()
        print(f'{token[:3]}{"*"*(len(token)-6)}{token[-3:]}')