cd %~dp0
call .venv\Scripts\activate.bat
python download_artifacts.py
pause