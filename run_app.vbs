Set WshShell = CreateObject("WScript.Shell")  
WshShell.Run "cmd /c cd /d ""C:\Users\Narek\Desktop\ai_tutor"" && python -m streamlit run app.py --server.headless true", 0, False  
WScript.Sleep 2000  
WshShell.Run "msedge --app=http://localhost:8501", 0, False 
