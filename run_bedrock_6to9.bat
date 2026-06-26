@echo off
setlocal
cd /d "C:\Users\bhask\Desktop\Archive\New folder"
set PYTHONIOENCODING=utf-8
set OLLAMA_FLASH_ATTENTION=1

REM Bedrock Config
set BEDROCK_API_KEY=YOUR_BEDROCK_API_KEY_HERE
set AWS_BEARER_TOKEN_BEDROCK=%BEDROCK_API_KEY%
set BEDROCK_REGION=us-east-1
set BEDROCK_MODEL=deepseek.v3.2
set LLM_PROVIDER=bedrock

echo [%date% %time%] Starting Class 6-9 English Bedrock RAG generation... >> "exam_notes_generator\logs\bedrock_class_6_to_9.log"
"C:\Users\bhask\Desktop\Archive\New folder\exam_notes_generator\.venv\Scripts\python.exe" "C:\Users\bhask\Desktop\Archive\New folder\exam_notes_generator\rag_batch_generate.py" --classes 6th 7th 8th 9th --mediums English --context-length 16384 --max-tokens 4000 --top-k 15 --chunk-size 1200 --chunk-overlap 200 --temperature 0.15 --pause 1.0 --workers 8 --reindex >> "exam_notes_generator\logs\bedrock_class_6_to_9.log" 2>&1
echo [%date% %time%] Finished generation. >> "exam_notes_generator\logs\bedrock_class_6_to_9.log"
