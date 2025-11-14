#!/bin/bash
clear
echo "======================================"
echo "  GALION PLATFORM - AGENT MONITOR"
echo "======================================"
echo ""

if [ ! -f shared/agent-state.json ]; then
  echo "Error: agent-state.json not found"
  exit 1
fi

STATE=$(cat shared/agent-state.json)

echo "VoiceCore Agent:"
echo "$STATE" | jq -r '.agents.VoiceCore | "  Status: \(.status)\n  Task: \(.current_task)\n  Progress: \(.progress)%"'
echo ""

echo "BackendCore Agent:"
echo "$STATE" | jq -r '.agents.BackendCore | "  Status: \(.status)\n  Task: \(.current_task)\n  Progress: \(.progress)%"'
echo ""

echo "FrontendUI Agent:"
echo "$STATE" | jq -r '.agents.FrontendUI | "  Status: \(.status)\n  Task: \(.current_task)\n  Progress: \(.progress)%"'
echo ""

echo "IntegrationOps Agent:"
echo "$STATE" | jq -r '.agents.IntegrationOps | "  Status: \(.status)\n  Task: \(.current_task)\n  Progress: \(.progress)%"'
echo ""

TOTAL=$(echo "$STATE" | jq '[.agents[].progress] | add / length')
echo "======================================"
echo "  OVERALL PROGRESS: ${TOTAL}%"
echo "======================================"
echo ""

# Check for restart flags
if [ "$STATE" | jq -r '.server_restart_needed' == "true" ]; then
  echo -e "\033[1;33m⚠ SERVER RESTART NEEDED\033[0m"
fi

# Check for conflicts
CONFLICTS=$(echo "$STATE" | jq '.conflicts | length')
if [ "$CONFLICTS" -gt 0 ]; then
  echo -e "\033[0;31m✗ $CONFLICTS CONFLICTS DETECTED\033[0m"
fi
