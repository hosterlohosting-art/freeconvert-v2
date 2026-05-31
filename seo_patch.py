"""
Technical SEO & Internal Linking Patch for freeconvert.cloud
Applies 8 targeted improvements to build_tools.py
"""
import re

with open('build_tools.py', 'r', encoding='utf-8') as f:
    src = f.read()

# =============================================================================
# FIX 1: Smart Related Tools Generator (replaces bare 4-link generator)
# =============================================================================

OLD_RELATED = '''        # Related tools injection
        related_html = ""
        # Find 4 tools in the same category
        matched_tools = [t for t in tools if t['type'] == t_type and t['id'] != t_id][:4]
        if len(matched_tools) < 4:
            matched_tools += [t for t in tools if t['id'] != t_id and t not in matched_tools][:4 - len(matched_tools)]
            
        for r_tool in matched_tools:
            related_html += f\'<a href="/{r_tool["id"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">{r_tool["icon"]} {r_tool["name"]}</a>\'
            
        html = html.replace(\'{{RELATED_LINKS}}\', related_html)'''

NEW_RELATED = '''        # Smart Related Tools (category-aware, card style, 6 links)
        same_cat = [t for t in tools if t['type'] == t_type and t['id'] != t_id]
        cross_cat = [t for t in tools if t['id'] != t_id and t not in same_cat]
        matched_tools = (same_cat + cross_cat)[:6]
        related_html = ""
        for r_tool in matched_tools:
            related_html += f"""<a href="/{r_tool['id']}/" style="display:flex;flex-direction:column;gap:0.3rem;padding:1rem 1.2rem;background:var(--bg-light);border:1px solid var(--border-color);border-radius:12px;text-decoration:none;color:var(--text-primary);transition:all 0.2s;font-size:0.9rem;" onmouseover="this.style.borderColor='var(--brand-primary)';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='var(--border-color)';this.style.transform=''">
  <span style="font-size:1.4rem;">{r_tool['icon']}</span>
  <strong style="font-size:0.88rem;">{r_tool['name']}</strong>
  <span style="font-size:0.78rem;color:var(--text-muted);line-height:1.3;">{r_tool['description'][:60]}...</span>
</a>"""
        html = html.replace('{{RELATED_LINKS}}', related_html)

        # Blog Links injection (contextual links to guides)
        BLOG_LINK_MAP = {
            'image': [
                ('/blog/jpg-vs-png-which-format-should-you-use/', 'JPG vs PNG — Which Format Should You Use?'),
                ('/blog/how-to-compress-images-online-without-losing-quality/', 'How to Compress Images Without Losing Quality'),
                ('/blog/heic-to-jpg-how-to-convert-iphone-photos-online/', 'HEIC to JPG — Convert iPhone Photos Online'),
                ('/blog/webp-vs-jpg-which-image-format-should-you-use/', 'WebP vs JPG — Which Format Is Better?'),
            ],
            'image_advanced': [
                ('/blog/how-to-compress-an-image-to-100kb/', 'How to Compress an Image to 100KB'),
                ('/blog/how-to-compress-images-online-without-losing-quality/', 'Compress Images Without Losing Quality'),
                ('/blog/webp-vs-jpg-which-image-format-should-you-use/', 'WebP vs JPG Explained'),
            ],
            'pdf': [
                ('/blog/how-to-convert-jpg-to-pdf-online/', 'How to Convert JPG to PDF Online'),
                ('/blog/pdf-vs-docx-what-is-the-difference/', 'PDF vs DOCX — What Is the Difference?'),
                ('/blog/how-to-keep-files-secure-when-using-online-converters/', 'How to Keep Files Secure Online'),
            ],
            'dev_basic': [
                ('/blog/how-to-convert-json-to-csv-for-spreadsheets/', 'How to Convert JSON to CSV for Excel'),
                ('/blog/how-to-use-a-json-formatter-and-validator/', 'How to Use a JSON Formatter & Validator'),
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Online Tools for Students'),
            ],
            'dev_advanced': [
                ('/blog/how-to-use-a-json-formatter-and-validator/', 'How to Use a JSON Formatter & Validator'),
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Tools for Developers'),
                ('/blog/how-to-convert-json-to-csv-for-spreadsheets/', 'JSON to CSV for Spreadsheets'),
            ],
            'text': [
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Online Tools for Bloggers'),
                ('/blog/best-free-online-file-conversion-tools-for-students-and-professionals/', 'Best File Conversion Tools'),
            ],
            'video': [
                ('/blog/mp4-vs-webm-best-video-format-for-the-web/', 'MP4 vs WebM — Best Video Format for the Web'),
                ('/blog/mp3-vs-wav-which-audio-format-is-better/', 'MP3 vs WAV — Which Audio Format Is Better?'),
            ],
            'utility': [
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Online Tools'),
                ('/blog/what-is-a-qr-code-and-how-to-generate-one-safely/', 'What Is a QR Code? How to Generate One Safely'),
            ],
            'qr': [
                ('/blog/what-is-a-qr-code-and-how-to-generate-one-safely/', 'What Is a QR Code & How to Generate One Safely'),
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Online Tools'),
            ],
            'security': [
                ('/blog/how-to-keep-files-secure-when-using-online-converters/', 'How to Keep Your Files Secure Online'),
                ('/blog/best-free-online-tools-for-bloggers-and-students/', 'Best Free Online Tools'),
            ],
        }
        blog_links_list = BLOG_LINK_MAP.get(t_type, [
            ('/blog/best-free-online-file-conversion-tools-for-students-and-professionals/', 'Best File Conversion Tools'),
            ('/blog/how-to-keep-files-secure-when-using-online-converters/', 'File Security Guide'),
        ])
        blog_links_html = "".join(
            f\'\'\'<a href="{url}" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 0.9rem;background:var(--bg-dark,#0f0f1a);border:1px solid var(--border-color);border-radius:8px;font-size:0.82rem;color:var(--brand-primary);text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background=\'var(--brand-primary)\';this.style.color=\'#fff\'" onmouseout="this.style.background=\'var(--bg-dark,#0f0f1a)\';this.style.color=\'var(--brand-primary)\'">📖 {label}</a>\'\'\'
            for url, label in blog_links_list
        )
        html = html.replace('{{BLOG_LINKS}}', blog_links_html)'''

src = src.replace(OLD_RELATED, NEW_RELATED)
print("FIX 1 (Related tools + Blog links):", "OK" if OLD_RELATED not in src else "FAILED")


# =============================================================================
# FIX 2: Add OG + Twitter + Preload to category pages <head>
# =============================================================================

OLD_CAT_HEAD = '''    <link rel="canonical" href="https://freeconvert.cloud/{CAT_SLUG}/" />
    {SCHEMA_TAG}
</head>'''

NEW_CAT_HEAD = '''    <link rel="canonical" href="https://freeconvert.cloud/{CAT_SLUG}/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="{SEO_TITLE} | freeconvert.cloud">
    <meta property="og:description" content="{SEO_DESC}">
    <meta property="og:url" content="https://freeconvert.cloud/{CAT_SLUG}/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{SEO_TITLE} | freeconvert.cloud">
    <meta name="twitter:description" content="{SEO_DESC}">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">

    {SCHEMA_TAG}
</head>'''

src = src.replace(OLD_CAT_HEAD, NEW_CAT_HEAD)
print("FIX 2 (Category OG tags):", "OK" if OLD_CAT_HEAD not in src else "FAILED")


# =============================================================================
# FIX 3: Add ItemList schema to category pages
# =============================================================================

OLD_CAT_SCHEMA = '''        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "name": cat['seo_title'],
                    "description": cat['seo_desc']
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_schema
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Home",
                            "item": "https://freeconvert.cloud/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": cat['name'],
                            "item": f"https://freeconvert.cloud/{cat['slug']}/"
                        }
                    ]
                }
            ]
        }
        schema_tag = f\'<script type="application/ld+json">{json.dumps(schema_data)}</script>\''''

NEW_CAT_SCHEMA = '''        # Build ItemList of tools for category schema
        item_list_elements = []
        for idx, cat_tool in enumerate(cat_tools, 1):
            item_list_elements.append({
                "@type": "ListItem",
                "position": idx,
                "name": cat_tool['name'],
                "url": f"https://freeconvert.cloud/{cat_tool['id']}/"
            })

        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "name": cat['seo_title'],
                    "description": cat['seo_desc'],
                    "url": f"https://freeconvert.cloud/{cat['slug']}/"
                },
                {
                    "@type": "ItemList",
                    "name": f"{cat['name']} Tools",
                    "description": cat['seo_desc'],
                    "numberOfItems": len(cat_tools),
                    "itemListElement": item_list_elements
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_schema
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Home",
                            "item": "https://freeconvert.cloud/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": cat['name'],
                            "item": f"https://freeconvert.cloud/{cat['slug']}/"
                        }
                    ]
                }
            ]
        }
        schema_tag = f\'<script type="application/ld+json">{json.dumps(schema_data)}</script>\''''

src = src.replace(OLD_CAT_SCHEMA, NEW_CAT_SCHEMA)
print("FIX 3 (Category ItemList schema):", "OK" if OLD_CAT_SCHEMA not in src else "FAILED")


# =============================================================================
# FIX 4: Expanded footer (15 tool links + New Tools column)
# =============================================================================

OLD_FOOTER_COLS = '''        <div class="footer-content">
            <div class="footer-brand">
                <a href="/"><img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud" style="height:36px;width:auto;margin-bottom:0.75rem;display:block;"></a>
                <p>The world\'s most beautiful, privacy-first SaaS conversion platform. Process documents, images, video, audio, and archives instantly.</p>
            </div>
            <div class="footer-col">
                <h4>Popular Converters</h4>
                <div class="footer-links">
                    <a href="/jpg-to-pdf/">JPG to PDF</a>
                    <a href="/pdf-to-word/">PDF to Word</a>
                    <a href="/png-to-jpg/">PNG to JPG</a>
                    <a href="/mp4-to-mp3/">MP4 to MP3</a>
                    <a href="/csv-to-json/">CSV to JSON</a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Category Guides</h4>
                <div class="footer-links">
                    <a href="/image-converter/">Image Converter</a>
                    <a href="/video-converter/">Video Converter</a>
                    <a href="/audio-converter/">Audio Converter</a>
                    <a href="/document-converter/">Document Tools</a>
                    <a href="/pdf-tools/">PDF Tools Grid</a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Company &amp; Legal</h4>
                <div class="footer-links">
                    <a href="/about/">About Us</a>
                    <a href="/pricing/">Plan Pricing</a>
                    <a href="/api/">Developer API</a>
                    <a href="/privacy/">Privacy Policy</a>
                    <a href="/terms/">Terms of Service</a>
                    <a href="/security/">File Security</a>
                    <a href="/cookies/">Cookie Policy</a>
                    <a href="/contact/">Contact Us</a>
                    <a href="/dmca/">DMCA Policy</a>
                </div>
            </div>
        </div>'''

NEW_FOOTER_COLS = '''        <div class="footer-content">
            <div class="footer-brand">
                <a href="/"><img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud" style="height:36px;width:auto;margin-bottom:0.75rem;display:block;"></a>
                <p>The world\'s most beautiful, privacy-first SaaS conversion platform. Convert images, PDFs, video, audio, and developer files in your browser.</p>
                <div style="margin-top:0.8rem;font-size:0.78rem;color:var(--text-muted);">
                    <a href="/blog/" style="color:var(--brand-primary);text-decoration:none;">📖 Read Our Guides</a> &nbsp;|&nbsp;
                    <a href="/pricing/" style="color:var(--brand-primary);text-decoration:none;">💎 Upgrade to Pro</a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Popular Tools</h4>
                <div class="footer-links">
                    <a href="/jpg-to-pdf/">JPG to PDF</a>
                    <a href="/pdf-to-word/">PDF to Word</a>
                    <a href="/png-to-jpg/">PNG to JPG</a>
                    <a href="/mp4-to-mp3/">MP4 to MP3</a>
                    <a href="/csv-to-json/">CSV to JSON</a>
                    <a href="/json-to-csv/">JSON to CSV</a>
                    <a href="/compress-pdf/">Compress PDF</a>
                    <a href="/image-compressor/">Image Compressor</a>
                    <a href="/compress-image-to-100kb/">Compress to 100KB</a>
                    <a href="/webp-to-jpg/">WebP to JPG</a>
                    <a href="/jpg-to-webp/">JPG to WebP</a>
                    <a href="/merge-pdf/">Merge PDF</a>
                    <a href="/qr-code-generator/">QR Code Generator</a>
                    <a href="/password-generator/">Password Generator</a>
                    <a href="/json-formatter/">JSON Formatter</a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Tool Categories</h4>
                <div class="footer-links">
                    <a href="/image-converter/">Image Converter</a>
                    <a href="/video-converter/">Video Converter</a>
                    <a href="/audio-converter/">Audio Converter</a>
                    <a href="/document-converter/">Document Tools</a>
                    <a href="/pdf-tools/">PDF Tools</a>
                    <a href="/archive-converter/">Archive Tools</a>
                    <a href="/ebook-converter/">eBook Converter</a>
                    <a href="/unit-converter/">Unit Converter</a>
                </div>
                <h4 style="margin-top:1.2rem;">New Tools</h4>
                <div class="footer-links">
                    <a href="/word-counter/">Word Counter</a>
                    <a href="/base64-encode/">Base64 Encoder</a>
                    <a href="/url-encoder/">URL Encoder</a>
                    <a href="/markdown-editor/">Markdown Editor</a>
                    <a href="/diff-checker/">Diff Checker</a>
                    <a href="/uuid-generator/">UUID Generator</a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Company &amp; Legal</h4>
                <div class="footer-links">
                    <a href="/about/">About Us</a>
                    <a href="/pricing/">Plan Pricing</a>
                    <a href="/api/">Developer API</a>
                    <a href="/blog/">Blog &amp; Guides</a>
                    <a href="/privacy/">Privacy Policy</a>
                    <a href="/terms/">Terms of Service</a>
                    <a href="/security/">File Security</a>
                    <a href="/cookies/">Cookie Policy</a>
                    <a href="/contact/">Contact Us</a>
                    <a href="/dmca/">DMCA Policy</a>
                </div>
            </div>
        </div>'''

src = src.replace(OLD_FOOTER_COLS, NEW_FOOTER_COLS)
print("FIX 4 (Footer expansion):", "OK" if OLD_FOOTER_COLS not in src else "FAILED")


# =============================================================================
# FIX 5: Add preloads to homepage head
# =============================================================================

OLD_HP_FONTS = '''    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <!-- Canonical tag -->'''

NEW_HP_FONTS = '''    <!-- Fonts & Preloads -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">

    <!-- Canonical tag -->'''

src = src.replace(OLD_HP_FONTS, NEW_HP_FONTS)
print("FIX 5 (Homepage preloads):", "OK" if OLD_HP_FONTS not in src else "FAILED")


# =============================================================================
# FIX 6: Blog pages - inject tool links box after author box
# =============================================================================

BLOG_TOOL_LINK_MAP = """
# Blog → Tool contextual link map
BLOG_TOOL_MAP = {
    'how-to-convert-jpg-to-pdf-online': [('jpg-to-pdf','JPG to PDF'),('compress-pdf','Compress PDF'),('pdf-to-word','PDF to Word')],
    'how-to-convert-png-to-jpg-without-losing-quality': [('png-to-jpg','PNG to JPG'),('image-compressor','Image Compressor'),('resize-image','Resize Image')],
    'jpg-vs-png-which-format-should-you-use': [('png-to-jpg','PNG to JPG'),('jpg-to-webp','JPG to WebP'),('image-compressor','Compress Image')],
    'pdf-vs-docx-what-is-the-difference': [('pdf-to-word','PDF to Word'),('compress-pdf','Compress PDF'),('jpg-to-pdf','JPG to PDF')],
    'how-to-compress-images-for-websites': [('image-compressor','Image Compressor'),('compress-image-to-100kb','Compress to 100KB'),('resize-image','Resize Image')],
    'how-to-convert-json-to-csv-for-spreadsheets': [('json-to-csv','JSON to CSV'),('csv-to-json','CSV to JSON'),('json-formatter','JSON Formatter')],
    'mp3-vs-wav-which-audio-format-is-better': [('mp4-to-mp3','MP4 to MP3'),('video-compressor','Video Compressor')],
    'mp4-vs-webm-best-video-format-for-the-web': [('mp4-to-mp3','MP4 to MP3'),('webm-to-mp4','WebM to MP4'),('video-compressor','Video Compressor')],
    'how-to-keep-files-secure-when-using-online-converters': [('security','File Security'),('password-generator','Password Generator'),('image-compressor','Image Compressor')],
    'best-free-online-file-conversion-tools-for-students-and-professionals': [('jpg-to-pdf','JPG to PDF'),('json-to-csv','JSON to CSV'),('image-compressor','Image Compressor'),('word-counter','Word Counter')],
    'how-to-compress-images-online-without-losing-quality': [('image-compressor','Image Compressor'),('compress-image-to-100kb','Compress to 100KB'),('compress-image-to-200kb','Compress to 200KB'),('resize-image','Resize Image')],
    'how-to-compress-an-image-to-100kb': [('compress-image-to-100kb','Compress to 100KB'),('compress-image-to-200kb','Compress to 200KB'),('image-compressor','Image Compressor')],
    'webp-vs-jpg-which-image-format-should-you-use': [('webp-to-jpg','WebP to JPG'),('jpg-to-webp','JPG to WebP'),('png-to-jpg','PNG to JPG')],
    'heic-to-jpg-how-to-convert-iphone-photos-online': [('png-to-jpg','PNG to JPG'),('image-compressor','Image Compressor'),('resize-image','Resize Image')],
    'best-free-online-tools-for-bloggers-and-students': [('word-counter','Word Counter'),('character-counter','Character Counter'),('qr-code-generator','QR Code Generator'),('meta-title-checker','Meta Title Checker')],
    'how-to-use-a-json-formatter-and-validator': [('json-formatter','JSON Formatter'),('json-validator','JSON Validator'),('json-to-csv','JSON to CSV'),('base64-encode','Base64 Encoder')],
    'what-is-a-qr-code-and-how-to-generate-one-safely': [('qr-code-generator','QR Code Generator'),('barcode-generator','Barcode Generator'),('url-encoder','URL Encoder')],
}
"""

# Find where build_blog is defined and insert the map before it
OLD_BLOG_DEF = "def build_blog():"
NEW_BLOG_DEF = BLOG_TOOL_LINK_MAP + "\ndef build_blog():"
src = src.replace(OLD_BLOG_DEF, NEW_BLOG_DEF, 1)
print("FIX 6a (Blog tool map):", "OK" if "BLOG_TOOL_MAP" in src else "FAILED")

# Now inject the tool link box into the blog build loop, after full_content assembly
OLD_BLOG_RELATED = '''        # Generate related blogs links (excluding the current one)
        related_articles = [art for art in BLOG_ARTICLES if art['slug'] != slug][:4]
        related_blogs_html = ""
        for rel in related_articles:
            related_blogs_html += f\'<a href="/blog/{rel["slug"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">📝 {rel["title"]}</a>\''''

NEW_BLOG_RELATED = '''        # Inject "Try These Tools" box from contextual map
        tool_links_for_blog = BLOG_TOOL_MAP.get(slug, [('image-compressor','Image Compressor'),('jpg-to-pdf','JPG to PDF'),('json-formatter','JSON Formatter')])
        tool_links_html = "".join(
            f\'\'\'<a href="/{tid}/" style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.5rem 1rem;background:var(--brand-primary);color:#fff;border-radius:8px;font-size:0.85rem;font-weight:600;text-decoration:none;transition:opacity 0.2s;" onmouseover="this.style.opacity=0.85" onmouseout="this.style.opacity=1">⚡ {tname}</a>\'\'\'
            for tid, tname in tool_links_for_blog
        )
        tool_links_box = f\'\'\'
        <div style="margin:2rem 0;padding:1.25rem 1.5rem;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);border-radius:14px;">
            <p style="font-size:0.85rem;font-weight:700;margin-bottom:0.8rem;color:var(--brand-primary);">⚡ Try These Free Tools</p>
            <div style="display:flex;flex-wrap:wrap;gap:0.6rem;">{tool_links_html}</div>
        </div>\'\'\'
        # Insert after author box
        if \'author-box\' in full_content:
            full_content = full_content.replace(\'</div>\\n\', \'</div>\\n\' + tool_links_box, 1)
        else:
            full_content = tool_links_box + full_content

        # Generate related blogs links (excluding the current one)
        related_articles = [art for art in BLOG_ARTICLES if art['slug'] != slug][:4]
        related_blogs_html = ""
        for rel in related_articles:
            related_blogs_html += f\'<a href="/blog/{rel["slug"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">📝 {rel["title"]}</a>\''''

src = src.replace(OLD_BLOG_RELATED, NEW_BLOG_RELATED)
print("FIX 6b (Blog tool link box):", "OK" if "Try These Free Tools" in src else "FAILED")


# =============================================================================
# Write the patched file
# =============================================================================
with open('build_tools.py', 'w', encoding='utf-8') as f:
    f.write(src)

print("\nAll patches written. Run: py build_tools.py")
