@echo off
setlocal
cd /d "C:\Users\bhask\Desktop\New folder"
set PYTHONIOENCODING=utf-8
set OLLAMA_FLASH_ATTENTION=1
set OLLAMA_CONTEXT_LENGTH=16384

REM Class 12 Hindi-medium max-quality RAG run.
REM Generates: Hindi Science, Hindi Commerce, Hindi Humanities only.

echo [%date% %time%] Starting Class 12 Hindi-only RAG batch generation... >> "exam_notes_generator\logs\rag_batch_class_12th_hindi.log"
"C:\Users\bhask\Desktop\New folder\exam_notes_generator\.venv\Scripts\python.exe" "C:\Users\bhask\Desktop\New folder\exam_notes_generator\rag_batch_generate.py" --classes 12th_Science 12th_Commerce 12th_Humanities --mediums Hindi --context-length 16384 --max-tokens 2500 --top-k 15 --chunk-size 1200 --chunk-overlap 200 --temperature 0.15 --pause 0.3 --workers 1 >> "exam_notes_generator\logs\rag_batch_class_12th_hindi.log" 2>&1
echo [%date% %time%] Finished Class 12 Hindi-only RAG batch generation. >> "exam_notes_generator\logs\rag_batch_class_12th_hindi.log"
