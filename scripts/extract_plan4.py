import json, sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"C:\Users\Hawk\.gemini\antigravity\brain\331ba9b6-c436-4ad1-8124-8faabcb88642\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "PLAN DE RESCATE" in line:
            obj = json.loads(line)
            if obj.get("type") == "USER_INPUT":
                text = obj.get("content")
                
                # We divided it into 20 parts. Let's find what Part 9 is.
                # Actually, the user's document was 17 parts, we divided it into 20.
                print("DOCUMENT FOUND. Printing lines mentioning '9.' or 'Parte'")
                for l in text.split('\n'):
                    if '9' in l or '8' in l or '10' in l or 'Parte' in l:
                        print(l.strip())
                break
