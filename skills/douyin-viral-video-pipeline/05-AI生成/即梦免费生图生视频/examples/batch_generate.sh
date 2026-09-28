#!/bin/bash
# Example: Batch generate multiple images from a prompt list
# Usage: bash batch_generate.sh

set -euo pipefail

OUTPUT_DIR="./output"
RATIO="3:4"
REGION="cn"

# Pre-flight check
echo "[*] Checking jimeng token..."
if ! jimeng token check --region "$REGION" 2>/dev/null; then
    echo "[FAIL] Token expired or invalid. Re-login first:"
    echo "  python3 scripts/extract_session.py --login --region $REGION"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Define prompts (one per line)
PROMPTS=(
    "a watercolor painting of a cat reading a book in a cozy library"
    "a cyberpunk city at night with neon lights reflecting in puddles"
    "a serene mountain landscape at golden hour"
    "a cute robot planting flowers in a garden"
    "an underwater scene with colorful coral reef and tropical fish"
)

echo "[*] Generating ${#PROMPTS[@]} images..."

for i in "${!PROMPTS[@]}"; do
    echo ""
    echo "[$((i+1))/${#PROMPTS[@]}] Generating: ${PROMPTS[$i]}"
    
    ATTEMPT=0
    MAX_ATTEMPTS=3
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        ATTEMPT=$((ATTEMPT+1))
        echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS..."
        
        if jimeng image generate \
            --prompt "${PROMPTS[$i]}" \
            --ratio "$RATIO" \
            --region "$REGION" \
            --output-dir "$OUTPUT_DIR" 2>/dev/null; then
            echo "  [OK] Generated successfully"
            break
        else
            echo "  [WARN] Generation failed (attempt $ATTEMPT)"
            if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
                echo "  [FAIL] Max retries reached, skipping"
            fi
            sleep 2
        fi
    done
done

echo ""
echo "[*] Done! Images saved to $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
