from tqdm import tqdm
import pandas as pd
import csv
import utils.llm_utils as llm_utils
from utils.regex_utils import get_disorder_for_term
from agents.agent2_englishchecker import is_english
from utils.path_utils import USER_RECHECK_OTHER_DISORDERS, VERIFIED_USERS_FILE_S2, OUTPUT_FILE_A3, VERIFIED_USERS_FILE
from agents.agent1_identifier import save_verified_post
from fetch_data_user import fetch_user_data_for_other_disorders
import os
import ast

def run_agent_verify_other_disorders(disorder: str):
    """
    Verifies self-declarations for disorders other than the specified one,
    by checking posts with patterns found in USER_RECHECK_OTHER_DISORDERS file,
    calling the LLM with the disorder found from the pattern.

    Parameters:
        disorder (str): The disorder to exclude (like 'sz').
    """

    expected_field_order = [
        "type", "id", "parent_id", "username", "user_flair", "created_utc",
        "title", "text", "score", "upvote_ratio", "num_comments", "subreddit",
        "flair_declared", "text_declared", "any_declared", "is_english", "llm_verified", "pattern_found", "other_mental_declaration"
    ]


    print(f"Agent 3: Starting verification of other disorders")
    users_to_check = []
    mismatch_users = set()


    if os.path.exists(VERIFIED_USERS_FILE):
        with open(VERIFIED_USERS_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                if row:  # check if row is not empty
                    users_to_check.append(row[0])

    print(f'Fetching posts for {len(users_to_check)} users for disorders other than {disorder}')
    fetch_user_data_for_other_disorders(users_to_check, post_limit=None, disorder=disorder)

    # Load DataFrame
    df = pd.read_csv(USER_RECHECK_OTHER_DISORDERS)

    expected_field_order = [
        "type", "id", "parent_id", "username", "user_flair", "created_utc",
        "title", "text", "score", "upvote_ratio", "num_comments", "subreddit",
        "flair_declared", "text_declared", "any_declared", "is_english", "llm_verified", "pattern_found",
        "other_mental_declaration"
    ]

    # tqdm iteration
    for idx, post in tqdm(df.iterrows(), total=len(df), desc="Agent 3"):

        username = post.get("username", "")

        full_text = f"{post.get('title', '')}\n{post.get('text', '')}"

        # Get disorder from pattern_found column
        pattern_term = ast.literal_eval(post.get("pattern_found", ""))

        for pattern_found in pattern_term:
            detected_disorder = get_disorder_for_term(pattern_found)
            if not detected_disorder:
                continue  # skip if no disorder found

            # Check English
            if is_english(full_text):
                df.at[idx, "is_english"] = True

                # Verify self-declaration
                if llm_utils.verify_self_declaration_with_llm(full_text, detected_disorder):
                    df.at[idx, "llm_verified"] = True
                    df.at[idx, "other_mental_declaration"] = True
                    if username in mismatch_users:
                        mismatch_users.remove(username)
                    with open(OUTPUT_FILE_A3, "a", newline='', encoding="utf-8") as f_s2:
                        writer = csv.DictWriter(f_s2, fieldnames=expected_field_order, extrasaction="ignore")
                        save_verified_post(post, writer)

                else:
                    df.at[idx, "llm_verified"] = True
                    df.at[idx, "other_mental_declaration"] = False
                    mismatch_users.add(username)
                    with open(OUTPUT_FILE_A3, "a", newline='', encoding="utf-8") as f_s2:
                        writer = csv.DictWriter(f_s2, fieldnames=expected_field_order, extrasaction="ignore")
                        save_verified_post(post, writer)


            else:
                df.at[idx, "is_english"] = False

    # Step 1: Load existing usernames into a set
    existing_usernames = set()
    if os.path.exists(VERIFIED_USERS_FILE_S2):
        with open(VERIFIED_USERS_FILE_S2, "r", encoding="utf-8") as f_existing:
            for line in f_existing:
                existing_usernames.add(line.strip())

    # Step 2: Append only new usernames
    with open(VERIFIED_USERS_FILE_S2, "a", encoding="utf-8") as f_out:
        for username in set(mismatch_users):
            if username not in existing_usernames:
                f_out.write(f"{username}\n")
    print(
        f"Agent 3: Finished verifying self-declarations for disorders other than {disorder}. Verified posts saved to {VERIFIED_USERS_FILE_S2}")
