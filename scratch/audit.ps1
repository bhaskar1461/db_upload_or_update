$json = Get-Content 'C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired.json' -Raw | ConvertFrom-Json

Write-Host "============================================"
Write-Host "  STRUCTURAL ANALYSIS"
Write-Host "============================================"
Write-Host "Total entries: $($json.Count)"

# Per-state stats
$states = $json | ForEach-Object { $_.state } | Sort-Object -Unique
Write-Host "States present: $($states -join ', ')"
Write-Host "States count: $($states.Count)"

foreach ($state in $states) {
    $stateEntries = @($json | Where-Object { $_.state -eq $state })
    $classes = $stateEntries | ForEach-Object { $_.class_name } | Sort-Object -Unique
    Write-Host "`n--- $state ($($stateEntries.Count) entries) ---"
    Write-Host "  Classes present: $($classes -join ', ')"
    Write-Host "  Classes count: $($classes.Count) / 10 required"
    
    # Missing classes
    $allClasses = 1..10 | ForEach-Object { "Class $_" }
    $missing = $allClasses | Where-Object { $_ -notin $classes }
    if ($missing.Count -gt 0) {
        Write-Host "  MISSING CLASSES: $($missing -join ', ')"
    }
    
    foreach ($cls in $classes) {
        $clsEntries = @($stateEntries | Where-Object { $_.class_name -eq $cls })
        $subjects = $clsEntries | ForEach-Object { $_.subject_name }
        Write-Host "    $cls ($($clsEntries.Count) subjects): $($subjects -join '; ')"
    }
}

Write-Host "`n============================================"
Write-Host "  VERIFICATION STATUS"
Write-Host "============================================"
$verified = @($json | Where-Object { $_.verification_status -eq 'VERIFIED' }).Count
$partial = @($json | Where-Object { $_.verification_status -eq 'PARTIALLY_VERIFIED' }).Count
$unverified = @($json | Where-Object { $_.verification_status -eq 'UNVERIFIED' }).Count
Write-Host "VERIFIED: $verified"
Write-Host "PARTIALLY_VERIFIED: $partial"
Write-Host "UNVERIFIED: $unverified"

Write-Host "`n============================================"
Write-Host "  CONFIDENCE SCORES"
Write-Host "============================================"
$scores = $json | ForEach-Object { $_.confidence_score }
$avg = ($scores | Measure-Object -Average).Average
$min = ($scores | Measure-Object -Minimum).Minimum
$max = ($scores | Measure-Object -Maximum).Maximum
Write-Host "Average: $([math]::Round($avg, 1))"
Write-Host "Min: $min"
Write-Host "Max: $max"

$below80 = @($json | Where-Object { $_.confidence_score -lt 80 })
Write-Host "Entries below 80: $($below80.Count)"
foreach ($e in $below80) {
    Write-Host "  [$($e.confidence_score)] $($e.state) > $($e.class_name) > $($e.subject_name): $($e.textbook_name)"
}

Write-Host "`n============================================"
Write-Host "  EMPTY DOWNLOAD LINKS"
Write-Host "============================================"
$emptyLinks = @($json | Where-Object { $_.official_download_link -eq '' })
Write-Host "Entries with empty download link: $($emptyLinks.Count) / $($json.Count)"
foreach ($e in $emptyLinks) {
    Write-Host "  $($e.state) > $($e.class_name) > $($e.subject_name)"
}

Write-Host "`n============================================"
Write-Host "  NON-DIRECT DOWNLOAD LINKS"
Write-Host "============================================"
$portalLinks = @($json | Where-Object { $_.official_download_link -ne '' -and $_.official_download_link -notlike '*.pdf*' })
foreach ($e in $portalLinks) {
    Write-Host "  [$($e.state)] $($e.official_download_link)"
}

Write-Host "`n============================================"
Write-Host "  PLACEHOLDER TEXTBOOK NAME DETECTION"
Write-Host "============================================"
$placeholderPatterns = @('SCERT .+ Textbook', 'SCERT .+ \(Class', 'AP SCERT .+ Textbook', 'AP SCERT .+ Class')
foreach ($e in $json) {
    $idx = [array]::IndexOf($json, $e)
    $name = $e.textbook_name
    $isGeneric = $false
    foreach ($pattern in $placeholderPatterns) {
        if ($name -match $pattern) { $isGeneric = $true; break }
    }
    if ($name -match '^\w+ \w+ .+ Textbook') { $isGeneric = $true }
    if ($name -match 'NCERT Aligned\)$') { $isGeneric = $true }
    if ($name -match 'NCERT-aligned\)$') { $isGeneric = $true }
    
    if ($isGeneric) {
        Write-Host "  [idx=$idx] GENERIC: '$name'"
    }
}

Write-Host "`n============================================"
Write-Host "  NCERT CLAIM ANALYSIS"
Write-Host "============================================"
$ncertEntries = @($json | Where-Object { $_.uses_ncert -eq $true })
Write-Host "Entries claiming NCERT usage: $($ncertEntries.Count)"
$fullNcert = @($ncertEntries | Where-Object { $_.usage_type -eq 'full' }).Count
$partialNcert = @($ncertEntries | Where-Object { $_.usage_type -eq 'partial' }).Count
Write-Host "  Full NCERT: $fullNcert"
Write-Host "  Partial NCERT: $partialNcert"
$isNcertBook = @($ncertEntries | Where-Object { $_.is_ncert_book -eq $true }).Count
$notNcertBook = @($ncertEntries | Where-Object { $_.is_ncert_book -eq $false }).Count
Write-Host "  is_ncert_book=true: $isNcertBook"
Write-Host "  is_ncert_book=false (aligned only): $notNcertBook"

Write-Host "`n============================================"
Write-Host "  DUPLICATE DETECTION"
Write-Host "============================================"
$groups = $json | Group-Object -Property { "$($_.state)|$($_.class_name)|$($_.subject_name)" }
$dupes = @($groups | Where-Object { $_.Count -gt 1 })
Write-Host "Duplicate state+class+subject combos: $($dupes.Count)"
foreach ($d in $dupes) {
    Write-Host "  DUPE: $($d.Name) (count=$($d.Count))"
}

Write-Host "`n============================================"
Write-Host "  REPAIRED FIELDS ANALYSIS"
Write-Host "============================================"
$allRepaired = @()
foreach ($e in $json) {
    $allRepaired += $e.repaired_fields
}
$fieldCounts = $allRepaired | Group-Object | Sort-Object Count -Descending
foreach ($fc in $fieldCounts) {
    Write-Host "  $($fc.Name): repaired in $($fc.Count) entries"
}
