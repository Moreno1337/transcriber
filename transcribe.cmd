@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul

if "%~1"=="" (
  echo Uso: .\transcribe arquivo.mp4
  echo O arquivo precisa estar na pasta input\
  exit /b 1
)

if not exist "input\%~1" (
  echo Arquivo nao encontrado: input\%~1
  exit /b 1
)

echo [1/3] Transcrevendo...
docker compose run --rm transcriber python transcribe.py "%~1"
if errorlevel 1 (
  echo A transcricao falhou.
  exit /b 1
)

echo.
echo [2/3] Identificando falantes...
docker compose run --rm diarizer python diarize.py "%~1"
if errorlevel 1 (
  echo A identificacao dos falantes falhou.
  exit /b 1
)

echo.
echo [3/3] Combinando transcricao e falantes...
docker compose run --rm transcriber python merge.py "%~1"
if errorlevel 1 (
  echo A combinacao falhou.
  exit /b 1
)

echo.
echo Pronto. Resultado: output\%~n1\transcript_diarized.txt
exit /b 0
