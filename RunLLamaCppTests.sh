llamacppDir="/c/LlamaCpp"

export LLAMACPP_BASE_URL="http://localhost:8080"

runTest() {
    local model="$1"
    local modelHuggingFaceUrl="$2"
    local contextSize="$3"

    export LLAMACPP_MODEL_NAME="$model"
    # Run llama.cpp server with vision model
    "$llamacppDir/llama-server.exe" -hf "$modelHuggingFaceUrl" --port 8080 -c "$contextSize" --reasoning-budget 0 -np 1 &
    TaskId=$!

    sleep 300 # The model needs to download and run an empty inference to warm up.

    python MeshBenchmark.py -m "$model" --api-timeout 14400
    
    kill $TaskId

    export LLAMACPP_MODEL_NAME="$model-HighReasoning"
    # Run llama.cpp server with vision model
    "$llamacppDir/llama-server.exe" -hf "$modelHuggingFaceUrl" --port 8080 -c "$contextSize" --reasoning-budget -1 -np 1 &
    TaskId=$!

    sleep 300 # The model needs to download and run an empty inference to warm up.

    python MeshBenchmark.py -m "$model-HighReasoning" --api-timeout 86400
    
    kill $TaskId
}

runTest "LLaVA-1.6-Mistral-7B" "cjpais/llava-1.6-mistral-7b-gguf:Q5_K_M" 32768
runTest "LLaVA-1.6-34B" "cjpais/llava-v1.6-34B-gguf:Q4_K_M" 294912
runTest "LLaVA-1.5-7B" "mys/ggml_llava-v1.5-7b:Q4_K_M" 294912
runTest "LLaVA-1.5-13B" "PsiPi/liuhaotian_llava-v1.5-13b-GGUF:Q5_K_M" 294912
runTest "BakLLaVA-Mistral" "advanced-stack/bakllava-mistral-v1-gguf:Q4_K_M" 294912
runTest "Moondream2" "moondream/moondream2-gguf:F16" 294912
runTest "Phi-3.5-Vision" "abetlen/Phi-3.5-vision-instruct-gguf:Q4_K_M" 294912
runTest "Llama3-LLaVA-Next-8B" "KBlueLeaf/llama3-llava-next-8b-gguf:Q4_K_M" 294912
runTest "Qwen2-VL-72B" "bartowski/Qwen2-VL-72B-Instruct-GGUF:Q4_K_M" 294912
runTest "Mistral-Large-3-675B" "bartowski/mistralai_Mistral-Large-3-675B-Instruct-2512-GGUF:Q4_K_M" 294912
runTest "deepseek-coder-33b-instruct" "RichardErkhov/deepseek-ai_-_deepseek-coder-33b-instruct-gguf:Q6_K" 294912
runTest "deepseek-r1-distill-llama-70b" "DevQuasar/deepseek-ai.DeepSeek-R1-Distill-Llama-70B-GGUF:Q4_K_M" 294912
runTest "deepseek-v2.5" "DevQuasar/deepseek-ai.DeepSeek-V2.5-1210-GGUF:Q4_K_M" 294912
runTest "internlm-s1" "bartowski/internlm_Intern-S1-GGUF:Q4_0" 294912
runTest "Llama-4-Maverick-128E" "Nekotekina/Llama-4-Maverick-17B-128E-Instruct-Projected-Abliterated-GGUF:Q4_K_XL" 294912
runTest "Qwen3-VL-235B-A22B-Thinking" "Qwen/Qwen3-VL-235B-A22B-Thinking-GGUF:Q4_K_M" 294912
runTest "deepseek-vl2" "deepseek-ai/deepseek-vl2" 294912
runTest "deepseek-vl2-small" "deepseek-ai/deepseek-vl2-small" 294912
runTest "deepseek-ocr" "deepseek-ai/deepseek-ocr" 294912
runTest "MiniMax-VL-M2.1" "unsloth/MiniMax-M2.1-GGUF:Q4_0" 294912
runTest "ERNIE-4.5-VL-424B" "gabriellarson/ERNIE-4.5-300B-A47B-PT-GGUF:Q4_K_M" 294912
runTest "Qwen2.5-VL-3B-Instruct" "Mungert/Qwen2.5-VL-3B-Instruct-GGUF:q4_0" 294912
runTest "Qwen2-VL-2B-Instruct" "bartowski/Qwen2-VL-2B-Instruct-GGUF:Q6_K" 32768
runTest "Qwen2-VL-7B-Instruct" "bartowski/Qwen2-VL-7B-Instruct-GGUF:Q5_K_M" 294912
