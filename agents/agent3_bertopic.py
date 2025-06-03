import pandas as pd
from bertopic import BERTopic
import os

USER_ALL_POSTS_COMMENTS = 'data/raw/all_user_data.csv'
USER_TOPIC_SUMMARY = 'data/raw/user_topic_summary.csv'

def model_user_post_topics(input_path=USER_ALL_POSTS_COMMENTS, output_path=USER_ALL_POSTS_COMMENTS,
                           summary_output=USER_TOPIC_SUMMARY):
    # Load user data
    df = pd.read_csv(input_path)

    # Validate structure
    required_columns = {'username', 'type', 'text', 'title'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")

    df['topic_id'] = None  # Add new column to assign topic IDs
    summary_rows = []

    users = df['username'].dropna().unique()

    for username in users:
        user_data = df[df['username'] == username]

        if user_data.empty:
            continue

        # Build document list (combined text for submissions)
        docs = []
        doc_indices = []

        for idx, row in user_data.iterrows():
            if row['type'] == 'comment':
                text = str(row['text']) if pd.notnull(row['text']) else ""
            elif row['type'] == 'submission':
                title = str(row['title']) if pd.notnull(row['title']) else ""
                body = str(row['text']) if pd.notnull(row['text']) else ""
                text = f"{title} {body}"
            else:
                continue

            if text.strip():
                docs.append(text.strip())
                doc_indices.append(idx)

        if not docs:
            continue

        try:
            # Topic modeling
            topic_model = BERTopic(verbose=False)
            topics, _ = topic_model.fit_transform(docs)

            # Assign topics to DataFrame
            for idx, topic in zip(doc_indices, topics):
                df.at[idx, 'topic_id'] = topic

            # Generate labels
            topic_model.generate_topic_labels()
            topic_labels = topic_model.topic_labels_

            # Record user-topic mappings
            for topic_id in set(topics):
                if topic_id == -1:
                    continue  # skip outliers
                summary_rows.append({
                    "username": username,
                    "topic_id": topic_id,
                    "topic_label": topic_labels.get(topic_id, "Unknown")
                })

        except Exception as e:
            print(f"⚠️ BERTopic failed for u/{username}: {str(e)}")
            continue

    # Save enriched user post data
    df.to_csv(output_path, index=False)
    print(f"✅ Updated dataset saved to: {output_path}")

    # Save topic summaries
    if summary_rows:
        os.makedirs(os.path.dirname(summary_output), exist_ok=True)
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(summary_output, index=False)
        print(f"✅ User-topic summary saved to: {summary_output}")
    else:
        print("⚠️ No topic summaries generated.")
