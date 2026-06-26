$json = Get-Content 'C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired.json' -Raw | ConvertFrom-Json
Write-Host "Total entries: $($json.Count)"

$states = $json | ForEach-Object { $_.state } | Sort-Object -Unique
Write-Host "States: $($states -join ', ')"

$verified = @($json | Where-Object { $_.verification_status -eq 'VERIFIED' }).Count
$partial = @($json | Where-Object { $_.verification_status -eq 'PARTIALLY_VERIFIED' }).Count
Write-Host "VERIFIED: $verified"
Write-Host "PARTIALLY_VERIFIED: $partial"

$scores = $json | ForEach-Object { $_.confidence_score }
$avg = ($scores | Measure-Object -Average).Average
Write-Host "Average confidence: $([math]::Round($avg, 1))"

# Check required fields
$required = @('state','board_name','class_name','subject_name','uses_ncert','usage_type','is_ncert_book','textbook_name','publisher','medium','official_download_link','academic_year','pdf_available','source_website','notes','repaired_fields','confidence_score','verification_status')

$missingFields = @()
foreach ($entry in $json) {
    $entryFields = $entry | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
    foreach ($req in $required) {
        if ($req -notin $entryFields) {
            $missingFields += "$($entry.state) > $($entry.class_name) > $($entry.subject_name): missing '$req'"
        }
    }
}

if ($missingFields.Count -eq 0) {
    Write-Host "ALL REQUIRED FIELDS PRESENT"
} else {
    Write-Host "Missing fields:"
    $missingFields | ForEach-Object { Write-Host "  $_" }
}

# Per state breakdown
foreach ($state in $states) {
    $stateEntries = @($json | Where-Object { $_.state -eq $state })
    $classes = $stateEntries | ForEach-Object { $_.class_name } | Sort-Object -Unique
    Write-Host ""
    Write-Host "=== $state ==="
    Write-Host "  Entries: $($stateEntries.Count)"
    Write-Host "  Classes: $($classes -join ', ')"
    foreach ($cls in $classes) {
        $clsEntries = @($stateEntries | Where-Object { $_.class_name -eq $cls })
        $subjects = $clsEntries | ForEach-Object { $_.subject_name }
        Write-Host "    $cls ($($clsEntries.Count) subjects): $($subjects -join '; ')"
    }
}
