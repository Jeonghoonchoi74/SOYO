# 프론트엔드 실행 (새 창)
Start-Process powershell -ArgumentList 'cd frontend; npm run dev'

# 백엔드 실행 (새 창)
Start-Process powershell -ArgumentList 'cd backend; venv\Scripts\Activate.ps1; python app.py' 