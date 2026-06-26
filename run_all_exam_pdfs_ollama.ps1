$ErrorActionPreference = "Stop"

$Root = "C:\Users\bhask\Desktop\New folder"
$Python = Join-Path $Root "exam_notes_generator\.venv\Scripts\python.exe"
$Script = Join-Path $Root "generate_exam_pdfs.py"
$LogDir = Join-Path $Root "exam_notes_generator\logs"
$LogFile = Join-Path $LogDir "all_exam_generation.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$env:OPENAI_API_KEY = "ollama"
$env:PYTHONIOENCODING = "utf-8"
$env:OLLAMA_FLASH_ATTENTION = "1"
$env:OLLAMA_CONTEXT_LENGTH = "8192"

Set-Location $Root

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting all exam PDF generation with Ollama..." | Tee-Object -FilePath $LogFile
& $Python $Script 2>&1 | Tee-Object -FilePath $LogFile -Append
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Finished." | Tee-Object -FilePath $LogFile -Append
