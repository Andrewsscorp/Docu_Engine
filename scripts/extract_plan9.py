import json, sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"C:\Users\Hawk\.gemini\antigravity\brain\331ba9b6-c436-4ad1-8124-8faabcb88642\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "1) Tag y backup" in line:
            obj = json.loads(line)
            if obj.get("source") == "MODEL":
                text = obj.get("content")
                if text:
                    idx = text.find("1)")
                    print(text[idx:idx+1000])
                    break
