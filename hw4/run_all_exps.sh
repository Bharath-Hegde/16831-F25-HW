#!/bin/bash

# Script to run all experiments from exps_to_run.txt sequentially
# Continues even if one fails, and logs all output

# Get the directory where this script is located (should be hw4/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

EXP_FILE="exps_to_run.txt"
LOG_DIR="exp_logs"
COMBINED_LOG="${LOG_DIR}/all_experiments.log"
SUMMARY_LOG="${LOG_DIR}/summary.log"

# Check if exp file exists
if [ ! -f "${EXP_FILE}" ]; then
    echo "ERROR: ${EXP_FILE} not found!"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check for required commands
if ! command -v bc &> /dev/null; then
    echo "ERROR: 'bc' command not found. Please install it."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "ERROR: 'uv' command not found. Please install it."
    exit 1
fi

# Create log directory
mkdir -p "${LOG_DIR}"

echo "Working directory: $(pwd)"
echo "Experiment file: ${EXP_FILE}"
echo ""

# Wait for existing experiment to finish
# Based on: iteration 9 of 16, 2603.08 seconds elapsed
CURRENT_ITER=9
TOTAL_ITERS=16
TIME_ELAPSED=2603.08

# Calculate estimated completion time
TIME_PER_ITER=$(echo "scale=2; ${TIME_ELAPSED} / ${CURRENT_ITER}" | bc)
if [ -z "${TIME_PER_ITER}" ] || [ "${TIME_PER_ITER}" = "0" ]; then
    echo "ERROR: Failed to calculate time per iteration"
    exit 1
fi

REMAINING_ITERS=$((TOTAL_ITERS - CURRENT_ITER))
ESTIMATED_REMAINING=$(echo "scale=2; ${TIME_PER_ITER} * ${REMAINING_ITERS}" | bc)
ESTIMATED_TOTAL=$(echo "scale=2; ${TIME_ELAPSED} + ${ESTIMATED_REMAINING}" | bc)
# Add 30% buffer for safety
WAIT_TIME=$(echo "scale=0; ${ESTIMATED_TOTAL} * 1.3 / 1" | bc)

if [ -z "${WAIT_TIME}" ] || [ "${WAIT_TIME}" -le 0 ]; then
    echo "ERROR: Invalid wait time calculated: ${WAIT_TIME}"
    exit 1
fi

WAIT_HOURS=$(echo "scale=1; ${WAIT_TIME} / 3600" | bc)
WAIT_MINS=$(echo "scale=0; (${WAIT_TIME} % 3600) / 60" | bc)

echo "=========================================="
echo "Waiting for existing experiment to finish"
echo "=========================================="
echo "Current progress: iteration ${CURRENT_ITER} of ${TOTAL_ITERS}"
echo "Time elapsed: ${TIME_ELAPSED} seconds"
echo "Estimated time per iteration: ${TIME_PER_ITER} seconds"
echo "Estimated remaining time: ${ESTIMATED_REMAINING} seconds"
echo "Total estimated time: ${ESTIMATED_TOTAL} seconds"
echo "Waiting ${WAIT_TIME} seconds (${WAIT_HOURS} hours, ${WAIT_MINS} minutes) with buffer..."
EXPECTED_START=$(date -d "+${WAIT_TIME} seconds" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "N/A (unable to calculate)")
echo "Expected start time: ${EXPECTED_START}"
echo ""

# Countdown display
while [ ${WAIT_TIME} -gt 0 ]; do
    HOURS=$((WAIT_TIME / 3600))
    MINS=$(((WAIT_TIME % 3600) / 60))
    SECS=$((WAIT_TIME % 60))
    printf "\rWaiting... %02d:%02d:%02d remaining" ${HOURS} ${MINS} ${SECS}
    sleep 60
    WAIT_TIME=$((WAIT_TIME - 60))
done
printf "\rWaiting... 00:00:00 remaining - Starting experiments now!\n"
echo ""

# Initialize summary
echo "=== Experiment Run Summary ===" > "${SUMMARY_LOG}"
echo "Started at: $(date)" >> "${SUMMARY_LOG}"
echo "" >> "${SUMMARY_LOG}"

# Counter for experiments
EXP_NUM=0
SUCCESS_COUNT=0
FAIL_COUNT=0

# Trap to handle script interruption
trap 'echo ""; echo "Script interrupted at $(date)"; echo "Processed ${EXP_NUM} experiments (${SUCCESS_COUNT} successful, ${FAIL_COUNT} failed)"; exit 130' INT TERM

# Check if there are any experiments to run
if ! grep -q "^python" "${EXP_FILE}" 2>/dev/null; then
    echo "WARNING: No experiments found in ${EXP_FILE}"
    echo "Make sure the file contains lines starting with 'python'"
    exit 1
fi

# Read and execute each line
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    [[ -z "${line// }" ]] && continue
    
    EXP_NUM=$((EXP_NUM + 1))
    
    # Extract experiment name for individual log file
    EXP_NAME=$(echo "$line" | grep -oP -- '--exp_name \K\S+' || echo "exp_${EXP_NUM}")
    INDIVIDUAL_LOG="${LOG_DIR}/${EXP_NAME}.log"
    
    # Replace 'python' with 'uv run python' in the command
    COMMAND=$(echo "$line" | sed 's/^python/uv run python/')
    
    echo ""
    echo "=========================================="
    echo "Running experiment ${EXP_NUM}: ${EXP_NAME}"
    echo "Command: ${COMMAND}"
    echo "=========================================="
    echo ""
    
    # Log to summary
    echo "[${EXP_NUM}] ${EXP_NAME}" >> "${SUMMARY_LOG}"
    echo "  Command: ${COMMAND}" >> "${SUMMARY_LOG}"
    echo "  Started: $(date)" >> "${SUMMARY_LOG}"
    
    # Run the command, tee output to both combined and individual logs, and show on screen
    # Use set +e to continue on error
    set +e
    eval "${COMMAND}" 2>&1 | tee -a "${COMBINED_LOG}" | tee "${INDIVIDUAL_LOG}"
    EXIT_CODE=${PIPESTATUS[0]}
    set -e
    
    # Log result
    if [ ${EXIT_CODE} -eq 0 ]; then
        echo "  Status: SUCCESS" >> "${SUMMARY_LOG}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo ""
        echo "✓ Experiment ${EXP_NUM} (${EXP_NAME}) completed successfully"
    else
        echo "  Status: FAILED (exit code: ${EXIT_CODE})" >> "${SUMMARY_LOG}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
        echo "✗ Experiment ${EXP_NUM} (${EXP_NAME}) failed with exit code ${EXIT_CODE}"
    fi
    
    echo "  Finished: $(date)" >> "${SUMMARY_LOG}"
    echo "" >> "${SUMMARY_LOG}"
    
    # Add separator to combined log
    echo "" >> "${COMBINED_LOG}"
    echo "==========================================" >> "${COMBINED_LOG}"
    echo "End of experiment: ${EXP_NAME}" >> "${COMBINED_LOG}"
    echo "==========================================" >> "${COMBINED_LOG}"
    echo "" >> "${COMBINED_LOG}"
    
done < "${EXP_FILE}"

# Final summary
echo ""
echo "=========================================="
echo "All experiments completed!"
echo "=========================================="
echo "Total experiments: ${EXP_NUM}"
echo "Successful: ${SUCCESS_COUNT}"
echo "Failed: ${FAIL_COUNT}"
echo ""
echo "Logs saved in: ${LOG_DIR}/"
echo "  - Combined log: ${COMBINED_LOG}"
echo "  - Summary: ${SUMMARY_LOG}"
echo "  - Individual logs: ${LOG_DIR}/*.log"
echo ""

# Append final summary to summary log
echo "=== Final Summary ===" >> "${SUMMARY_LOG}"
echo "Total experiments: ${EXP_NUM}" >> "${SUMMARY_LOG}"
echo "Successful: ${SUCCESS_COUNT}" >> "${SUMMARY_LOG}"
echo "Failed: ${FAIL_COUNT}" >> "${SUMMARY_LOG}"
echo "Finished at: $(date)" >> "${SUMMARY_LOG}"

