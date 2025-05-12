from utils.llm_utils import verify_self_declaration_with_llm
from agents.agent2_englishchecker import is_english
post_text = "Quero tomar um picolé."

if is_english(post_text):
    print("Post is English.")

result = verify_self_declaration_with_llm(post_text)
print(f"Model's answer: {result}")


# This file is just for random tests of subprocesses