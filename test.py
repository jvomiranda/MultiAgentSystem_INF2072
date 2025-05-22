from utils.llm_utils import verify_self_declaration_with_llm
from agents.agent2_englishchecker import is_english
from utils.regex_utils import find_declaration_patterns
from fetch_data_subreddit import match_self_declaration
post_text = "My friend has schizophrenia"

if is_english(post_text):
    print("Post is English.")

result = verify_self_declaration_with_llm(post_text, 'sz')
print(f"Model's answer: {result}")


test_strings = [
    "I have schizophrenia.",
    "I'm schizophrenic.",
    "I was diagnosed with schizoaffective disorder in 2020.",
    "My diagnosis is schizophrenia.",
    "I live with schizotypal personality disorder.",
    "I suffer from schizophrenia and depression.",
    "Just dealing with life, no diagnosis.",  # should NOT match
    "My brother has schizophrenia.",
    "I'm bipolar"# should NOT match — not first-person
]

# Get patterns
patterns = find_declaration_patterns('bp')

# Test each string
for i, text in enumerate(test_strings):
    found = any(pattern.search(text) for pattern in patterns)
    print(f"{i+1}. {text}")
    print(f"   ➤ Match: {'✅' if found else '❌'}")

# This file is just for random tests of subprocesses
for t in test_strings:
    match_self_declaration(t, 'sz')