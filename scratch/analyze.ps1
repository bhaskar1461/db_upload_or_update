$json = Get-Content 'C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check.json' -Raw | ConvertFrom-Json

Write-Host "=== STRUCTURAL ANALYSIS ==="
Write-Host "Total top-level entries: $($json.Count)"
Write-Host ""

foreach ($entry in $json) {
    Write-Host "--- State: $($entry.state) ---"
    Write-Host "  Board: $($entry.board_name)"
    Write-Host "  Website: $($entry.official_board_website)"
    Write-Host "  Classes: $($entry.classes.Count)"
    
    $fields = $entry | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
    Write-Host "  Top-level fields: $($fields -join ', ')"
    
    foreach ($cls in $entry.classes) {
        $subjCount = 0
        if ($cls.subjects) { $subjCount = $cls.subjects.Count }
        $linkCount = 0
        if ($cls.official_source_links) { $linkCount = $cls.official_source_links.Count }
        
        Write-Host "    $($cls.class): uses_ncert=$($cls.uses_ncert), adoption=$($cls.adoption_type), subjects=$subjCount, source_links=$linkCount"
        
        $clsFields = $cls | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
        Write-Host "      Fields: $($clsFields -join ', ')"
        
        if ($cls.subjects) {
            foreach ($subj in $cls.subjects) {
                $subjFields = $subj | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
                Write-Host "        Subject: $($subj.subject) | Book: $($subj.book_name) | Type: $($subj.book_type) | Link: $($subj.official_download_link)"
                Write-Host "          Fields: $($subjFields -join ', ')"
            }
        }
    }
    Write-Host ""
}

# Check required fields per specification
Write-Host "=== REQUIRED FIELDS CHECK (per spec) ==="
$requiredTopLevel = @('state', 'board_name', 'class_name', 'subject_name', 'uses_ncert', 'usage_type', 'is_ncert_book', 'textbook_name', 'publisher', 'medium', 'official_download_link', 'academic_year', 'pdf_available', 'source_website', 'notes')

Write-Host "Required fields per spec: $($requiredTopLevel -join ', ')"
Write-Host ""
Write-Host "SCHEMA MISMATCH: The dataset uses a NESTED structure (state > classes > subjects)"
Write-Host "but the spec requires a FLAT structure with these fields per entry."
Write-Host ""

# Collect all unique URLs
Write-Host "=== ALL URLS IN DATASET ==="
$allUrls = @()
foreach ($entry in $json) {
    if ($entry.official_board_website) { $allUrls += $entry.official_board_website }
    foreach ($cls in $entry.classes) {
        if ($cls.official_source_links) {
            foreach ($link in $cls.official_source_links) {
                $allUrls += $link
            }
        }
        if ($cls.subjects) {
            foreach ($subj in $cls.subjects) {
                if ($subj.official_download_link) {
                    $allUrls += $subj.official_download_link
                }
            }
        }
    }
}
$uniqueUrls = $allUrls | Sort-Object -Unique
Write-Host "Total URLs: $($allUrls.Count), Unique: $($uniqueUrls.Count)"
foreach ($url in $uniqueUrls) {
    Write-Host "  $url"
}

# Check empty download links
Write-Host ""
Write-Host "=== EMPTY DOWNLOAD LINKS ==="
$emptyCount = 0
foreach ($entry in $json) {
    foreach ($cls in $entry.classes) {
        if ($cls.subjects) {
            foreach ($subj in $cls.subjects) {
                if ([string]::IsNullOrWhiteSpace($subj.official_download_link)) {
                    Write-Host "  EMPTY: $($entry.state) > $($cls.class) > $($subj.subject)"
                    $emptyCount++
                }
            }
        }
    }
}
Write-Host "Total empty download links: $emptyCount"

# Check empty subjects arrays
Write-Host ""
Write-Host "=== EMPTY SUBJECTS ARRAYS ==="
$emptySubjCount = 0
foreach ($entry in $json) {
    foreach ($cls in $entry.classes) {
        if (-not $cls.subjects -or $cls.subjects.Count -eq 0) {
            Write-Host "  EMPTY SUBJECTS: $($entry.state) > $($cls.class)"
            $emptySubjCount++
        }
    }
}
Write-Host "Total classes with empty subjects: $emptySubjCount"
