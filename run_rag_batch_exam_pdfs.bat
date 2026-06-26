@echo off
setlocal
cd /d "C:\Users\bhask\Desktop\New folder"
set PYTHONIOENCODING=utf-8
set OLLAMA_FLASH_ATTENTION=1

REM ── Maximum Quality Settings ──
REM   context-length=16384 : Let the AI read up to 16k tokens at once (uses ~6GB VRAM)
REM   max-tokens=2500      : Allow the AI to write long, detailed notes per chapter
REM   top-k=15             : Retrieve 15 most relevant chunks per chapter (more context)
REM   chunk-size=1200      : Smart chunk sizes for better semantic boundaries
REM   chunk-overlap=200    : More overlap means less chance of cutting important sentences
REM   temperature=0.15     : Lower = more factual and deterministic output
REM   pause=0.3            : Small pause between chapters to let GPU cool slightly

echo [%date% %time%] Starting RAG batch exam PDF generation (MAX QUALITY)... >> "exam_notes_generator\logs\rag_batch_generation.log"
"C:\Users\bhask\Desktop\New folder\exam_notes_generator\.venv\Scripts\python.exe" "C:\Users\bhask\Desktop\New folder\exam_notes_generator\rag_batch_generate.py" --context-length 16384 --max-tokens 2500 --top-k 15 --chunk-size 1200 --chunk-overlap 200 --temperature 0.15 --pause 0.3 --reindex >> "exam_notes_generator\logs\rag_batch_generation.log" 2>&1
echo [%date% %time%] Finished RAG batch exam PDF generation. >> "exam_notes_generator\logs\rag_batch_generation.log"
