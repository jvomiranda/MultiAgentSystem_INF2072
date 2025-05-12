from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import warnings

# This agent is used to check if a specific post is written in English

# When this runs, it triggers some library warnings. This is to deactivate them:
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Using a RoBERTa model to analyze if text is in English
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "papluca/xlm-roberta-base-language-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
id2lang = model.config.id2label

def is_english(text, threshold=0.90): # Adjust threshold to need


    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        english_label_id = [k for k, v in id2lang.items() if v == "en"]
        if not english_label_id:
            return False
        english_prob = probs[0, english_label_id[0]].item()
        return english_prob >= threshold