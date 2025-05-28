from pathlib import Path
project_root = Path(__file__).parent.parent.resolve().__str__()
USER_RECHECK_OTHER_DISORDERS = project_root + '/data/raw/verified_users_step2_posts_other_disorders.csv'
USER_RECHECK_FILE = project_root + '/data/raw/verified_users_step1_posts.csv' # Users that agent1 flagged "No" for explicit textual self-declaration
OUTPUT_FILE = project_root + '/data/processed/verified_self_declarations.csv' # Self-declarations that agent1 analyzed
VERIFIED_USERS_FILE = project_root + '/data/processed/verified_users_step1.csv' # Username that agent1 flagged "Yes" for explicit self-declarations of target disorder
OUTPUT_FILE_A3 = project_root + '/data/processed/verified_self_declarations_a3.csv' # Self-declarations that agent3 analyzed
VERIFIED_USERS_FILE_S2 = project_root + '/data/processed/verified_users_step2.csv'  # Username2 that agent1 flagged "No" for explicit self-declarations of other mental disorder, thus they pass to next steps
RAW_PATH = project_root + '/data/raw/' # Path to files that did not go through agents yet
