import fetch_data_subreddit
from agents.agent1_identifier import run_agent

# main is used to create a chain that calls all the necessary processes for the system

def main():
    print("tarting the pipeline...")

    # Step 1: Fetch schizophrenia-related data from Reddit
    fetch_data_subreddit.fetch_schizophrenia_data(
        submission_goal=10,
        comment_goal=10
    )
    # Step 2: Run the self-declaration verification agent
    print("Running self-declaration of schizophrenia verification agent (Agent 1)...")
    run_agent()  # This will process the Reddit data and verify self-declarations

main()