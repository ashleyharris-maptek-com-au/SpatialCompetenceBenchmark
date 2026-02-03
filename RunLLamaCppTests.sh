llamacppDir = "/c/LlamaCpp"

set LLAMACPP_BASE_URL=http://localhost:8080

function runTest(model, modelHuggingFaceUrl, mmprojUrl) {
    set LLAMACPP_MODEL_NAME=$model
    # Run llama.cpp server with vision model
    $llamacppDir/llama-server.exe -hf $modelHuggingFaceUrl --port 8080 &
    TaskId=$!

    python MeshBenchmark.py -m $model
    
    kill $TaskId

}

runTest "Qwen2-VL-2B-Instruct-Q6_K" "https://huggingface.co/bartowski/Qwen2-VL-2B-Instruct-GGUF:Q6_K"
runTest "Qwen2.5-VL-3B-Instruct-q4_0" "https://huggingface.co/Mungert/Qwen2.5-VL-3B-Instruct-GGUF:q4_0"
runTest "Qwen2-VL-7B-Instruct-Q5_K_M" "https://huggingface.co/bartowski/Qwen2-VL-7B-Instruct-GGUF:Q5_K_M"
runTest "LLaVA-1.6-Mistral-7B-Q5_K_M" "https://huggingface.co/cjpais/llava-1.6-mistral-7b-gguf:Q5_K_M"
runTest "LLaVA-1.6-34B-Q4_K_M" "https://huggingface.co/cjpais/llava-v1.6-34B-gguf:Q4_K_M"
runTest "LLaVA-1.5-7B" "https://huggingface.co/mys/ggml_llava-v1.5-7b:Q4_K_M"
runTest "LLaVA-1.5-13B-Q5_K_M" "https://huggingface.co/PsiPi/liuhaotian_llava-v1.5-13b-GGUF:Q5_K_M"
runTest "BakLLaVA-Mistral" "https://huggingface.co/advanced-stack/bakllava-mistral-v1-gguf:Q4_K_M"
runTest "Moondream2-F16" "https://huggingface.co/moondream/moondream2-gguf:F16"
runTest "Phi-3.5-Vision" "https://huggingface.co/abetlen/Phi-3.5-vision-instruct-gguf:Q4_K_M"
runTest "Llama3-LLaVA-Next-8B" "https://huggingface.co/KBlueLeaf/llama3-llava-next-8b-gguf:Q4_K_M"
runTest "Qwen2-VL-72B-Instruct-Q4_K_M" "https://huggingface.co/bartowski/Qwen2-VL-72B-Instruct-GGUF:Q4_K_M"
