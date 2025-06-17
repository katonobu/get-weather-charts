@echo off

rem This file is UTF-8 encoded, so we need to update the current code page while executing it
for /f "tokens=2 delims=:." %%a in ('"%SystemRoot%\System32\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" 65001 > nul
)

python --version

cd %~dp0
echo --- venv環境を生成します。 ---
python -m venv .venv

echo --- venv環境に移行します。 ---
call .venv\Scripts\activate.bat

echo --- pipをupgradeします。 ---
python -m pip install --upgrade pip

echo --- 必要なモジュールをインストールします。 ---
pip install -r requirements.txt

echo --- インストール済モジュール一覧を表示します。 ---
pip list

if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" %_OLD_CODEPAGE% > nul
    set _OLD_CODEPAGE=
)
echo --- 終了します。 ---
pause
