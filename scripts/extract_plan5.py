import json, sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"C:\Users\Hawk\.gemini\antigravity\brain\331ba9b6-c436-4ad1-8124-8faabcb88642\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "PLAN DE RESCATE" in line:
            obj = json.loads(line)
            if obj.get("type") == "USER_INPUT":
                text = obj.get("content")
                print(text[text.find("Auditor"):text.find("Auditor")+1000])
                break
