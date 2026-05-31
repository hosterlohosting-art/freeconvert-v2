"""
Patch 2: Add OG/Twitter tags to pricing, api, legal, blog-hub pages
"""
with open('build_tools.py', 'r', encoding='utf-8') as f:
    src = f.read()

# Helper: inject OG block after a canonical tag for a specific page
def inject_og(content, canonical_url, title, desc, slug):
    old = f'    <link rel="canonical" href="{canonical_url}" />\n</head>'
    new = f'''    <link rel="canonical" href="{canonical_url}" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>'''
    if old in content:
        return content.replace(old, new), True
    return content, False

# Pricing
src, ok = inject_og(src,
    'https://freeconvert.cloud/pricing/',
    'Pricing Plans | freeconvert.cloud',
    'View pricing options for freeconvert.cloud. Free, Pro, and API Enterprise plans available.',
    'pricing')
print("Pricing OG:", "OK" if ok else "FAILED")

# API
src, ok = inject_og(src,
    'https://freeconvert.cloud/api/',
    'Developer API | freeconvert.cloud',
    'Integrate freeconvert.cloud into your app with our REST API. Convert files programmatically at scale.',
    'api')
print("API OG:", "OK" if ok else "FAILED")

# Blog hub - find the blog/index.html write and look for its canonical
OLD_BLOG_CANON = '    <link rel="canonical" href="https://freeconvert.cloud/blog/" />\n</head>'
NEW_BLOG_CANON = '''    <link rel="canonical" href="https://freeconvert.cloud/blog/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="Blog & File Conversion Guides | freeconvert.cloud">
    <meta property="og:description" content="Expert guides on image conversion, PDF tools, video formats, and more. Free tutorials from the freeconvert.cloud editorial team.">
    <meta property="og:url" content="https://freeconvert.cloud/blog/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Blog & File Conversion Guides | freeconvert.cloud">
    <meta name="twitter:description" content="Expert guides on image conversion, PDF tools, video formats, and more.">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>'''
if OLD_BLOG_CANON in src:
    src = src.replace(OLD_BLOG_CANON, NEW_BLOG_CANON)
    print("Blog Hub OG: OK")
else:
    print("Blog Hub OG: FAILED - canonical not found, trying alternate")

# Legal pages - they share a common html template in build_legal_pages
# Find the canonical pattern used in that function
OLD_LEGAL_CANON = """    <link rel="canonical" href="https://freeconvert.cloud/{slug}/" />
</head>"""
NEW_LEGAL_CANON = """    <link rel="canonical" href="https://freeconvert.cloud/{slug}/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="{page_title} | freeconvert.cloud">
    <meta property="og:description" content="{page_desc}">
    <meta property="og:url" content="https://freeconvert.cloud/{slug}/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{page_title} | freeconvert.cloud">
    <meta name="twitter:description" content="{page_desc}">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>"""

if OLD_LEGAL_CANON in src:
    src = src.replace(OLD_LEGAL_CANON, NEW_LEGAL_CANON)
    print("Legal pages OG: OK")
else:
    print("Legal pages OG: trying to find pattern...")
    # Find what's actually in the legal template
    import re
    m = re.search(r'<link rel="canonical" href="https://freeconvert\.cloud/\{slug\}/" />(.*?)</head>', src, re.DOTALL)
    if m:
        print("  Found:", repr(m.group(0)[:100]))
    else:
        print("  Legal canonical pattern not found, will patch differently")

with open('build_tools.py', 'w', encoding='utf-8') as f:
    f.write(src)

print("\nPatch 2 complete.")
