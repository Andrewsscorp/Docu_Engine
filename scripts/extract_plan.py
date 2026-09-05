import json
with open(r"C:\Users\Hawk\.gemini\antigravity\brain\331ba9b6-c436-4ad1-8124-8faabcb88642\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "Plan de Rescate y Evoluci" in line:
            obj = json.loads(line)
            if obj.get("type") == "USER_INPUT":
                print(obj.get("content"))
                break
