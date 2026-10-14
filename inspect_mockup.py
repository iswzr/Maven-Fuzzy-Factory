import re

with open(r'f:\MAVEN DATA\Maven+Fuzzy+Factory\maven_fuzzy_factory_powerbi_mockup.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all OBJ items:
obj_match = re.search(r'const OBJ=\[(.*?)\];\s*const DIS=', text, re.DOTALL)
if obj_match:
    print("Found OBJ section, length:", len(obj_match.group(1)))

# Find all DIS items:
dis_match = re.search(r'const DIS=\[(.*?)\];\s*const TAB=', text, re.DOTALL)
if dis_match:
    print("Found DIS section, length:", len(dis_match.group(1)))

# Find all DAX items in P:
p_match = re.search(r'const P=\[(.*?)\];\s*/\* ---- calculated columns', text, re.DOTALL)
if p_match:
    print("Found P section, length:", len(p_match.group(1)))
    # extract dax: [ [...] ]
    for m in re.finditer(r"dax:\s*\[\s*\[\s*'([^']+)'\s*,\s*`([^`]+)`\s*\]", p_match.group(1)):
        print("P DAX:", m.group(1))

# Let's inspect DIS:
for m in re.finditer(r"\[\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*(\[[^\]]+\])\s*,\s*(\[.*?\])\s*,\s*`([^`]+)`\s*\]", text, re.DOTALL):
    print("DIS TABLE:", m.group(1), "PAGES:", m.group(2))
    print("DAX:\n", m.group(6)[:200])
    print("-" * 40)
