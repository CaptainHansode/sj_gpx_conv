@if(0)==(0) ECHO OFF
echo UI file convert
echo.

@REM Py ver
set pyverdir=Python310



set pyside2uicpath=%LOCALAPPDATA%\Programs\Python\%pyverdir%\Scripts

@REM UI File
set in_file=%~dp0sj_gpx_conv.ui
set out_file=%~dp0sj_gpx_conv_ui.py

set "target_dir=%UserProfile%\AppData\Local\Programs\Python"
set "filename=pyside2-uic.exe"
set "PYSIDE2_PATH="
for /r "%target_dir%" %%f in (%filename%) do (
    @REM echo %%f | findstr /i /c:"__pycache__" >nul
    if Exist %%f (
        set "PYSIDE2_PATH=%%f" goto :found
    )
)

:found
if defined PYSIDE2_PATH (
    echo ================
    echo Found pyside2-uic.exe file: %PYSIDE2_PATH%
    echo ================
    echo Compile start
    echo %PYSIDE2_PATH% -o %out_file% %in_file%
    %PYSIDE2_PATH% -o %out_file% %in_file%
    echo ================

) else (
    echo File not found.
)

echo.

pause
Rem cmd.exe /K
