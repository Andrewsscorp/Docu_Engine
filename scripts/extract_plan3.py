import json
with open(r"C:\Users\Hawk\.gemini\antigravity\brain\331ba9b6-c436-4ad1-8124-8faabcb88642\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "PLAN DE RESCATE Y EVOLUCI" in line:
            obj = json.loads(line)
            if obj.get("type") == "USER_INPUT":
                text = obj.get("content")
                print(text[:2000])
                print("\n\n... skipping to parts ...\n\n")
                
                # Extract the 20 parts
                import re
                parts = re.findall(r"(?i)(parte \d+:.*?\n.*?(?=parte \d+:|$))", text, re.DOTALL)
                for p in parts[:12]:
                    print(p[:200].strip())
                    print("---")
                break
