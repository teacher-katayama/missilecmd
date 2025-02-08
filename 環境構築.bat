rmdir /s /q .venv
python -m venv --upgrade-deps .venv
call %~dp0.venv\Scripts\activate.bat
pip install -r requirements.txt
pause
