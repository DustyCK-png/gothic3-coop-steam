@echo off
cd /d "%~dp0SteamLink"
G3Steam.exe join --game "%~dp0."
pause
