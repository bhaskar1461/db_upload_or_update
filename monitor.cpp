#define _WIN32_WINNT 0x0600
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <windows.h>
#include <iomanip>
#include <dirent.h>

#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif

// nlohmann/json for parsing the cache files
#include "json.hpp"
using json = nlohmann::json;

using namespace std;

// Function to calculate CPU usage
static unsigned long long FileTimeToInt64(const FILETIME& ft) {
    return (((unsigned long long)(ft.dwHighDateTime)) << 32) | ((unsigned long long)ft.dwLowDateTime);
}

float GetCPULoad() {
    static FILETIME prevSysIdle, prevSysKernel, prevSysUser;
    static bool firstCall = true;

    FILETIME sysIdle, sysKernel, sysUser;
    if (!GetSystemTimes(&sysIdle, &sysKernel, &sysUser)) return 0.0f;

    if (firstCall) {
        prevSysIdle = sysIdle;
        prevSysKernel = sysKernel;
        prevSysUser = sysUser;
        firstCall = false;
        return 0.0f;
    }

    unsigned long long sysIdleDiff = FileTimeToInt64(sysIdle) - FileTimeToInt64(prevSysIdle);
    unsigned long long sysKernelDiff = FileTimeToInt64(sysKernel) - FileTimeToInt64(prevSysKernel);
    unsigned long long sysUserDiff = FileTimeToInt64(sysUser) - FileTimeToInt64(prevSysUser);

    unsigned long long totalSys = sysKernelDiff + sysUserDiff;
    float cpuLoad = 0.0f;
    if (totalSys > 0) {
        cpuLoad = ((totalSys - sysIdleDiff) * 100.0f) / totalSys;
    }

    prevSysIdle = sysIdle;
    prevSysKernel = sysKernel;
    prevSysUser = sysUser;

    return cpuLoad;
}

// Function to get Memory usage
void GetMemoryUsage(double& used_gb, double& total_gb, float& mem_util) {
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);

    total_gb = memInfo.ullTotalPhys / (1024.0 * 1024.0 * 1024.0);
    double free_gb = memInfo.ullAvailPhys / (1024.0 * 1024.0 * 1024.0);
    used_gb = total_gb - free_gb;
    mem_util = (used_gb / total_gb) * 100.0f;
}

// Function to count completed chapters from all json cache files
int GetCompletedChaptersCount() {
    int count = 0;
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(".")) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            string filename = ent->d_name;
            if (filename.find("rag_cache_Class_") == 0 && filename.find(".json") != string::npos) {
                try {
                    ifstream file(filename);
                    if (file.is_open()) {
                        json j;
                        file >> j;
                        count += j.size();
                    }
                } catch (...) {
                    // Ignore parsing errors
                }
            }
        }
        closedir(dir);
    }
    return count;
}

string MakeProgressBar(float pct, int width) {
    int filled = (int)((pct / 100.0f) * width);
    string bar = "[";
    for(int i=0; i<width; i++) {
        if (i < filled) bar += "=";
        else if (i == filled) bar += ">";
        else bar += " ";
    }
    bar += "]";
    return bar;
}

int main() {
    // Enable ANSI escape codes on Windows 10+
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);

    int total_chapters = 821; // Hardcoded total estimate based on previous batches

    while (true) {
        // Clear screen and move cursor to top-left
        cout << "\033[2J\033[H";

        // Fetch System Telemetry
        float cpu_load = GetCPULoad();
        double mem_used, mem_total;
        float mem_util;
        GetMemoryUsage(mem_used, mem_total, mem_util);

        // Fetch Progress
        int completed = GetCompletedChaptersCount();
        float progress_pct = 0.0f;
        if (total_chapters > 0) {
            progress_pct = ((float)completed / total_chapters) * 100.0f;
            if (progress_pct > 100.0f) progress_pct = 100.0f;
        }

        // Render Dashboard
        cout << "\033[1;36m============================================================\033[0m\n";
        cout << "\033[1;36m              RAG BATCH PIPELINE HUD (C++ TUI)              \033[0m\n";
        cout << "\033[1;36m============================================================\033[0m\n\n";

        cout << "\033[1;33m[ SYSTEM TELEMETRY ]\033[0m\n";
        cout << "  CPU Load:   " << MakeProgressBar(cpu_load, 30) << " " << fixed << setprecision(1) << cpu_load << "%\n";
        cout << "  RAM Usage:  " << MakeProgressBar(mem_util, 30) << " " << fixed << setprecision(1) << mem_used << " GB / " << mem_total << " GB (" << mem_util << "%)\n\n";

        cout << "\033[1;32m[ BATCH PROGRESS ]\033[0m\n";
        cout << "  Completed:  " << completed << " / " << total_chapters << " Chapters\n";
        cout << "  Progress:   " << MakeProgressBar(progress_pct, 40) << " " << fixed << setprecision(1) << progress_pct << "%\n\n";

        if (completed >= total_chapters) {
            cout << "\033[1;32mSTATUS: ALL GENERATION TASKS COMPLETE.\033[0m\n";
        } else {
            cout << "\033[1;36mSTATUS: GENERATING IN BACKGROUND...\033[0m\n";
        }
        
        cout << "\033[1;30m(Press Ctrl+C to exit)\033[0m\n";
        
        Sleep(1000);
    }
    return 0;
}
