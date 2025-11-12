# ╔════════════════════════════════════════════════════════════╗
# ║  Rename Emoji Files to ASCII                               ║
# ║  Improves compatibility across systems and git             ║
# ╚════════════════════════════════════════════════════════════╝

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📝 Renaming Emoji Files to ASCII Names                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Mapping of emoji files to new names
$renameMap = @{
    # Lightning bolt (⚡)
    "⚡_DEPLOY_NOW_RUNPOD.md" = "DEPLOY_NOW_RUNPOD.md"
    "⚡_FINAL_DEPLOYMENT_COMMAND.md" = "FINAL_DEPLOYMENT_COMMAND.md"
    "⚡_EXECUTE_DEPLOYMENT_NOW.md" = "EXECUTE_DEPLOYMENT_NOW.md"
    "⚡_START_DEPLOYMENT_HERE.txt" = "START_DEPLOYMENT_HERE.txt"
    "⚡_DOMAIN_FIX_COMPLETE.txt" = "DOMAIN_FIX_COMPLETE.txt"
    "⚡_START_HERE_DOMAIN_FIX.md" = "START_HERE_DOMAIN_FIX.md"
    "⚡_EVERYTHING_DELIVERED_README.md" = "EVERYTHING_DELIVERED_README.md"
    "⚡_START_ALPHA_HERE.md" = "START_ALPHA_HERE.md"
    "⚡_START_HERE_NOW.md" = "START_HERE_NOW.md"
    
    # Party popper (🎉)
    "🎉_IMPLEMENTATION_COMPLETE_FINAL.md" = "IMPLEMENTATION_COMPLETE_FINAL.md"
    "🎉_AI_IMPLEMENTATION_COMPLETE.md" = "AI_IMPLEMENTATION_COMPLETE.md"
    "🎉_ALPHA_LAUNCH_READY.md" = "ALPHA_LAUNCH_READY.md"
    "🎉_IMPLEMENTATION_COMPLETE_WITH_RUNPOD.md" = "IMPLEMENTATION_COMPLETE_WITH_RUNPOD.md"
    "_🎉_ALL_SECURITY_FEATURES_IMPLEMENTED.md" = "ALL_SECURITY_FEATURES_IMPLEMENTED.md"
    "🎉_COMPLETE_NEXUSLANG_V2_SUMMARY.md" = "COMPLETE_NEXUSLANG_V2_SUMMARY.md"
    
    # Confetti ball (🎊)
    "🎊_READY_TO_LAUNCH.md" = "READY_TO_LAUNCH.md"
    "🎊_COMPLETE_IMPLEMENTATION_REPORT.md" = "COMPLETE_IMPLEMENTATION_REPORT.md"
    "🎊_FINAL_STATUS_COMPLETE.md" = "FINAL_STATUS_COMPLETE.md"
    "🎊_IMPLEMENTATION_COMPLETE_FINAL.md" = "IMPLEMENTATION_COMPLETE_FINAL_2.md"
    "🎊_MISSION_ACCOMPLISHED.md" = "MISSION_ACCOMPLISHED.md"
    
    # Checkmark (✅)
    "✅_GITHUB_PUSHED_WHATS_NEXT.md" = "GITHUB_PUSHED_WHATS_NEXT.md"
    "✅_COMPLETE_AI_IMPLEMENTATION.md" = "COMPLETE_AI_IMPLEMENTATION.md"
    "✅_ALL_PHASES_IMPLEMENTED.md" = "ALL_PHASES_IMPLEMENTED.md"
    "✅_ALL_COMPLETE_FINAL_SUMMARY.md" = "ALL_COMPLETE_FINAL_SUMMARY.md"
    "✅_VPS_MIGRATION_SUCCESS_REPORT.md" = "VPS_MIGRATION_SUCCESS_REPORT.md"
    
    # Other emojis
    "⭐_READ_ME_FIRST.md" = "READ_ME_FIRST.md"
    "⭐_START_HERE_NOW.md" = "START_HERE_NOW_2.md"
    "🌐_DEVELOPER_GALION_APP_READY.md" = "DEVELOPER_GALION_APP_READY.md"
    "🌟_COMPLETE_SESSION_ACHIEVEMENTS.md" = "COMPLETE_SESSION_ACHIEVEMENTS.md"
    "🌟_PROJECT_COMPLETE_SUMMARY.md" = "PROJECT_COMPLETE_SUMMARY.md"
    "🎮_DEPLOY_TO_RUNPOD_NOW.md" = "DEPLOY_TO_RUNPOD_NOW.md"
    "🎮_RUNPOD_QUICK_START.md" = "RUNPOD_QUICK_START.md"
    "🎯_COMPLETE_ACTION_PLAN.md" = "COMPLETE_ACTION_PLAN.md"
    "🎯_FINAL_ACTION_CHECKLIST.md" = "FINAL_ACTION_CHECKLIST.md"
    "🎯_IMPLEMENTATION_SUMMARY.md" = "IMPLEMENTATION_SUMMARY.md"
    "🎯_MASTER_LAUNCH_DOCUMENT.md" = "MASTER_LAUNCH_DOCUMENT.md"
    "🎯_QUICK_START_NEXUSLANG_V2.md" = "QUICK_START_NEXUSLANG_V2.md"
    "🏁_FINAL_IMPLEMENTATION_SUMMARY.md" = "FINAL_IMPLEMENTATION_SUMMARY.md"
    "🏁_FINAL_PROJECT_DELIVERY.md" = "FINAL_PROJECT_DELIVERY.md"
    "🏆_MISSION_COMPLETE.md" = "MISSION_COMPLETE.md"
    "🏆_SESSION_COMPLETE_SUMMARY.md" = "SESSION_COMPLETE_SUMMARY.md"
    "👉_WHAT_TO_DO_NEXT.md" = "WHAT_TO_DO_NEXT.md"
    "📊_VISUAL_PROJECT_SUMMARY.md" = "VISUAL_PROJECT_SUMMARY.md"
    "📋_DEPLOY_QUICK_REFERENCE.md" = "DEPLOY_QUICK_REFERENCE.md"
    "📍_YOU_ARE_HERE.md" = "YOU_ARE_HERE.md"
    "📤_PUSH_TO_GITHUB_NOW.md" = "PUSH_TO_GITHUB_NOW.md"
    "🔒_START_HERE_SECURITY.md" = "START_HERE_SECURITY.md"
    "🚀_FINAL_LAUNCH_GUIDE.md" = "FINAL_LAUNCH_GUIDE.md"
    "🚀_GO_LIVE_NOW.md" = "GO_LIVE_NOW.md"
    "🚀_NEXUSLANG_V2_READY_TO_LAUNCH.md" = "NEXUSLANG_V2_READY_TO_LAUNCH.md"
    "🚀_RUNPOD_QUICK_START.md" = "RUNPOD_QUICK_START_2.md"
    "🚀_START_TESTING_NOW.md" = "START_TESTING_NOW.md"
}

$renamedCount = 0
$errors = @()

Write-Host "Found $($renameMap.Count) files to rename" -ForegroundColor Yellow
Write-Host ""

# Rename files
foreach ($oldName in $renameMap.Keys) {
    $newName = $renameMap[$oldName]
    
    # Check if file exists (in root or v2/)
    $filePath = $null
    if (Test-Path $oldName) {
        $filePath = $oldName
    } elseif (Test-Path "v2\$oldName") {
        $filePath = "v2\$oldName"
        $newName = "v2\$newName"
    } elseif (Test-Path "v1\galion\services\galion-alpha\$oldName") {
        $filePath = "v1\galion\services\galion-alpha\$oldName"
        $newName = "v1\galion\services\galion-alpha\$newName"
    }
    
    if ($filePath) {
        try {
            Move-Item -Path $filePath -Destination $newName -Force
            Write-Host "✅ Renamed: $oldName → $newName" -ForegroundColor Green
            $renamedCount++
        } catch {
            Write-Host "❌ Error renaming $oldName : $_" -ForegroundColor Red
            $errors += $oldName
        }
    } else {
        Write-Host "⏭️  Skipped: $oldName (not found)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Renamed: $renamedCount files" -ForegroundColor Green
Write-Host "Errors: $($errors.Count)" -ForegroundColor $(if ($errors.Count -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "Files with errors:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    Write-Host ""
}

Write-Host "Next: Commit changes" -ForegroundColor Yellow
Write-Host "  git add -A" -ForegroundColor Cyan
Write-Host "  git commit -m `"Rename emoji files to ASCII for compatibility`"" -ForegroundColor Cyan
Write-Host ""

