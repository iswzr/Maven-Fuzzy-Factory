import re

with open(r'f:\MAVEN DATA\Maven+Fuzzy+Factory\maven_fuzzy_factory_powerbi_mockup.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see what is inside _Measures in the mockup HTML
meas_match = re.search(r'01 Volume.*?(?=</div>)', text, re.DOTALL)
if meas_match:
    print("Found _Measures section:")
    print(meas_match.group(0))

# Print all P[i].dax blocks
p_match = re.search(r'const P=\[(.*?)\];\s*/\* ---- calculated columns', text, re.DOTALL)
if p_match:
    for m in re.finditer(r"\[\s*'([^']+)'\s*,\s*`([^`]+)`\s*\]", p_match.group(1)):
        print(f"=== PAGE DAX: {m.group(1)} ===")
        print(m.group(2))

# Print all OBJ blocks
obj_match = re.search(r'const OBJ=\[(.*?)\];\s*const DIS=', text, re.DOTALL)
if obj_match:
    for m in re.finditer(r"\[\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*`([^`]+)`\s*\]", obj_match.group(1)):
        print(f"=== OBJ: {m.group(1)} | {m.group(2)} ({m.group(3)}) ===")
        print(m.group(6))
