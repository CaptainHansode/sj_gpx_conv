@if(0)==(0) ECHO OFF
echo UI file convert
echo.

@REM Py ver
set pyverdir=Python310
set pyside2uicpath=%LOCALAPPDATA%\Programs\Python\%pyverdir%\Scripts

@REM UI File
set in_file=%~dp0sj_gpx_conv.ui
set out_file=%~dp0sj_gpx_conv_ui.py

echo.
echo %pyside2uicpath%\pyside2-uic.exe -o %out_file% %in_file%
%pyside2uicpath%\pyside2-uic.exe -o %out_file% %in_file%
echo.
echo.

pause