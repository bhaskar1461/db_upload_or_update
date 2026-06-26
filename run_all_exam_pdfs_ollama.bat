@echo off
setlocal
cd /d "C:\Users\bhask\Desktop\New folder"
set OPENAI_API_KEY=ollama
set PYTHONIOENCODING=utf-8
set OLLAMA_FLASH_ATTENTION=1
set OLLAMA_CONTEXT_LENGTH=8192

echo [%date% %time%] Starting all exam PDF generation with Ollama... >> "exam_notes_generator\logs\all_exam_generation.log"
"C:\Users\bhask\Desktop\New folder\exam_notes_generator\.venv\Scripts\python.exe" "C:\Users\bhask\Desktop\New folder\generate_exam_pdfs.py" >> "exam_notes_generator\logs\all_exam_generation.log" 2>&1
echo [%date% %time%] Finished all exam PDF generation. >> "exam_notes_generator\logs\all_exam_generation.log"
