@echo off
rem Compila Lynx para MiSTer en la Chameleon96 (revision Lynx_ch96) con Quartus 17.0 desde linea de comandos
set QUARTUS=C:\altera_lite\17.0\quartus\bin64
"%QUARTUS%\quartus_sh.exe" --flow compile Lynx -c Lynx_ch96
if errorlevel 1 goto :error
for /f %%i in ('powershell -nologo -noprofile -command "Get-Date -Format yyyyMMdd"') do set DT=%%i
copy /y output_files\Lynx_ch96.rbf releases\Lynx_%DT%_ch96.rbf >nul
echo Hecho: releases\Lynx_%DT%_ch96.rbf
goto :eof
:error
echo Error de compilacion
exit /b 1
