import os

def clean(d):
    for root, _, files in os.walk(d):
        for f in files:
            if not f.endswith(".py"): continue
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8") as cur:
                text = cur.read()
            
            cleaned = False
            while text.endswith("\\n\n"): 
                text = text[:-3] + "\n"
                cleaned = True
            while text.endswith("\\n"): 
                text = text[:-2] + "\n"
                cleaned = True
            
            if cleaned:
                with open(p, "w", encoding="utf-8") as cur:
                    cur.write(text)
                print(f"Cleaned {p}")

clean("c:/Users/adith/OneDrive/Desktop/ayush_health/backend")
clean("c:/Users/adith/OneDrive/Desktop/ayush_health/prakriti_backend")
