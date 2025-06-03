from langchain_ollama import OllamaLLM
import re
from utils.regex_utils import get_term_for_disorder
from path_utils import POSTS_TOPIC_VALID
# Local model name (You need to pull it with Ollama or other tool first before running this code:
MODEL_NAME = "deepseek-r1:14b" # Using 14b for tests, better to use 32b for more performance

# Instantiate the LLM once and reuse
llm = OllamaLLM(model=MODEL_NAME, temperature=0.0) # Temperature 0.0 because of verbosity of answers

def build_prompt_self_declaration(text: str, disorder: str) -> str:
    """
    A prompt to evaluate whether the text is a self-declaration of the given disorder.

    Parameters:
        text (str): The Reddit post text.
        disorder (str): The disorder to check for self-declaration (e.g., 'schizophrenia').

    Returns:
        str: The prompt string.
    """
    disorder = get_term_for_disorder(disorder)
    return (
        f"Read the Reddit post below and determine if the user is self-declaring "
        f"that they have {disorder}.\n\n"
        f"Post:\n\"{text}\"\n\n"
        f"Answer only 'Yes' if you consider the post to be a self-declaration of {disorder}, "
        f"otherwise answer 'No'."
    )

def build_prompt_topic_analysis(text: str, topic_keywords: str) -> str:
    """
    Build a prompt to determine if a Reddit post is related to mental health, disorders, or pharmacological content.

    Parameters:
        text (str): The Reddit post content.
        topic_keywords (list): Keywords or phrases representing the topic the post was assigned to.

    Returns:
        str: A natural language prompt ready for LLM evaluation.
    """
    # Join topic keywords cleanly
    # topics = ", ".join(topic_keywords)

    # Compose the prompt
    return (
        "You are analyzing Reddit posts to determine if they are related to mental health, mental disorders, or pharmacological topics.\n\n"
        f"Post:\n\"{text}\"\n\n"
        f"Associated topic cluster keywords: {topic_keywords}\n\n"
        "Does the post or its topic indicate any discussion related to mental health, disorders, psychiatric experiences, or medications?\n"
        "Respond only with 'Yes' or 'No'."
    )


def verify_self_declaration_with_llm(text: str, disorder: str) -> bool:
    """
    Uses the local DeepSeek model via Ollama to verify whether a Reddit post
    is a self-declaration of schizophrenia by evaluating content outside <think></think> tags.
    """
    # print("Post text:")
    # print(text)
    # print('Agent response:')
    prompt = build_prompt_self_declaration(text, disorder)
    # print("Prompt:")
    # print(prompt)
    # print('Agent response:')
    try:
        response = llm.invoke(prompt).strip()

        # Remove the content inside <think></think> tags
        # print(response)
        cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()

        # Now evaluate the content outside of <think></think>
        cleaned_response = cleaned_response.lower()
        # print(cleaned_response)

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


import pandas as pd
import re


def verify_topics(posts_file: str, topics_file: str) -> pd.DataFrame:
    """
    Checks if each Reddit post (comment or submission) is about mental health or related topics
    by combining the post content with its associated BERTopic keywords and using an LLM.

    Args:
        posts_file (str): Path to the CSV file with user posts/comments and topic_id.
        topics_file (str): Path to the CSV file mapping (username, topic_id) to topic keywords.

    Returns:
        pd.DataFrame: Updated DataFrame with a new column `relevant_to_mental_health` (True/False).
    """
    # Load data
    df_posts = pd.read_csv(posts_file)
    df_topics = pd.read_csv(topics_file)

    # Create a lookup dictionary: (username, topic_id) -> keywords
    topic_lookup = {
        (row['username'], row['topic_id']): row['topic_label']
        for _, row in df_topics.iterrows()
    }

    # Prepare a new column
    results = []

    for idx, row in df_posts.iterrows():
        username = row['username']
        topic_id = row['topic_id']

        # Skip rows without topic
        if pd.isna(topic_id) or pd.isna(username):
            results.append(False)
            continue

        # Convert topic_id to int if needed
        try:
            topic_id = int(topic_id)
        except:
            results.append(False)
            continue

        topic_keywords = topic_lookup.get((username, topic_id), [])

        # Construct full post text
        if row['type'] == 'submission':
            post_text = f"{row.get('title', '')} {row.get('text', '')}".strip()
        else:
            post_text = row.get('text', '')

        # Generate prompt
        prompt = build_prompt_topic_analysis(post_text, topic_keywords)

        try:
            response = llm.invoke(prompt).strip()
            cleaned_response = cleaned_response.lower()

            # Remove <think> sections
            response = re.sub(r'<think>.*?</think>', '', cleaned_response, flags=re.DOTALL).strip()

            if 'yes' in response:
                results.append(True)
            elif 'no' in response:
                results.append(False)
            else:
                print(f"⚠️ Unclear LLM response at index {idx}: '{response}'")
                results.append(False)

        except Exception as e:
            print(f"❌ LLM failed for row {idx} (user: {username}): {e}")
            results.append(False)

    # Add the result to the DataFrame
    df_posts['is_mental_health'] = results
    df_posts.to_csv(POSTS_TOPIC_VALID, index=False)
    return df_posts
