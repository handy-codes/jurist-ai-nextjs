import sqlite3
import json

def generate_dataset():
    conn = sqlite3.connect('usage_logs.db')
    c = conn.cursor()
    c.execute("SELECT user_query, ai_response FROM logs")
    examples = [{"prompt": q, "completion": a} for q, a in c.fetchall()]
    with open("juristai_finetune.jsonl", "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"{len(examples)} entries saved to juristai_finetune.jsonl")

if __name__ == "__main__":
    generate_dataset()
