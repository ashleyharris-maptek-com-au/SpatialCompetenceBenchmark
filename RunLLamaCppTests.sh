llamacppDir="/c/LlamaCpp"

export LLAMACPP_BASE_URL="http://localhost:8080"

# Convert shorthand context size to actual number
convertContextSize() {
    local size="$1"
    case "${size,,}" in  # Convert to lowercase for case-insensitive matching
        "4k") echo "4096" ;;
        "8k") echo "8192" ;;
        "16k") echo "16384" ;;
        "32k") echo "32768" ;;
        "64k") echo "65536" ;;
        "128k") echo "131072" ;;
        *) echo "$size" ;;  # Return as-is if no shorthand matches
    esac
}

runTest() {
    local model="$1"
    local modelHuggingFaceUrl="$2"
    local contextSizeList="$3"

    # Convert context size list to array
    IFS=' ' read -ra contextSizes <<< "$contextSizeList"
    
    # Build propagate-to list for each reasoning variant
    local propagateList=""
    local propagateListHR=""
    
    for i in "${!contextSizes[@]}"; do
        if [ $i -gt 0 ]; then
            if [ -n "$propagateList" ]; then
                propagateList="$propagateList,"
                propagateListHR="$propagateListHR,"
            fi
            propagateList="$propagateList$model"
            propagateListHR="$propagateListHR$model-HighReasoning"
        fi
    done

    # Run tests for each context size
    for i in "${!contextSizes[@]}"; do
        local contextSize="${contextSizes[$i]}"
        local actualContextSize=$(convertContextSize "$contextSize")
        
        echo "=== Testing $model at context size $contextSize ($actualContextSize) ==="
        
        # Set up propagation for remaining context sizes
        local currentPropagate=""
        local currentPropagateHR=""
        if [ $i -lt $((${#contextSizes[@]} - 1)) ]; then
            # Get remaining models for propagation
            local remaining=("${contextSizes[@]:$((i + 1))}")
            currentPropagate=""
            currentPropagateHR=""
            for j in "${!remaining[@]}"; do
                local remainingContext="${remaining[$j]}"
                if [ -n "$currentPropagate" ]; then
                    currentPropagate="$currentPropagate,"
                    currentPropagateHR="$currentPropagateHR,"
                fi
                currentPropagate="$currentPropagate$model-$remainingContext"
                currentPropagateHR="$currentPropagateHR$model-$remainingContext-HighReasoning"
            done
        fi

        # Test normal reasoning model
        export LLAMACPP_MODEL_NAME="$model-$contextSize"
        "$llamacppDir/llama-server.exe" -hf "$modelHuggingFaceUrl" --port 8080 -c "$actualContextSize" --reasoning-budget 0 -np 1 --cache-ram 0 &
        TaskId=$!
        
        echo "Waiting for model to warm up..."
        sleep 300
        
        if [ -n "$currentPropagate" ]; then
            echo "Running with propagation to: $currentPropagate"
            python MeshBenchmark.py -m "$model-$contextSize" --api-timeout 28800 --propagate-to "$currentPropagate"
        else
            echo "Running without propagation (last context size)"
            python MeshBenchmark.py -m "$model-$contextSize" --api-timeout 28800
        fi
        
        kill $TaskId
        
        # Test high reasoning model
        export LLAMACPP_MODEL_NAME="$model-$contextSize-HighReasoning"
        "$llamacppDir/llama-server.exe" -hf "$modelHuggingFaceUrl" --port 8080 -c "$actualContextSize" --reasoning-budget -1 -np 1 --cache-ram 0 &
        TaskId=$!
        
        echo "Waiting for high reasoning model to warm up..."
        sleep 300
        
        if [ -n "$currentPropagateHR" ]; then
            echo "Running high reasoning with propagation to: $currentPropagateHR"
            python MeshBenchmark.py -m "$model-$contextSize-HighReasoning" --api-timeout 86400 --propagate-to "$currentPropagateHR"
        else
            echo "Running high reasoning without propagation (last context size)"
            python MeshBenchmark.py -m "$model-$contextSize-HighReasoning" --api-timeout 86400
        fi
        
        kill $TaskId
        
        echo "=== Completed $model at context size $contextSize ==="
        echo
    done
}

# Models that scored 0 on first run:
runTest "Qwen3-Coder-Next" "Qwen/Qwen3-Coder-Next-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "LLaVA-1.5-7B" "mys/ggml_llava-v1.5-7b:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "LLaVA-1.5-13B" "PsiPi/liuhaotian_llava-v1.5-13b-GGUF:Q5_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "Llama3-LLaVA-Next-8B" "KBlueLeaf/llama3-llava-next-8b-gguf:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "Qwen2-VL-72B" "bartowski/Qwen2-VL-72B-Instruct-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "Mistral-Large-3-675B" "bartowski/mistralai_Mistral-Large-3-675B-Instruct-2512-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-coder-33b-instruct" "RichardErkhov/deepseek-ai_-_deepseek-coder-33b-instruct-gguf:Q6_K" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-r1-distill-llama-70b" "DevQuasar/deepseek-ai.DeepSeek-R1-Distill-Llama-70B-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-v2.5" "DevQuasar/deepseek-ai.DeepSeek-V2.5-1210-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "internlm-s1" "bartowski/internlm_Intern-S1-GGUF:Q4_0" "4k 8k 16k 32k 64k 128k"
# runTest "Llama-4-Maverick-128E" "Nekotekina/Llama-4-Maverick-17B-128E-Instruct-Projected-Abliterated-GGUF:Q4_K_XL" "4k 8k 16k 32k 64k 128k"
runTest "Qwen3-VL-235B-A22B-Thinking" "Qwen/Qwen3-VL-235B-A22B-Thinking-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-vl2" "deepseek-ai/deepseek-vl2" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-vl2-small" "deepseek-ai/deepseek-vl2-small" "4k 8k 16k 32k 64k 128k"
# runTest "deepseek-ocr" "deepseek-ai/deepseek-ocr" "4k 8k 16k 32k 64k 128k"
# runTest "MiniMax-VL-M2.1" "unsloth/MiniMax-M2.1-GGUF:Q4_0" "4k 8k 16k 32k 64k 128k"
# runTest "ERNIE-4.5-VL-424B" "gabriellarson/ERNIE-4.5-300B-A47B-PT-GGUF:Q4_K_M" "4k 8k 16k 32k 64k 128k"

# Models which don't appear to have ever run?
runTest "BakLLaVA-Mistral" "advanced-stack/bakllava-mistral-v1-gguf:Q4_K_M" "4k 8k 16k 32k 64k 128k"

# Models that have scored > 0 (and are worth keeping):
runTest "LLaVA-1.6-Mistral-7B" "cjpais/llava-1.6-mistral-7b-gguf:Q5_K_M" "4k 8k 16k 32k"
runTest "LLaVA-1.6-34B" "cjpais/llava-v1.6-34B-gguf:Q4_K_M" "4k 8k 16k 32k 64k 128k"
runTest "Qwen2.5-VL-3B-Instruct" "Mungert/Qwen2.5-VL-3B-Instruct-GGUF:q4_0" "4k 8k 16k 32k 64k 128k"
runTest "Qwen2-VL-2B-Instruct" "bartowski/Qwen2-VL-2B-Instruct-GGUF:Q6_K" "4k 8k 16k 32k"
runTest "Qwen2-VL-7B-Instruct" "bartowski/Qwen2-VL-7B-Instruct-GGUF:Q5_K_M" "4k 8k 16k 32k 64k 128k"