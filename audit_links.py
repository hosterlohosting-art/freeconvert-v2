import os, re

tool_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and os.path.exists(os.path.join(d,'index.html'))]
link_counts = {}
for d in tool_dirs:
    c = open(os.path.join(d,'index.html'), encoding='utf-8', errors='ignore').read()
    links = re.findall(r'href="/([\w-]+)/"', c)
    link_counts[d] = len(links)

sorted_counts = sorted(link_counts.items(), key=lambda x: x[1])
print('Pages with FEWEST internal links (bottom 15):')
for name, count in sorted_counts[:15]:
    print(f'  {count} links: /{name}/')
print()
print('Pages with MOST internal links (top 5):')
for name, count in sorted_counts[-5:]:
    print(f'  {count} links: /{name}/')
