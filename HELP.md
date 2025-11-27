# Working Windows 10
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
uvicorn app.api.main:app --reload