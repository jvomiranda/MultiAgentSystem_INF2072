from langchain_ollama import OllamaLLM
import re
# Local model name (You need to pull it with Ollama or other tool first before running this code:
MODEL_NAME = "deepseek-r1:14b" # Using 14b for tests, better to use 32b for more performance

# Instantiate the LLM once and reuse
llm = OllamaLLM(model=MODEL_NAME, temperature=0.0) # Temperature 0.0 because of verbosity of answers

def build_prompt(text: str) -> str:
    """
    A prompt to evaluate whether the text is a self-declaration of schizophrenia
    """
    return (
        f"Read the Reddit post below and determine if the user is self-declaring "
        f"that they have schizophrenia.\n\n"
        f"Post:\n\"{text}\"\n\n"
        f"Answer only 'Yes' if you consider the post to be a self-declaration of schizophrenia, "
        f"otherwise answer 'No'."
    )


def verify_self_declaration_with_llm(text: str) -> bool:
    """
    Uses the local DeepSeek model via Ollama to verify whether a Reddit post
    is a self-declaration of schizophrenia by evaluating content outside <think></think> tags.
    """
    print("Post text:")
    print(text)
    print('Agent response:')
    prompt = build_prompt(text)

    try:
        response = llm.invoke(prompt).strip()

        # Remove the content inside <think></think> tags
        print(response)
        cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()

        # Now evaluate the content outside of <think></think>
        cleaned_response = cleaned_response.lower()

        # If the response outside <think></think> indicates "yes" or "no", we process it
        if "yes" in cleaned_response:
            return True
        elif "no" in cleaned_response:
            return False
        else:
            print(f"⚠️ Unexpected content outside <think></think>: {cleaned_response}")
            return False
    except Exception as e:
        print(f"❌ LLM verification failed: {e}")
        return False