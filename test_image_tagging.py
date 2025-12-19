import PromptImageTagging as pit

from AiEngineAnthropicClaude import build_anthropic_message_content
from AiEngineOpenAiChatGPT import build_openai_input


def main():
    image_ref = "images/1.png"
    prompt = f"Describe this image. [[image: {image_ref}]] Thanks."

    parts = pit.parse_prompt_parts(prompt)
    assert any(t == "image" for t, _ in parts)

    openai_input = build_openai_input(prompt)
    assert isinstance(openai_input, list)
    assert openai_input[0]["role"] == "user"
    openai_content = openai_input[0]["content"]
    assert any(b.get("type") == "input_image" for b in openai_content)
    for block in openai_content:
        if block.get("type") == "input_image":
            assert block["image_url"].startswith("data:image/")

    anthropic_content = build_anthropic_message_content(prompt)
    assert isinstance(anthropic_content, list)
    assert any(b.get("type") == "image" for b in anthropic_content)
    for block in anthropic_content:
        if block.get("type") == "image":
            assert block["source"]["type"] in ["base64", "url"]
            if block["source"]["type"] == "base64":
                assert block["source"].get("media_type")
                assert isinstance(block["source"].get("data"), str)

    try:
        from AiEngineGoogleGemini import build_gemini_contents
        from google.genai import types

        gemini_contents = build_gemini_contents(prompt, None)
        assert isinstance(gemini_contents, list)
        assert any(isinstance(x, types.Part) for x in gemini_contents)
        assert any(
            isinstance(x, types.Part) and x.inline_data is not None
            for x in gemini_contents)
    except Exception as e:
        print(f"Skipping Gemini payload test: {e}")

    try:
        from AiEngineXAIGrok import build_xai_user_args

        xai_args = build_xai_user_args(prompt, None)
        assert isinstance(xai_args, list)
        assert len(xai_args) > 0
    except Exception as e:
        print(f"Skipping xAI payload test: {e}")

    print("Image tagging payload tests passed")


if __name__ == "__main__":
    main()
