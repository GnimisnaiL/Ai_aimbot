@echo off
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"

D:
cd D:\0326aimbotyolo11n\aimbot
python main.py

:: 使用PowerShell设置窗口位置并运行Python
:: powershell -command "&{$host.UI.RawUI.WindowPosition = New-Object System.Management.Automation.Host.Coordinates 0,0; python main.py}"
