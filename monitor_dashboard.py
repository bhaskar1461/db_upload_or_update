import sys
import os
import json
import re
import time
import subprocess
from pathlib import Path
from collections import OrderedDict
import psutil
import streamlit as st

# Configure page
st.set_page_config(
    page_title="RAG Note Generation Monitor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force stdout to UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"C:\Users\bhask\Desktop\Archive\New folder")
STUDY_MATERIALS_DIR = Path(r"C:\Users\bhask\Desktop\Study Materials")

ENGLISH_MEDIUM = {
    "6th": STUDY_MATERIALS_DIR / "Class 6",
    "7th": STUDY_MATERIALS_DIR / "Class 7",
    "8th": STUDY_MATERIALS_DIR / "Class 8",
    "9th": STUDY_MATERIALS_DIR / "Class 9",
    "11th_Science": BASE_DIR / "English" / "11th & 12th" / "11th Science",
    "11th_Commerce": BASE_DIR / "English" / "11th & 12th" / "11th Commerce",
    "12th_Science": BASE_DIR / "English" / "11th & 12th" / "12th Science",
    "12th_Commerce": BASE_DIR / "English" / "11th & 12th" / "12th Commerce",
}

HINDI_MEDIUM = {
    "6th": BASE_DIR / "Hindi" / "Class 6th",
    "7th": BASE_DIR / "Hindi" / "Class 7th",
    "8th": BASE_DIR / "Hindi" / "Class 8th",
    "9th": BASE_DIR / "Hindi" / "9th Class",
    "11th_Science": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Science"),
    "11th_Commerce": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Commerce"),
    "11th_Humanities": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Humanities"),
    "12th_Science": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Science"),
    "12th_Commerce": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Commerce"),
    "12th_Humanities": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Humanities"),
}


class Chapter:
    def __init__(self, subject: str, subcategory: str, subject_key: str, name: str, path: Path):
        self.subject = subject
        self.subcategory = subcategory
        self.subject_key = subject_key
        self.name = name
        self.path = path

def clean_chapter_name(path: Path) -> str:
    name = re.sub(r"_create$", "", path.stem, flags=re.IGNORECASE)
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    # Strip "Chapter Notes 10." / "Ch Notes 3." style prefixes entirely
    name = re.sub(r"^(Chapter|Ch|CH)\s+Notes\s+\d+\.?\s*", "", name, flags=re.IGNORECASE).strip()
    name = re.sub(r"^(Chapter|Ch|CH)\s*[-_.]\s*", "Chapter ", name, flags=re.IGNORECASE)
    name = re.sub(r"^(Chapter|Ch|CH)\s+(\d+)\s+", r"Chapter \2: ", name, flags=re.IGNORECASE)
    return name

def sort_key(value: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", value)
    return (int(match.group(1)) if match else 999, value.lower())

def has_pdfs(folder: Path) -> bool:
    return folder.is_dir() and any(folder.rglob("*.pdf"))

def dedupe_pdfs(files: list[Path]) -> list[Path]:
    seen: dict[str, Path] = {}
    for file in files:
        stem = re.sub(r"_create$", "", file.stem, flags=re.IGNORECASE)
        current = seen.get(stem)
        if current is None or "_create" not in file.stem.lower():
            seen[stem] = file
    return sorted(seen.values(), key=lambda path: sort_key(path.name))

def collect_chapters(class_dir: Path) -> OrderedDict[str, OrderedDict[str, list[Chapter]]]:
    subjects: OrderedDict[str, OrderedDict[str, list[Chapter]]] = OrderedDict()
    if not class_dir.exists():
        return subjects

    for subject_dir in sorted((p for p in class_dir.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        subject_name = subject_dir.name
        subcats: OrderedDict[str, list[Chapter]] = OrderedDict()

        root_pdfs = [f for f in subject_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
        if root_pdfs:
            chapters = [
                Chapter(subject_name, "_main", subject_name, clean_chapter_name(file), file)
                for file in dedupe_pdfs(root_pdfs)
            ]
            if chapters:
                subcats["_main"] = chapters

        child_pdf_dirs = [
            p for p in sorted(subject_dir.iterdir(), key=lambda x: x.name.lower())
            if has_pdfs(p) and p.name.lower() == "notes"
        ]
        for sub_dir in child_pdf_dirs:
            chapters = [
                Chapter(subject_name, sub_dir.name, f"{subject_name} / {sub_dir.name}", clean_chapter_name(file), file)
                for file in dedupe_pdfs(list(sub_dir.rglob("*.pdf")))
            ]
            if chapters:
                subcats[sub_dir.name] = chapters

        if subcats:
            subjects[subject_name] = subcats
    return subjects

def cache_key(chapter: Chapter) -> str:
    return f"{chapter.subject}||{chapter.subcategory}||{chapter.name}"

# --- Real-Time Resource Monitoring functions ---

def format_bytes(n_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n_bytes < 1024.0:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024.0
    return f"{n_bytes:.1f} PB"

def format_speed(speed_bytes_sec):
    return f"{format_bytes(speed_bytes_sec)}/s"

def get_gpu_usage():
    # Try NVIDIA first (discrete GPU)
    try:
        cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,name", "--format=csv,noheader,nounits"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        parts = [p.strip() for p in output.split(",")]
        if len(parts) >= 6:
            return {
                "active": True,
                "gpu_util": float(parts[0]),
                "mem_util": float(parts[1]),
                "mem_used": float(parts[2]),
                "mem_total": float(parts[3]),
                "temp": float(parts[4]),
                "name": parts[5]
            }
    except Exception:
        pass

    # Fallback: detect integrated GPU (AMD/Intel) via WMI + performance counters
    try:
        # Get GPU name from WMI
        wmi_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notlike \'*GlideX*\' } | Select-Object -First 1 -ExpandProperty Name"'
        gpu_name = subprocess.check_output(wmi_cmd, shell=True, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if not gpu_name:
            return {"active": False}

        # Get GPU utilization via Windows performance counter
        gpu_util = 0.0
        try:
            perf_cmd = 'powershell -NoProfile -Command "try { (Get-Counter \'\\GPU Engine(*engtype_3D)\\Utilization Percentage\' -ErrorAction Stop).CounterSamples | Measure-Object -Property CookedValue -Sum | Select-Object -ExpandProperty Sum } catch { 0 }"'
            util_out = subprocess.check_output(perf_cmd, shell=True, stderr=subprocess.DEVNULL, timeout=5).decode("utf-8").strip()
            gpu_util = min(float(util_out), 100.0) if util_out else 0.0
        except Exception:
            pass

        # Get VRAM from WMI (AdapterRAM in bytes)
        mem_total = 512.0  # default MB
        try:
            vram_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notlike \'*GlideX*\' } | Select-Object -First 1 -ExpandProperty AdapterRAM"'
            vram_out = subprocess.check_output(vram_cmd, shell=True, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if vram_out:
                mem_total = float(vram_out) / (1024 * 1024)  # bytes to MB
        except Exception:
            pass

        return {
            "active": True,
            "gpu_util": gpu_util,
            "mem_util": 0.0,
            "mem_used": 0.0,
            "mem_total": mem_total,
            "temp": 0.0,
            "name": gpu_name
        }
    except Exception:
        pass
    return {"active": False}

def get_cpu_usage():
    cpu_util = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    return {
        "cpu_util": cpu_util,
        "cpu_count": cpu_count,
        "mem_util": mem.percent,
        "mem_used_gb": mem.used / (1024**3),
        "mem_total_gb": mem.total / (1024**3)
    }

def is_generator_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            cmd_str = " ".join(cmdline).lower()
            name = (proc.info.get('name') or "").lower()
            if "rag_batch_generate.py" in cmd_str and "python" in name:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def parse_running_args():
    pid = is_generator_running()
    if not pid:
        return ["6th", "7th", "8th"], ["English", "Hindi"]
    
    try:
        proc = psutil.Process(pid)
        cmdline = proc.cmdline()
        classes = []
        mediums = []
        
        for i, arg in enumerate(cmdline):
            if arg == "--classes":
                for j in range(i+1, len(cmdline)):
                    if cmdline[j].startswith("-"):
                        break
                    classes.append(cmdline[j])
            elif arg == "--mediums":
                for j in range(i+1, len(cmdline)):
                    if cmdline[j].startswith("-"):
                        break
                    mediums.append(cmdline[j])
                    
        if not classes:
            classes = ["6th", "7th", "8th"]
        if not mediums:
            mediums = ["English", "Hindi"]
        return classes, mediums
    except Exception:
        return ["6th", "7th", "8th"], ["English", "Hindi"]

# CSS for a premium dark mode HUD
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background-color: #0b0f19;
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }
    
    /* Header/Title */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.25rem;
        font-family: 'Outfit', sans-serif;
    }
    .metric-detail {
        font-size: 0.8rem;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Status Badge */
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }
    .status-running {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-idle {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Progress Bar */
    .progress-container {
        margin: 1.5rem 0;
    }
    
    /* Custom Scrollbar for Logs */
    .log-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        max-height: 280px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
    }
    
    /* Activity Feed Items */
    .feed-item {
        padding: 8px 12px;
        border-left: 3px solid #6366f1;
        background: rgba(99, 102, 241, 0.03);
        margin-bottom: 6px;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
    }
    .feed-time {
        color: #6366f1;
        font-weight: 700;
        margin-right: 8px;
    }
    .feed-class {
        background: rgba(255, 255, 255, 0.1);
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.72rem;
        margin-right: 6px;
        color: #cbd5e1;
    }
    .feed-chapter {
        color: #e2e8f0;
    }
    
    /* Neon glow progress utility */
    .bar-glow {
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Main Title & Subtitle
st.markdown('<div class="main-header">RAG BATCH PIPELINE HUD</div>', unsafe_allow_html=True)

# Autorefresh toggle
col_header_1, col_header_2 = st.columns([4, 1])
with col_header_1:
    pid = is_generator_running()
    status_class = "status-running" if pid else "status-idle"
    status_text = f"RUNNING (PID: {pid})" if pid else "IDLE"
    st.markdown(
        f'<div class="sub-header">Real-time Pipeline Operations Board &nbsp;&nbsp;'
        f'<span class="status-badge {status_class}">{status_text}</span></div>', 
        unsafe_allow_html=True
    )
with col_header_2:
    autorefresh = st.checkbox("Auto-refresh (0.1s)", value=True)

# Resolve target classes and mediums dynamically with caching and throttling
now = time.time()
if "cached_gpu" not in st.session_state:
    st.session_state.cached_gpu = {"active": False}
if "cached_completed_chapters" not in st.session_state:
    st.session_state.cached_completed_chapters = {}
if "cached_pid" not in st.session_state:
    st.session_state.cached_pid = None
if "last_slow_query" not in st.session_state:
    st.session_state.last_slow_query = 0.0
if "all_chapters_cache" not in st.session_state:
    st.session_state.all_chapters_cache = None
if "stats_history" not in st.session_state:
    st.session_state.stats_history = []

# Update slow items every 1.0 second
if now - st.session_state.last_slow_query >= 1.0 or st.session_state.all_chapters_cache is None:
    pid = is_generator_running()
    if pid != st.session_state.cached_pid or st.session_state.all_chapters_cache is None:
        st.session_state.cached_pid = pid
        # Invalidate/refresh target classes and mediums dynamically
        classes, mediums = parse_running_args()
        
        # Collect target curriculum chapters list
        all_chapters = []
        for medium in mediums:
            source_map = ENGLISH_MEDIUM if medium.lower() == "english" else HINDI_MEDIUM
            for class_name in classes:
                if class_name not in source_map:
                    continue
                class_dir = source_map[class_name]
                try:
                    subjects = collect_chapters(class_dir)
                    for subject, subcats in subjects.items():
                        for subcat, chapters in subcats.items():
                            for chapter in chapters:
                                all_chapters.append({
                                    "class": class_name,
                                    "medium": medium,
                                    "subject": subject,
                                    "subcat": subcat,
                                    "name": chapter.name,
                                    "key": cache_key(chapter)
                                })
                except Exception:
                    pass
        st.session_state.all_chapters_cache = (classes, mediums, all_chapters)
    else:
        classes, mediums, all_chapters = st.session_state.all_chapters_cache
        
    # Query GPU (expensive subprocess)
    st.session_state.cached_gpu = get_gpu_usage()
    
    # Scan cache files for completed chapters (disk read)
    completed_chapters = {}
    cache_notes_content = {}  # Store actual note content for preview
    for medium in mediums:
        for class_name in classes:
            cache_file = BASE_DIR / f"rag_cache_Class_{class_name}_{medium}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for key, notes in data.items():
                            comp_key = f"{class_name}||{medium}||{key}"
                            completed_chapters[comp_key] = {
                                "class": class_name,
                                "medium": medium,
                                "key": key
                            }
                            cache_notes_content[comp_key] = notes
                except Exception:
                    pass
    st.session_state.cached_completed_chapters = completed_chapters
    st.session_state.cached_notes_content = cache_notes_content
    st.session_state.last_slow_query = now

pid = st.session_state.cached_pid
classes, mediums, all_chapters = st.session_state.all_chapters_cache
gpu = st.session_state.cached_gpu
completed_chapters = st.session_state.cached_completed_chapters

total_chapters_count = len(all_chapters)
completed_count = len(completed_chapters)
progress_pct = min(1.0, (completed_count / total_chapters_count)) if total_chapters_count > 0 else 0.0

# Track chronological completions in session state
if "known_completed" not in st.session_state:
    st.session_state.known_completed = set(completed_chapters.keys())
    st.session_state.history = []
    st.session_state.completion_timestamps = []

# Detect newly completed chapters
current_completed_keys = set(completed_chapters.keys())
newly_completed = current_completed_keys - st.session_state.known_completed

if newly_completed:
    for key in newly_completed:
        info = completed_chapters[key]
        # Split key subject||subcategory||chapter
        parts = info["key"].split("||")
        subject = parts[0]
        chapter_name = parts[2] if len(parts) > 2 else parts[-1]
        
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.history.insert(0, {
            "timestamp": timestamp,
            "class": info["class"],
            "medium": info["medium"],
            "subject": subject,
            "chapter": chapter_name
        })
        st.session_state.completion_timestamps.append(now)
        
    # Keep rolling window of last 15 timestamps
    if len(st.session_state.completion_timestamps) > 15:
        st.session_state.completion_timestamps = st.session_state.completion_timestamps[-15:]
        
    st.session_state.known_completed = current_completed_keys

# Track stats history for intelligent sliding window rate estimation
# Filter stats_history to keep only entries from the last 10 minutes
st.session_state.stats_history = [
    (t, c) for (t, c) in st.session_state.stats_history
    if now - t <= 600
]
# Add current entry if it's different from the last one or stats_history is empty
if not st.session_state.stats_history or st.session_state.stats_history[-1][1] != completed_count:
    st.session_state.stats_history.append((now, completed_count))

# Calculate estimated time remaining
remaining_chapters = total_chapters_count - completed_count
avg_sec_per_chapter = None

# Method 1: Sliding window rate from dashboard session history (last 10 minutes)
if len(st.session_state.stats_history) >= 2:
    # Find oldest entry
    old_time, old_count = st.session_state.stats_history[0]
    time_diff = now - old_time
    count_diff = completed_count - old_count
    if count_diff > 0 and time_diff > 5:
        avg_sec_per_chapter = time_diff / count_diff

# Method 2: Process lifetime rate if session has no completions yet
if avg_sec_per_chapter is None and pid:
    try:
        proc = psutil.Process(pid)
        start_time = proc.create_time()
        elapsed = now - start_time
        if elapsed > 10 and completed_count > 0:
            avg_sec_per_chapter = elapsed / completed_count
    except Exception:
        pass

# Method 3: Fallback defaults
if avg_sec_per_chapter is None:
    if pid:
        avg_sec_per_chapter = 15.0  # realistic LLM generation default
    else:
        avg_sec_per_chapter = 0.0

# Calculate ETC string
if not pid:
    etc_str = "Idle"
elif remaining_chapters == 0:
    etc_str = "Completed"
elif avg_sec_per_chapter == 0.0:
    etc_str = "--"
else:
    est_seconds_remaining = remaining_chapters * avg_sec_per_chapter
    if est_seconds_remaining < 60:
        etc_str = f"{int(est_seconds_remaining)}s"
    elif est_seconds_remaining < 3600:
        mins = int(est_seconds_remaining // 60)
        secs = int(est_seconds_remaining % 60)
        etc_str = f"{mins}m {secs}s"
    else:
        hours = int(est_seconds_remaining // 3600)
        mins = int((est_seconds_remaining % 3600) // 60)
        etc_str = f"{hours}h {mins}m"

# Resource Monitoring Data
cpu = get_cpu_usage()
gpu = get_gpu_usage()

# Network Monitoring
net_io = psutil.net_io_counters()
if "initial_net_io" not in st.session_state:
    st.session_state.initial_net_io = net_io

session_recv = net_io.bytes_recv - st.session_state.initial_net_io.bytes_recv
session_sent = net_io.bytes_sent - st.session_state.initial_net_io.bytes_sent

current_time = time.time()
if "last_net_io" not in st.session_state:
    st.session_state.last_net_io = (net_io, current_time)
    st.session_state.last_speeds = (0.0, 0.0)

last_io, last_time = st.session_state.last_net_io
time_diff = current_time - last_time

if time_diff >= 0.5:
    down_speed = (net_io.bytes_recv - last_io.bytes_recv) / time_diff
    up_speed = (net_io.bytes_sent - last_io.bytes_sent) / time_diff
    st.session_state.last_net_io = (net_io, current_time)
    st.session_state.last_speeds = (down_speed, up_speed)
else:
    down_speed, up_speed = st.session_state.last_speeds

# Cooling Fan Speed Estimation
# Estimate RPM based on highest current resource utilization
max_load = max(cpu['cpu_util'], gpu['gpu_util'] if gpu.get('active') else 0.0)
fan_rpm = int(1200 + (max_load / 100.0) * 3800)
# Map max_load (0-100) to spin animation duration (2.0s slow to 0.15s very fast)
duration = max(0.15, 2.0 - (max_load / 100.0) * 1.85)

# Render System Metrics Grid
st.markdown("### 🖥️ System Load & Batch Telemetry")

# Row 1: System Hardware Loads
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

with row1_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Processor Load</div>
        <div class="metric-value">{cpu['cpu_util']:.1f}%</div>
        <div class="metric-detail">{cpu['cpu_count']} Threads Active</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">System RAM</div>
        <div class="metric-value">{cpu['mem_util']:.1f}%</div>
        <div class="metric-detail">{cpu['mem_used_gb']:.1f} GB / {cpu['mem_total_gb']:.1f} GB</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col3:
    if gpu["active"]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">GPU utilization</div>
            <div class="metric-value">{gpu['gpu_util']:.0f}%</div>
            <div class="metric-detail">{gpu['name'][:22]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">GPU utilization</div>
            <div class="metric-value" style="color: #64748b;">OFFLINE</div>
            <div class="metric-detail">No GPU Detected</div>
        </div>
        """, unsafe_allow_html=True)

with row1_col4:
    if gpu["active"]:
        temp_display = f"{gpu['temp']:.0f}°C" if gpu['temp'] > 0 else "N/A"
        vram_detail = f"{gpu['mem_used']:.0f} MB / {gpu['mem_total']:.0f} MB" if gpu['mem_used'] > 0 else f"{gpu['mem_total']:.0f} MB VRAM"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">GPU VRAM & Temp</div>
            <div class="metric-value">{temp_display}</div>
            <div class="metric-detail">{vram_detail}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">GPU Temp</div>
            <div class="metric-value" style="color: #64748b;">--</div>
            <div class="metric-detail">No active GPU sensors</div>
        </div>
        """, unsafe_allow_html=True)

# Inject dynamic CSS animation for fan speed
st.markdown(f"""
<style>
@keyframes spin-fan {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}
.spinning-fan {{
    animation: spin-fan {duration:.3f}s linear infinite;
    transform-origin: 50% 50%;
}}
</style>
""", unsafe_allow_html=True)

# Row 2: Batch Jobs, Cooling, and Network Telemetry
row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.markdown(f"""
    <div class="metric-card" style="border: 1px solid rgba(56, 189, 248, 0.3);">
        <div class="metric-title" style="color: #38bdf8;">Est. Time Remaining</div>
        <div class="metric-value" style="color: #38bdf8;">{etc_str}</div>
        <div class="metric-detail">{remaining_chapters} ch left ({f"{avg_sec_per_chapter:.1f}s/ch" if avg_sec_per_chapter and avg_sec_per_chapter > 0 else "N/A"})</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""
    <div class="metric-card" style="display: flex; align-items: center; justify-content: space-between;">
        <div style="flex-grow: 1;">
            <div class="metric-title">Cooling Fan</div>
            <div class="metric-value">{fan_rpm} RPM</div>
            <div class="metric-detail">Est. Speed (Load: {max_load:.0f}%)</div>
        </div>
        <div style="margin-left: 10px; display: flex; align-items: center; justify-content: center;">
            <svg class="spinning-fan" viewBox="0 0 100 100" width="55" height="55" style="fill: #38bdf8;">
                <circle cx="50" cy="50" r="10" style="fill: #818cf8;"/>
                <path d="M 50 40 C 55 25, 70 15, 65 5 C 60 -5, 45 10, 48 40 Z"/>
                <path d="M 60 50 C 75 55, 85 70, 95 65 C 105 60, 90 45, 60 48 Z"/>
                <path d="M 50 60 C 45 75, 30 85, 35 95 C 40 105, 55 90, 52 60 Z"/>
                <path d="M 40 50 C 25 45, 15 30, 5 35 C -5 40, 10 55, 40 52 Z"/>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

with row2_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Network Usage</div>
        <div class="metric-value">↓ {format_speed(down_speed)} | ↑ {format_speed(up_speed)}</div>
        <div class="metric-detail">Total: {format_bytes(session_recv + session_sent)} | ↓ {format_bytes(session_recv)} | ↑ {format_bytes(session_sent)}</div>
    </div>
    """, unsafe_allow_html=True)

# Render Progress Bar section
st.markdown("### 📊 Notes Generation Progress")
st.progress(progress_pct)
col_pct1, col_pct2 = st.columns([1, 1])
with col_pct1:
    st.markdown(f"**Total Progress:** `{completed_count} / {total_chapters_count}` chapters completed (`{progress_pct * 100:.1f}%`)")
with col_pct2:
    st.markdown(f"<div style='text-align: right;'>Active Target Curriculum: <b>Classes {', '.join(classes)} ({', '.join(mediums)} Medium)</b></div>", unsafe_allow_html=True)

# Layout: Main columns (Completed feed vs Upcoming targets)
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 🔔 Live Activity Feed (Completed Chapters)")
    if st.session_state.history:
        for item in st.session_state.history[:8]: # Show last 8 completed
            st.markdown(
                f'<div class="feed-item">'
                f'<span class="feed-time">[{item["timestamp"]}]</span>'
                f'<span class="feed-class">{item["class"].upper()} {item["medium"].upper()}</span> '
                f'<b>{item["subject"]}</b> &raquo; <span class="feed-chapter">{item["chapter"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        # Fallback: display already completed chapters from cache if history isn't populated yet
        cached_keys = list(completed_chapters.keys())
        if cached_keys:
            st.info("Showing recently loaded cache entries (Waiting for new completions...):")
            for key in cached_keys[-6:]: # last 6
                info = completed_chapters[key]
                parts = info["key"].split("||")
                subject = parts[0]
                chapter_name = parts[2] if len(parts) > 2 else parts[-1]
                st.markdown(
                    f'<div class="feed-item" style="border-left-color: #10b981; background: rgba(16,185,129,0.03);">'
                    f'<span class="feed-time">[LOADED]</span>'
                    f'<span class="feed-class">{info["class"].upper()} {info["medium"].upper()}</span> '
                    f'<b>{subject}</b> &raquo; <span class="feed-chapter">{chapter_name}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<div class='log-container'>Waiting for notes generation to start saving to cache...</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 📋 Next in Queue (Pending)")
    
    # Filter out completed chapters from the total targets
    pending_chapters = []
    for chap in all_chapters:
        comp_key = f"{chap['class']}||{chap['medium']}||{chap['key']}"
        if comp_key not in completed_chapters:
            pending_chapters.append(chap)
            
    if pending_chapters:
        st.markdown(f"**Upcoming Chapters ({len(pending_chapters)} remaining):**")
        # List the next 6 pending chapters
        html_list = ""
        for i, chap in enumerate(pending_chapters[:6]):
            # Highlight first two as they are likely the ones being processed in background (2 workers)
            is_active = i < 2 and pid
            active_style = "border: 1px solid rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);" if is_active else "background: rgba(255,255,255,0.02);"
            active_badge = "<span style='color: #38bdf8; font-weight: bold; font-size: 0.72rem; border: 1px solid #38bdf8; padding: 1px 4px; border-radius: 4px; margin-right: 6px;'>PROCESSING</span>" if is_active else ""
            
            html_list += (
                f'<div style="padding: 10px; margin-bottom: 6px; border-radius: 8px; font-size: 0.85rem; {active_style}">'
                f'{active_badge}'
                f'<span style="color: #94a3b8; font-weight: 600;">{chap["class"].upper()} ({chap["medium"].upper()})</span><br>'
                f'<strong>{chap["subject"]}</strong> &raquo; {chap["name"]}'
                f'</div>'
            )
        st.markdown(html_list, unsafe_allow_html=True)
    else:
        st.success("🎉 All chapters in the batch have been successfully completed!")

# ── Terminal Output Section ──
st.markdown("### 💻 Terminal Output")

_TERM_LOG = BASE_DIR / "batch_generation.log"
if _TERM_LOG.exists():
    try:
        with open(_TERM_LOG, "r", encoding="utf-8", errors="replace") as _tf:
            all_lines = _tf.readlines()
        # Get last 25 non-empty lines
        tail_lines = [l.rstrip() for l in all_lines if l.strip()][-25:]
        
        # Color-code lines for visual clarity
        colored_lines = []
        for line in tail_lines:
            esc_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if "OK:" in line:
                colored_lines.append(f'<span style="color:#4ade80;">  ✓ {esc_line.strip()}</span>')
            elif "Generate:" in line:
                colored_lines.append(f'<span style="color:#38bdf8;">  ⚡ {esc_line.strip()}</span>')
            elif "SKIP cached:" in line:
                colored_lines.append(f'<span style="color:#fbbf24;">  ⏭ {esc_line.strip()}</span>')
            elif "Index " in line:
                colored_lines.append(f'<span style="color:#c084fc;">  📦 {esc_line.strip()}</span>')
            elif "======" in line:
                colored_lines.append(f'<span style="color:#64748b;">{esc_line}</span>')
            elif "Saved:" in line or "Building" in line:
                colored_lines.append(f'<span style="color:#34d399; font-weight:bold;">  ✅ {esc_line.strip()}</span>')
            elif "ERROR" in line or "FAIL" in line or "Traceback" in line:
                colored_lines.append(f'<span style="color:#f87171; font-weight:bold;">  ❌ {esc_line.strip()}</span>')
            elif "Loading weights" in line:
                continue  # skip noisy progress bars
            else:
                colored_lines.append(f'<span style="color:#94a3b8;">{esc_line}</span>')
        
        terminal_html = "<br>".join(colored_lines[-20:])  # show last 20 after filtering
        
        st.markdown(f"""
        <div style="
            background: #0a0e17;
            border: 1px solid rgba(56,189,248,0.15);
            border-radius: 12px;
            padding: 16px;
            font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace;
            font-size: 0.75rem;
            line-height: 1.6;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.4);
        ">
            <div style="color:#475569; margin-bottom:8px; font-size:0.7rem; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:6px;">
                📁 batch_generation.log — {len(all_lines)} lines total — showing last 20
            </div>
            {terminal_html}
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not read log: {e}")
else:
    st.markdown("""
    <div class="metric-card" style="text-align: center; padding: 1.5rem;">
        <div style="color: #64748b; font-size: 0.85rem;">⏳ Waiting for batch_generation.log to be created...</div>
    </div>
    """, unsafe_allow_html=True)

# ── Notes Preview Section ──
st.markdown("### 📝 Live Notes Preview")

import re as _re  # for markdown-to-HTML conversion below

cached_content = st.session_state.get("cached_notes_content", {})
if cached_content:
    # Get the last few entries (most recently added to the dict)
    all_content_keys = list(cached_content.keys())
    # Show the latest 3 entries
    preview_keys = all_content_keys[-3:][::-1]
    
    for pk in preview_keys:
        # Parse the composite key: "class||medium||subject||subcat||chapter"
        parts = pk.split("||")
        class_label = parts[0] if len(parts) > 0 else "?"
        medium_label = parts[1] if len(parts) > 1 else "?"
        # The inner key is "subject||subcat||chapter"
        inner_key = "||".join(parts[2:]) if len(parts) > 2 else pk
        inner_parts = inner_key.split("||")
        subject = inner_parts[0] if len(inner_parts) > 0 else "?"
        chapter = inner_parts[2] if len(inner_parts) > 2 else inner_parts[-1] if inner_parts else "?"
        
        raw_notes = cached_content[pk]
        
        # Convert markdown to styled HTML
        preview_html_lines = []
        for line in raw_notes.split('\n'):
            s = line.strip()
            if not s:
                continue
            # Escape HTML entities
            s_esc = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if s.startswith('# '):
                preview_html_lines.append(f'<div style="font-size:1.1rem; font-weight:700; color:#38bdf8; margin:8px 0 4px;">{s_esc[2:]}</div>')
            elif s.startswith('## '):
                preview_html_lines.append(f'<div style="font-size:0.95rem; font-weight:700; color:#818cf8; margin:10px 0 3px; border-bottom:1px solid rgba(129,140,248,0.2); padding-bottom:3px;">{s_esc[3:]}</div>')
            elif s.startswith('### '):
                preview_html_lines.append(f'<div style="font-size:0.88rem; font-weight:600; color:#a5b4fc; margin:6px 0 2px;">{s_esc[4:]}</div>')
            elif s.startswith('- ') or s.startswith('* '):
                bullet_text = s_esc[2:]
                bullet_text = _re.sub(r'\*\*([^*]+)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', bullet_text)
                preview_html_lines.append(f'<div style="font-size:0.82rem; color:#cbd5e1; padding-left:12px; margin:2px 0;">• {bullet_text}</div>')
            elif s.startswith('  - ') or s.startswith('  * '):
                bullet_text = s_esc.strip().lstrip('-* ')
                bullet_text = _re.sub(r'\*\*([^*]+)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', bullet_text)
                preview_html_lines.append(f'<div style="font-size:0.8rem; color:#94a3b8; padding-left:24px; margin:1px 0;">◦ {bullet_text}</div>')
            else:
                plain = _re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s_esc)
                plain = _re.sub(r'\*([^*]+)\*', r'<em>\1</em>', plain)
                preview_html_lines.append(f'<div style="font-size:0.82rem; color:#cbd5e1; margin:2px 0;">{plain}</div>')
        
        notes_html = '\n'.join(preview_html_lines)
        
        badge_color = "#10b981" if medium_label.lower() == "english" else "#f59e0b"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid {badge_color}; max-height: 350px; overflow-y: auto;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div>
                    <span style="background: {badge_color}22; color: {badge_color}; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; border: 1px solid {badge_color}44;">{class_label} {medium_label}</span>
                    <span style="color: #94a3b8; font-size: 0.78rem; margin-left: 8px;">{subject}</span>
                </div>
                <span style="color: #64748b; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace;">{len(raw_notes)} chars</span>
            </div>
            <div style="font-weight: 600; color: #e2e8f0; font-size: 0.9rem; margin-bottom: 8px;">{chapter}</div>
            <div style="background: rgba(15,23,42,0.5); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.04);">
                {notes_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="metric-card" style="text-align: center; padding: 2rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
        <div style="color: #64748b; font-size: 0.9rem;">No cached notes yet. Notes will appear here as chapters are generated...</div>
    </div>
    """, unsafe_allow_html=True)

# Keep page autorefreshing every 2 seconds if enabled
if autorefresh:
    time.sleep(2)
    st.rerun()
