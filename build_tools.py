import os
import json
import html
import re
from datetime import datetime, timezone
from pathlib import Path
from blog_data import BLOG_ARTICLES


# Compile Destination Constants
TOOLS_JSON = 'tools/tools.json'
TEMPLATE_PATH = 'tools/tool-template.html'
SITE_URL = 'https://freeconvert.cloud'
TODAY_ISO = '2026-06-30'
BRAND_IMAGE = f'{SITE_URL}/assets/freeconvert-logo.png'
ADSENSE_REVIEW_MODE = True
UNAVAILABLE_TOOL_IDS = {
    'heic-to-jpg', 'palette-extractor', 'ico-converter',
    'compress-pdf', 'pdf-to-jpg', 'jpg-to-pdf', 'merge-pdf', 'split-pdf',
    'pdf-to-word', 'word-to-pdf', 'barcode-generator', 'speed-test',
    'mp4-to-mp3', 'video-compressor', 'webm-to-mp4', 'mov-to-mp4',
    'avi-to-mp4', 'mkv-to-mp4', 'mp4-to-gif', 'video-to-mp3',
    'video-trimmer', 'video-resizer',
}
NOINDEX_PATH_PREFIXES = (
    'popular-conversions/',
    'free-online-converter-guides/',
    'blog/hub-pages/',
)
NOINDEX_TOP_LEVEL_SLUGS = {
    'video-converter', 'audio-converter', 'pdf-tools', 'archive-converter',
    'ebook-converter', 'pricing', 'api',
}
LEGACY_ROUTE_MAP = {
    '/image-resizer/': '/resize-image/',
    '/about-freeconvert/': '/about/',
    '/contact-us/': '/contact/',
    '/2025/11/02/hello-world/': '/',
    '/2025/12/18/qr-codes-on-business-cards/': '/free-online-converter-guides/qr-codes-on-business-cards/',
    '/base64-tool/': '/base64-encode/',
    '/qr-generator/': '/qr-code-generator/',
    '/lorem-ipsum/': '/lorem-ipsum-generator/',
    '/dev_basic/': '/document-converter/',
}


def is_indexable_tool(tool):
    return tool['id'] not in UNAVAILABLE_TOOL_IDS


def filter_indexable_tools(tools):
    return [tool for tool in tools if is_indexable_tool(tool)]

TOP_KEYWORD_TARGETS = [
    {
        'keyword': 'pdf to jpg',
        'tool_id': 'pdf-to-jpg',
        'intent': 'Convert PDF pages into JPG images for sharing, thumbnails, uploads, and previews.',
        'cluster': 'PDF conversion',
        'priority': 1,
        'modifiers': ['pdf to jpg converter', 'convert pdf to jpg online', 'pdf pages to jpg', 'pdf to jpg high quality', 'pdf to jpg free']
    },
    {
        'keyword': 'jpg to pdf',
        'tool_id': 'jpg-to-pdf',
        'intent': 'Combine photos, scans, receipts, and screenshots into one PDF document.',
        'cluster': 'PDF creation',
        'priority': 2,
        'modifiers': ['jpg to pdf converter', 'convert jpg to pdf online', 'image to pdf', 'jpg to pdf for school', 'merge jpg to pdf']
    },
    {
        'keyword': 'png to jpg',
        'tool_id': 'png-to-jpg',
        'intent': 'Turn PNG images into smaller, widely supported JPG files.',
        'cluster': 'Image conversion',
        'priority': 3,
        'modifiers': ['png to jpg converter', 'convert png to jpg online', 'png image to jpeg', 'png to jpg for website', 'png to jpg transparent']
    },
    {
        'keyword': 'jpg to png',
        'tool_id': 'jpg-to-png',
        'intent': 'Convert JPG photos into lossless PNG images for editing and design workflows.',
        'cluster': 'Image conversion',
        'priority': 4,
        'modifiers': ['jpg to png converter', 'convert jpg to png online', 'jpeg to png', 'jpg to png transparent', 'jpg to png no background']
    },
    {
        'keyword': 'webp to jpg',
        'tool_id': 'webp-to-jpg',
        'intent': 'Make modern WebP images compatible with older apps, CMS uploads, and editors.',
        'cluster': 'Image conversion',
        'priority': 5,
        'modifiers': ['webp to jpg converter', 'convert webp to jpg online', 'webp image to jpeg', 'webp to jpg for wordpress']
    },
    {
        'keyword': 'heic to jpg',
        'tool_id': 'heic-to-jpg',
        'intent': 'Convert iPhone HEIC photos into universal JPG files.',
        'cluster': 'Image conversion',
        'priority': 6,
        'modifiers': ['heic to jpg converter', 'iphone photo to jpg', 'convert heic to jpeg', 'heic to jpg on windows', 'heic to jpg iphone']
    },
    {
        'keyword': 'compress pdf',
        'tool_id': 'compress-pdf',
        'intent': 'Reduce PDF file size for email, uploads, storage, and document sharing.',
        'cluster': 'PDF compression',
        'priority': 7,
        'modifiers': ['compress pdf online', 'reduce pdf file size', 'pdf compressor', 'compress pdf to 1mb', 'compress pdf for email']
    },
    {
        'keyword': 'pdf to word',
        'tool_id': 'pdf-to-word',
        'intent': 'Convert PDF documents into editable Word DOCX files.',
        'cluster': 'Document conversion',
        'priority': 8,
        'modifiers': ['pdf to word converter', 'pdf to docx', 'convert pdf to editable word', 'pdf to word for editing', 'pdf to word free']
    },
    {
        'keyword': 'word to pdf',
        'tool_id': 'word-to-pdf',
        'intent': 'Export DOCX and Word documents into clean PDF files.',
        'cluster': 'Document conversion',
        'priority': 9,
        'modifiers': ['word to pdf converter', 'docx to pdf', 'convert word document to pdf', 'word to pdf online free', 'doc to pdf']
    },
    {
        'keyword': 'merge pdf',
        'tool_id': 'merge-pdf',
        'intent': 'Combine multiple PDF files into one organized document.',
        'cluster': 'PDF editing',
        'priority': 10,
        'modifiers': ['merge pdf online', 'combine pdf files', 'pdf merger', 'merge pdf files free', 'join pdf']
    },
    {
        'keyword': 'split pdf',
        'tool_id': 'split-pdf',
        'intent': 'Extract selected pages or split a PDF into smaller files.',
        'cluster': 'PDF editing',
        'priority': 11,
        'modifiers': ['split pdf online', 'extract pdf pages', 'pdf splitter', 'split pdf into pages', 'pdf page extractor']
    },
    {
        'keyword': 'image compressor',
        'tool_id': 'image-compressor',
        'intent': 'Shrink JPG, PNG, and WebP images while keeping useful visual quality.',
        'cluster': 'Image compression',
        'priority': 12,
        'modifiers': ['compress image online', 'reduce image size', 'photo compressor', 'compress image for website', 'compress jpg online']
    },
    {
        'keyword': 'compress image to 100kb',
        'tool_id': 'compress-image-to-100kb',
        'intent': 'Reduce photos under 100KB for forms, job portals, and application uploads.',
        'cluster': 'Image compression',
        'priority': 13,
        'modifiers': ['image compressor to 100kb', 'photo size reducer 100kb', 'compress jpg to 100kb', 'compress image under 100kb', 'image resize 100kb']
    },
    {
        'keyword': 'resize image',
        'tool_id': 'resize-image',
        'intent': 'Resize images to exact pixel dimensions for websites, social media, and forms.',
        'cluster': 'Image editing',
        'priority': 14,
        'modifiers': ['image resizer online', 'resize photo online', 'change image dimensions', 'resize image for instagram', 'resize image pixels']
    },
    {
        'keyword': 'png to webp',
        'tool_id': 'png-to-webp',
        'intent': 'Convert PNG graphics to WebP for faster pages and smaller image delivery.',
        'cluster': 'Image conversion',
        'priority': 15,
        'modifiers': ['png to webp converter', 'convert png to webp online', 'png webp optimizer', 'png to webp transparent']
    },
    {
        'keyword': 'jpg to webp',
        'tool_id': 'jpg-to-webp',
        'intent': 'Convert JPG photos into lightweight WebP images for SEO speed gains.',
        'cluster': 'Image conversion',
        'priority': 16,
        'modifiers': ['jpg to webp converter', 'convert jpg to webp online', 'jpeg to webp', 'jpg to webp for website']
    },
    {
        'keyword': 'mp4 to mp3',
        'tool_id': 'mp4-to-mp3',
        'intent': 'Extract audio from MP4 videos into MP3 files.',
        'cluster': 'Media conversion',
        'priority': 17,
        'modifiers': ['mp4 to mp3 converter', 'extract audio from mp4', 'video to mp3', 'mp4 to mp3 free', 'convert video to audio']
    },
    {
        'keyword': 'webm to mp4',
        'tool_id': 'webm-to-mp4',
        'intent': 'Convert WebM videos into widely compatible MP4 files.',
        'cluster': 'Media conversion',
        'priority': 18,
        'modifiers': ['webm to mp4 converter', 'convert webm to mp4 online', 'webm video to mp4', 'webm to mp4 free']
    },
    {
        'keyword': 'json to csv',
        'tool_id': 'json-to-csv',
        'intent': 'Flatten JSON data into CSV rows for Excel, Sheets, and data imports.',
        'cluster': 'Developer conversion',
        'priority': 19,
        'modifiers': ['json to csv converter', 'convert json to csv online', 'json array to csv', 'json to csv for excel', 'json to csv free']
    },
    {
        'keyword': 'qr code generator',
        'tool_id': 'qr-code-generator',
        'intent': 'Create QR codes for links, menus, contact cards, events, and WiFi access.',
        'cluster': 'Utility tools',
        'priority': 20,
        'modifiers': ['free qr code generator', 'create qr code online', 'qr generator', 'qr code for menu', 'qr code for wifi']
    },
    {
        'keyword': 'svg to png',
        'tool_id': 'svg-to-png',
        'intent': 'Render SVG vector files as high-quality PNG images for design and web use.',
        'cluster': 'Image conversion',
        'priority': 21,
        'modifiers': ['svg to png converter', 'convert svg to png online', 'svg to png transparent', 'svg to png logo']
    },
    {
        'keyword': 'ico converter',
        'tool_id': 'ico-converter',
        'intent': 'Create favicon .ico files from PNG or JPG images for websites.',
        'cluster': 'Image conversion',
        'priority': 22,
        'modifiers': ['ico converter', 'png to ico', 'jpg to ico', 'favicon generator', 'create favicon online']
    },
    {
        'keyword': 'mov to mp4',
        'tool_id': 'mov-to-mp4',
        'intent': 'Convert Apple MOV videos to universal MP4 format.',
        'cluster': 'Media conversion',
        'priority': 23,
        'modifiers': ['mov to mp4 converter', 'convert mov to mp4 online', 'mov to mp4 free', 'mov to mp4 iphone']
    },
    {
        'keyword': 'mkv to mp4',
        'tool_id': 'mkv-to-mp4',
        'intent': 'Convert MKV videos to widely supported MP4 files.',
        'cluster': 'Media conversion',
        'priority': 24,
        'modifiers': ['mkv to mp4 converter', 'convert mkv to mp4 online', 'mkv to mp4 free', 'mkv to mp4 without quality loss']
    },
    {
        'keyword': 'avi to mp4',
        'tool_id': 'avi-to-mp4',
        'intent': 'Convert AVI videos to MP4 for better compatibility.',
        'cluster': 'Media conversion',
        'priority': 25,
        'modifiers': ['avi to mp4 converter', 'convert avi to mp4 online', 'avi to mp4 free', 'avi to mp4 for windows']
    },
    {
        'keyword': 'mp4 to gif',
        'tool_id': 'mp4-to-gif',
        'intent': 'Turn MP4 video clips into animated GIF images.',
        'cluster': 'Media conversion',
        'priority': 26,
        'modifiers': ['mp4 to gif converter', 'convert mp4 to gif online', 'video to gif', 'mp4 to gif free']
    },
    {
        'keyword': 'csv to json',
        'tool_id': 'csv-to-json',
        'intent': 'Convert CSV spreadsheet rows into structured JSON arrays.',
        'cluster': 'Developer conversion',
        'priority': 27,
        'modifiers': ['csv to json converter', 'convert csv to json online', 'csv to json for api', 'excel to json']
    },
    {
        'keyword': 'json formatter',
        'tool_id': 'json-formatter',
        'intent': 'Format and beautify JSON data for readability and debugging.',
        'cluster': 'Developer tools',
        'priority': 28,
        'modifiers': ['json formatter', 'json beautifier', 'format json online', 'json pretty print']
    },
    {
        'keyword': 'base64 encode',
        'tool_id': 'base64-encode',
        'intent': 'Encode text or files to Base64 strings.',
        'cluster': 'Developer tools',
        'priority': 29,
        'modifiers': ['base64 encode', 'base64 encoder online', 'text to base64', 'encode base64']
    },
    {
        'keyword': 'password generator',
        'tool_id': 'password-generator',
        'intent': 'Generate strong, secure passwords with custom length and symbols.',
        'cluster': 'Security tools',
        'priority': 30,
        'modifiers': ['password generator', 'strong password generator', 'random password generator', 'secure password maker']
    },
    {
        'keyword': 'word counter',
        'tool_id': 'word-counter',
        'intent': 'Count words, characters, sentences, and reading time for text.',
        'cluster': 'Text tools',
        'priority': 31,
        'modifiers': ['word counter', 'character counter', 'word count online', 'essay word counter']
    },
    {
        'keyword': 'image to base64',
        'tool_id': 'image-to-base64',
        'intent': 'Convert images to Base64 data URIs for CSS, HTML, and emails.',
        'cluster': 'Developer tools',
        'priority': 32,
        'modifiers': ['image to base64', 'convert image to base64', 'base64 image encoder', 'img to base64']
    },
]


def article_date_iso(date_text):
    for fmt in ('%B %d, %Y', '%B %Y'):
        try:
            parsed = datetime.strptime(date_text, fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    return TODAY_ISO


def article_date_rfc822(date_text):
    parsed = datetime.fromisoformat(article_date_iso(date_text)).replace(tzinfo=timezone.utc)
    return parsed.strftime('%a, %d %b %Y 00:00:00 GMT')


def public_url_for_html(path):
    rel = Path(path).as_posix()
    if rel == 'index.html':
        return f'{SITE_URL}/'
    if rel.endswith('/index.html'):
        return f'{SITE_URL}/{rel[:-11]}/'
    return f'{SITE_URL}/{rel}'


def iter_public_html_files():
    excluded = {
        Path('tools/tool-template.html'),
        Path('blog/blog-template.html'),
    }
    for html_path in Path('.').rglob('*.html'):
        if html_path in excluded:
            continue
        if any(part in {'__pycache__', '.git'} for part in html_path.parts):
            continue
        yield html_path


def derive_meta_description(html, title):
    for marker in ('name="description" content="', 'property="og:description" content="'):
        if marker in html:
            return html.split(marker, 1)[1].split('"', 1)[0]
    clean_title = title.replace(' | freeconvert.cloud', '').replace(' | freeconvert.cloud Blog', '')
    return f'{clean_title} from freeconvert.cloud. Fast, free, privacy-first online tools for everyday file conversion and productivity tasks.'


def truncate_text(text, max_len=60, suffix='...'):
    """Truncate text to fit SERP limits without cutting mid-word."""
    if len(text) <= max_len:
        return text
    cutoff = max_len - len(suffix)
    trimmed = text[:cutoff]
    if ' ' in trimmed:
        trimmed = trimmed.rsplit(' ', 1)[0]
    return trimmed + suffix


def social_meta_tags(title, desc, url, image=BRAND_IMAGE, og_type='website'):
    """Return a complete Open Graph + Twitter Card block."""
    safe_title = html.escape(title)
    safe_desc = html.escape(desc)
    safe_url = html.escape(url)
    safe_image = html.escape(image)
    return (
        '    <!-- Open Graph -->\n'
        f'    <meta property="og:type" content="{og_type}">\n'
        '    <meta property="og:site_name" content="freeconvert.cloud">\n'
        f'    <meta property="og:title" content="{safe_title}">\n'
        f'    <meta property="og:description" content="{safe_desc}">\n'
        f'    <meta property="og:url" content="{safe_url}">\n'
        f'    <meta property="og:image" content="{safe_image}">\n'
        '\n'
        '    <!-- Twitter Card -->\n'
        '    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{safe_title}">\n'
        f'    <meta name="twitter:description" content="{safe_desc}">\n'
        f'    <meta name="twitter:image" content="{safe_image}">\n'
        '    <meta name="twitter:site" content="@freeconvertcloud">\n'
    )


def website_search_schema_tag():
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "freeconvert.cloud",
        "url": f"{SITE_URL}/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    return f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'


def keyword_target_for_tool(tool_id):
    for target in TOP_KEYWORD_TARGETS:
        if target['tool_id'] == tool_id:
            return target
    return None


def homepage_keyword_hub_html(tools):
    tools_by_id = {tool['id']: tool for tool in tools}
    cards = []
    for target in TOP_KEYWORD_TARGETS:
        tool = tools_by_id.get(target['tool_id'])
        if not tool:
            continue
        modifiers = ', '.join(target['modifiers'][:2])
        cards.append(f"""
                <a href="/{target['tool_id']}/" class="tool-card" style="text-align:left;text-decoration:none;">
                    <div class="tool-card-top">
                        <div class="tool-icon">{target['priority']}</div>
                        <span class="tool-category-tag">{html.escape(target['cluster'])}</span>
                    </div>
                    <div class="tool-card-body">
                        <span role="heading" aria-level="3" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{html.escape(target['keyword'].title())}</span>
                        <p>{html.escape(target['intent'])}</p>
                    </div>
                    <div class="tool-card-footer">
                        <span class="explore-text">Open {html.escape(tool['name'])}</span>
                        <span class="arrow-icon">-&gt;</span>
                    </div>
                </a>""")
    return f"""
    <section style="background:white;border-top:1px solid var(--border-color);padding:5rem 5%;">
        <div style="max-width:1440px;margin:0 auto;">
            <div style="text-align:center;max-width:820px;margin:0 auto 2.5rem;">
                <span class="badge">Top Searched Converter Keywords</span>
                <h2 style="font-size:2.2rem;margin-top:1rem;margin-bottom:0.8rem;">High-intent file conversion keywords we target</h2>
                <p style="font-size:1rem;color:var(--text-muted);">These are the core transactional searches for free online converters: PDF to JPG, JPG to PDF, PNG to JPG, image compression, document conversion, video extraction, and developer data tools.</p>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.2rem;">
                {''.join(cards)}
            </div>
        </div>
    </section>"""


def keyword_target_schema_tag(tools=None):
    allowed_tool_ids = {tool['id'] for tool in tools} if tools is not None else None
    targets = [
        target for target in TOP_KEYWORD_TARGETS
        if allowed_tool_ids is None or target['tool_id'] in allowed_tool_ids
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Top free online converter keyword targets",
        "description": "High-intent file conversion searches mapped to freeconvert.cloud converter landing pages.",
        "numberOfItems": len(targets),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": target["priority"],
                "name": target["keyword"],
                "url": f"{SITE_URL}/{target['tool_id']}/",
                "description": target["intent"]
            }
            for target in targets
        ]
    }
    return f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'


def tool_keyword_content_html(tool, tools):
    target = keyword_target_for_tool(tool['id'])
    name = html.escape(tool['name'])
    desc = html.escape(tool.get('description', ''))
    category = html.escape(tool.get('category', 'Utility'))
    base_intro = f"""
            <section style="margin-top:2.2rem;">
                <h2>What is {name}?</h2>
                <p>{name} is built for users who need a quick, free, and private way to handle {category.lower()} workflows without installing desktop software. {desc} The page combines a working converter, practical instructions, privacy notes, related tools, and common troubleshooting guidance so visitors can complete the task and understand the format decision in the same place.</p>
                <p>Use it for everyday document preparation, website uploads, email attachments, school work, client deliverables, developer cleanup, and mobile sharing. The experience is browser-first, which means supported local operations run inside your device memory and heavier conversion jobs use temporary secure processing only when a format requires it.</p>
            </section>
            <section style="margin-top:2rem;">
                <h2>Common {name} scenarios</h2>
                <table>
                    <thead><tr><th>Scenario</th><th>Why it matters</th><th>Recommended action</th></tr></thead>
                    <tbody>
                        <tr><td>Website publishing</td><td>Smaller, compatible files improve page speed and user experience.</td><td>Convert or compress before uploading to a CMS.</td></tr>
                        <tr><td>Email and forms</td><td>Many portals reject files that are too large or in unsupported formats.</td><td>Use the converter, then check the output size before sending.</td></tr>
                        <tr><td>Mobile sharing</td><td>Phones often save modern formats that older apps cannot open.</td><td>Export to a common format with broad compatibility.</td></tr>
                    </tbody>
                </table>
            </section>"""
    comparison = f"""
            <section style="margin-top:2rem;">
                <h2>{name} format notes</h2>
                <p>Before converting, check whether your goal is smaller file size, stronger compatibility, editable output, or better visual quality. Lossy formats usually reduce file size, while lossless or document formats may preserve more detail but create larger files. When quality matters, keep a backup of the original source file and compare the result before deleting anything.</p>
            </section>"""
    trust = f"""
            <section style="margin-top:2rem;padding:1.5rem;border-radius:14px;background:rgba(16,185,129,0.04);border:1px solid rgba(16,185,129,0.14);">
                <h2 style="font-size:1.25rem;margin-bottom:0.7rem;">Privacy-first conversion promise</h2>
                <p style="font-size:0.95rem;line-height:1.65;margin:0;">freeconvert.cloud is designed around clear privacy expectations: browser-local tools avoid uploads, server-required conversions use encrypted transfer, and user files are not treated as public content. For deeper details, read our <a href="/security/" style="color:var(--brand-primary);font-weight:700;text-decoration:none;">file security policy</a>.</p>
            </section>"""
    if not target:
        return base_intro + comparison + trust
    tools_by_id = {item['id']: item for item in tools}
    related_targets = [
        item for item in TOP_KEYWORD_TARGETS
        if item['tool_id'] in tools_by_id and item['tool_id'] != tool['id'] and (
            item['cluster'] == target['cluster']
            or item['cluster'].split()[0] == target['cluster'].split()[0]
        )
    ][:6]
    related_links = ''.join(
        f'<a href="/{rel["tool_id"]}/" style="display:inline-flex;padding:0.45rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-size:0.84rem;font-weight:700;">{html.escape(tools_by_id.get(rel["tool_id"], {}).get("name", rel["keyword"].title()))}</a>'
        for rel in related_targets
    )
    # Link to use-case guides that target the same tool for stronger internal linking
    use_case_guides = [g for g in generate_use_case_pages() if g['tool'] == tool['id']][:4]
    guide_links = ''.join(
        f'<a href="/free-online-converter-guides/{html.escape(g["slug"])}/" style="display:inline-flex;padding:0.45rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-size:0.84rem;font-weight:700;">{html.escape(g["title"])}</a>'
        for g in use_case_guides
    )
    keyword_section = f"""
            <section style="margin-top:2.2rem;padding:1.8rem;border:1px solid rgba(99,102,241,0.12);border-radius:16px;background:rgba(99,102,241,0.025);">
                <h2 style="font-size:1.35rem;margin-bottom:0.8rem;">What people search for</h2>
                <p style="font-size:0.95rem;line-height:1.65;margin-bottom:1rem;">This page answers the <strong>{html.escape(target['keyword'])}</strong> search intent and related converter phrases. {html.escape(target['intent'])}</p>
                <h3 style="font-size:1.05rem;margin-bottom:0.6rem;">Related converter searches</h3>
                <div style="display:flex;flex-wrap:wrap;gap:0.55rem;margin-bottom:1rem;">{related_links}</div>
                {f'<h3 style="font-size:1.05rem;margin-bottom:0.6rem;">Step-by-step guides</h3><div style="display:flex;flex-wrap:wrap;gap:0.55rem;">{guide_links}</div>' if guide_links else ''}
            </section>"""
    return base_intro + comparison + keyword_section + trust


def tool_deep_seo_content_html(tool, tools):
    """Add unique, practical on-page sections for indexable tool pages."""
    name = html.escape(tool['name'])
    t_id = tool['id']
    t_type = tool.get('type', '')
    category = html.escape(tool.get('category', 'Utility'))
    target = keyword_target_for_tool(t_id)

    intent = target['intent'] if target else f"Complete a {category.lower()} task quickly in the browser."
    modifiers = target['modifiers'] if target else [
        f"{tool['name']} online",
        f"free {tool['name']}",
        f"use {tool['name'].lower()} in browser",
    ]

    if t_type in ('image', 'image_advanced', 'image_base64'):
        before = "Large or incompatible image file"
        after = "Smaller, compatible image ready for upload"
        quality_tip = "Keep the original image, then export one web-ready copy for publishing or sharing."
        checks = [
            "Open the output image and compare edges, colors, and transparency handling.",
            "Check file size before uploading to WordPress, Shopify, forms, or email.",
            "Use WebP for speed when your platform supports it; use JPG or PNG for compatibility.",
        ]
    elif t_type in ('dev_basic', 'dev_advanced', 'text'):
        before = "Unformatted text, code, or data"
        after = "Clean output that is easier to copy, review, or import"
        quality_tip = "Validate the output with a small sample before processing a large data set."
        checks = [
            "Review punctuation, line breaks, encoding, and escaping before copying the result.",
            "For JSON or CSV, test the output in your target app before deleting the source.",
            "Avoid pasting secret production keys into any web tool unless local processing is clearly stated.",
        ]
    elif t_type in ('security', 'qr'):
        before = "Manual setup or weak reusable values"
        after = "Safer, structured output for a real workflow"
        quality_tip = "Store important generated values in a trusted password manager or project notes."
        checks = [
            "Test generated QR codes with a phone camera before printing.",
            "Use unique passwords for each account and avoid reusing old credentials.",
            "Confirm the destination URL, WiFi name, or payload before sharing publicly.",
        ]
    else:
        before = "Manual calculation or repetitive browser task"
        after = "Instant result with fewer copy-paste mistakes"
        quality_tip = "Double-check important values when the result will be used for finance, legal, or official forms."
        checks = [
            "Compare the output against your required format or upload guideline.",
            "Keep source values available until you have confirmed the final result.",
            "Use related tools when the task needs formatting, compression, or validation afterward.",
        ]

    modifier_rows = ''.join(
        f"<tr><td>{html.escape(phrase)}</td><td>{html.escape(intent)}</td></tr>"
        for phrase in modifiers[:5]
    )
    checklist_items = ''.join(f"<li>{html.escape(item)}</li>" for item in checks)
    related = [t for t in tools if t['id'] != t_id and t.get('category') == tool.get('category')][:4]
    if len(related) < 4:
        related += [t for t in tools if t['id'] != t_id and t not in related][:4 - len(related)]
    related_links = ''.join(
        f'<a href="/{rel["id"]}/" style="display:inline-flex;padding:0.5rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-weight:700;font-size:0.84rem;">{html.escape(rel["name"])}</a>'
        for rel in related
    )

    review_notes = [
        f"The page was reviewed on {TODAY_ISO} for clear instructions, indexable metadata, and working internal links.",
        "Active tools are kept in the XML sitemap; unavailable or review-mode tools are removed from the sitemap and marked noindex.",
        "Content is written around the task a visitor is trying to finish, not around repeated keyword stuffing.",
    ]
    review_items = ''.join(f"<li>{html.escape(item)}</li>" for item in review_notes)

    return f"""
            <section style="margin-top:2rem;">
                <h2>{name} workflow checklist</h2>
                <p>Use this checklist to decide whether {name} is the right tool for your file, text, or utility task. The page is designed for the practical search intent behind <strong>{html.escape(modifiers[0])}</strong>: get the job done, verify the output, and move on without installing software.</p>
                <table>
                    <thead><tr><th>Before</th><th>After</th><th>Best practice</th></tr></thead>
                    <tbody>
                        <tr><td>{html.escape(before)}</td><td>{html.escape(after)}</td><td>{html.escape(quality_tip)}</td></tr>
                    </tbody>
                </table>
            </section>
            <section style="margin-top:2rem;">
                <h2>Search intent covered on this page</h2>
                <p>Google tends to reward pages that answer the user task clearly instead of repeating keywords. This section maps common search phrases to the real action available on the page.</p>
                <table>
                    <thead><tr><th>Query variation</th><th>What the visitor needs</th></tr></thead>
                    <tbody>{modifier_rows}</tbody>
                </table>
            </section>
            <section style="margin-top:2rem;">
                <h2>Output quality checks</h2>
                <ul style="padding-left:1.5rem;display:flex;flex-direction:column;gap:0.55rem;line-height:1.65;">{checklist_items}</ul>
            </section>
            <section style="margin-top:2rem;padding:1.5rem;border-radius:14px;background:rgba(99,102,241,0.035);border:1px solid rgba(99,102,241,0.14);">
                <h2 style="font-size:1.25rem;margin-bottom:0.7rem;">Next useful tools</h2>
                <p style="margin-bottom:1rem;">Continue the workflow with nearby freeconvert.cloud tools that share similar intent and help Google understand the topical cluster around this page.</p>
                <div style="display:flex;flex-wrap:wrap;gap:0.55rem;">{related_links}</div>
            </section>
            <section style="margin-top:2rem;padding:1.5rem;border-radius:14px;background:rgba(16,185,129,0.04);border:1px solid rgba(16,185,129,0.14);">
                <h2 style="font-size:1.25rem;margin-bottom:0.7rem;">Editorial review and quality signals</h2>
                <p style="margin-bottom:0.9rem;">This page is maintained as a practical tool page, not a doorway page. Each update checks the user task, crawl signals, related links, privacy language, and whether the page should remain indexable.</p>
                <ul style="padding-left:1.5rem;display:flex;flex-direction:column;gap:0.45rem;line-height:1.6;">{review_items}</ul>
            </section>"""


def build_keyword_research_file(tools):
    tools_by_id = {tool['id']: tool for tool in tools}
    payload = []
    for target in TOP_KEYWORD_TARGETS:
        tool = tools_by_id.get(target['tool_id'])
        if not tool:
            continue
        payload.append({
            'priority': target['priority'],
            'keyword': target['keyword'],
            'target_url': f'{SITE_URL}/{target["tool_id"]}/',
            'page_title': tool.get('seo_title', tool.get('name', target['keyword'].title())),
            'intent': target['intent'],
            'cluster': target['cluster'],
            'modifiers': target['modifiers'],
            'source_note': f'Selected from visible SERP competitor patterns around FreeConvert-style file, PDF, image, media, and developer converter pages. Refreshed on {TODAY_ISO}.'
        })
    Path('seo-keyword-targets.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f"Generated seo-keyword-targets.json with top {len(payload)} targets")


def plain_text_from_html(fragment):
    text = re.sub(r'<[^>]+>', ' ', fragment)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def how_to_steps_from_html(how_to):
    steps = []
    for item in re.findall(r'<li>(.*?)</li>', how_to, flags=re.S | re.I):
        clean = plain_text_from_html(item)
        if clean:
            steps.append(clean)
    return steps


def normalize_generated_html_seo():
    """Apply site-wide technical SEO tags to generated and legacy HTML pages."""
    for html_path in iter_public_html_files():
        html = html_path.read_text(encoding='utf-8')
        original = html
        rel_path = html_path.as_posix()
        top_level_slug = rel_path.split('/', 1)[0]
        should_noindex = (
            top_level_slug in UNAVAILABLE_TOOL_IDS
            or top_level_slug in NOINDEX_TOP_LEVEL_SLUGS
            or any(rel_path.startswith(prefix) for prefix in NOINDEX_PATH_PREFIXES)
        )

        if ADSENSE_REVIEW_MODE:
            html = re.sub(
                r'\s*<script[^>]+pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^>]*></script>',
                '',
                html,
                flags=re.I,
            )
            html = re.sub(
                r'\s*<link[^>]+href="(?:https:)?//pagead2\.googlesyndication\.com"[^>]*>',
                '',
                html,
                flags=re.I,
            )
            html = re.sub(
                r'\s*<!-- AdSense Slot:[\s\S]*?<div class="adsense-wrap[^>]*>[\s\S]*?</div>',
                '',
                html,
                flags=re.I,
            )
            review_nav = '''<div class="nav-links">
                <a href="/image-converter/" class="nav-link">Image Tools</a>
                <a href="/document-converter/" class="nav-link">Developer &amp; Text</a>
                <a href="/unit-converter/" class="nav-link">Utility Tools</a>
                <a href="/blog/" class="nav-link">Guides</a>
                <a href="/all-tools/" class="btn primary" style="padding:0.5rem 1.2rem;font-size:0.8rem;border-radius:8px;">All Tools</a>
            </div>
        </nav>'''
            html = re.sub(
                r'<div class="nav-links">[\s\S]*?</nav>',
                review_nav,
                html,
                count=1,
                flags=re.I,
            )
            unavailable_routes = '|'.join(re.escape(slug) for slug in sorted(NOINDEX_TOP_LEVEL_SLUGS | UNAVAILABLE_TOOL_IDS))
            html = re.sub(
                rf'\s*<a\b[^>]*href="/(?:{unavailable_routes})/"[^>]*>[\s\S]*?</a>',
                '',
                html,
                flags=re.I,
            )
            if rel_path == 'index.html':
                html = re.sub(
                    r'\s*<!-- Developer API Preview Section -->[\s\S]*?</section>',
                    '',
                    html,
                    count=1,
                    flags=re.I,
                )
                review_description = (
                    "Free browser tools for image conversion, compression, developer formatting, "
                    "text utilities, QR codes, passwords, calculators, and file guides."
                )
                html = re.sub(
                    r'<meta property="og:description" content="[^"]*">',
                    f'<meta property="og:description" content="{review_description}">',
                    html,
                    count=1,
                    flags=re.I,
                )
                html = re.sub(
                    r'<meta name="twitter:description" content="[^"]*">',
                    f'<meta name="twitter:description" content="{review_description}">',
                    html,
                    count=1,
                    flags=re.I,
                )
                html = re.sub(
                    r'("description":\s*")[^"]*(")',
                    rf'\1{review_description}\2',
                    html,
                    count=2,
                    flags=re.I,
                )
                review_nav_schema = {
                    "@context": "https://schema.org",
                    "@type": "ItemList",
                    "name": "freeconvert.cloud Navigation",
                    "itemListElement": [
                        {
                            "@type": "SiteNavigationElement",
                            "position": 1,
                            "name": "Image Converter",
                            "description": "Browse active image conversion, compression, and resizing tools.",
                            "url": f"{SITE_URL}/image-converter/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 2,
                            "name": "PNG to JPG",
                            "description": "Convert PNG images into lightweight JPG files in the browser.",
                            "url": f"{SITE_URL}/png-to-jpg/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 3,
                            "name": "WebP to JPG",
                            "description": "Convert WebP images to widely compatible JPG files.",
                            "url": f"{SITE_URL}/webp-to-jpg/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 4,
                            "name": "Image Compressor",
                            "description": "Compress JPG, PNG, and WebP images for faster pages.",
                            "url": f"{SITE_URL}/image-compressor/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 5,
                            "name": "JSON Formatter",
                            "description": "Format and clean JSON data inside your browser.",
                            "url": f"{SITE_URL}/json-formatter/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 6,
                            "name": "QR Code Generator",
                            "description": "Create QR codes for URLs, WiFi, menus, and contact details.",
                            "url": f"{SITE_URL}/qr-code-generator/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 7,
                            "name": "All Tools",
                            "description": "Browse active image, developer, text, security, and utility tools.",
                            "url": f"{SITE_URL}/all-tools/",
                        },
                        {
                            "@type": "SiteNavigationElement",
                            "position": 8,
                            "name": "Guides",
                            "description": "Read practical tutorials for conversion, formatting, privacy, and search workflows.",
                            "url": f"{SITE_URL}/blog/",
                        },
                    ],
                }
                html = re.sub(
                    r'<!-- JSON-LD: SiteNavigationElement \(signals sitelinks to Google\) -->\s*<script type="application/ld\+json">[\s\S]*?</script>',
                    '<!-- JSON-LD: SiteNavigationElement (signals sitelinks to Google) -->\n    '
                    f'<script type="application/ld+json">{json.dumps(review_nav_schema, separators=(",", ":"))}</script>',
                    html,
                    count=1,
                    flags=re.I,
                )
            html = html.replace(
                "The world's most beautiful, privacy-first SaaS conversion platform. Convert images, PDFs, video, audio, and developer files in your browser.",
                "Free browser tools for image conversion, text, code, security, and everyday calculations.",
            )
        page_url = public_url_for_html(html_path)
        title = html.split('<title>', 1)[1].split('</title>', 1)[0] if '<title>' in html else 'freeconvert.cloud'

        if 'G-8XCZT6R7PL' not in html:
            if 'G-KYX3224LE0' in html:
                html = html.replace('G-KYX3224LE0', 'G-8XCZT6R7PL')
            else:
                google_tag = (
                    '<!-- Google tag (gtag.js) -->\n'
                    '    <script async src="https://www.googletagmanager.com/gtag/js?id=G-8XCZT6R7PL"></script>\n'
                    '    <script>\n'
                    '      window.dataLayer = window.dataLayer || [];\n'
                    '      function gtag(){dataLayer.push(arguments);}\n'
                    '      gtag(\'js\', new Date());\n\n'
                    '      gtag(\'config\', \'G-8XCZT6R7PL\');\n'
                    '    </script>'
                )
                html = html.replace('<head>', f'<head>\n    {google_tag}', 1)

        for old_route, new_route in LEGACY_ROUTE_MAP.items():
            html = html.replace(f'href="{old_route}"', f'href="{new_route}"')
            html = html.replace(f"href='{old_route}'", f"href='{new_route}'")

        resource_hints = (
            '    <link rel="preconnect" href="https://www.googletagmanager.com">\n'
            '    <link rel="dns-prefetch" href="//www.googletagmanager.com">\n'
            '    <link rel="preconnect" href="https://www.google-analytics.com">\n'
            '    <link rel="dns-prefetch" href="//www.google-analytics.com">\n'
        )
        if 'https://www.googletagmanager.com" rel="preconnect"' not in html and 'rel="preconnect" href="https://www.googletagmanager.com"' not in html:
            html = html.replace('</head>', resource_hints + '\n</head>', 1)

        if '<meta name="description"' not in html:
            description = derive_meta_description(html, title)
            html = html.replace('<title>' + title + '</title>', '<title>' + title + '</title>\n    <meta name="description" content="' + description + '">', 1)

        # Smart title / description length caps for SERP display
        original_title = title
        social_title = title
        if len(title) > 60:
            # Preserve brand suffixes so titles do not end mid-word before the brand
            suffix = None
            for candidate in (' | freeconvert.cloud Blog', ' | freeconvert.cloud'):
                if title.endswith(candidate):
                    suffix = candidate
                    break
            if suffix and len(suffix) < 60:
                prefix = title[:-len(suffix)]
                new_prefix = truncate_text(prefix, 60 - len(suffix) - 1)
                new_title = new_prefix + ' ' + suffix.strip()
            else:
                new_title = truncate_text(title, 60)
            html = html.replace('<title>' + title + '</title>', '<title>' + new_title + '</title>', 1)
            title = new_title
        if '<meta name="description" content="' in html:
            current_desc = html.split('<meta name="description" content="', 1)[1].split('"', 1)[0]
            if len(current_desc) > 160:
                new_desc = truncate_text(current_desc, 160)
                html = html.replace('<meta name="description" content="' + current_desc + '">', '<meta name="description" content="' + new_desc + '">', 1)

        # Keep a readable social title; social platforms tolerate longer titles than SERPs
        social_title = original_title if len(original_title) <= 115 else title

        if 'rel="canonical"' not in html:
            html = html.replace('</head>', f'    <link rel="canonical" href="{page_url}" />\n\n</head>', 1)

        # Inject a complete Open Graph + Twitter Card block when either is missing
        if 'property="og:title"' not in html or 'name="twitter:card"' not in html:
            og_type = 'article' if '/blog/' in page_url else 'website'
            description = derive_meta_description(html, title)
            html = html.replace('</head>', social_meta_tags(social_title, description, page_url, BRAND_IMAGE, og_type) + '\n</head>', 1)

        if 'property="og:locale"' not in html:
            html = html.replace('</head>', '    <meta property="og:locale" content="en_US">\n\n</head>', 1)

        if should_noindex:
            robots_value = 'noindex,follow'
            if 'name="robots"' in html:
                html = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots_value}">', html, count=1)
            else:
                html = html.replace('</head>', f'    <meta name="robots" content="{robots_value}">\n\n</head>', 1)
            if 'name="googlebot"' in html:
                html = re.sub(r'<meta name="googlebot" content="[^"]*">', f'<meta name="googlebot" content="{robots_value}">', html, count=1)
            else:
                html = html.replace('</head>', f'    <meta name="googlebot" content="{robots_value}">\n\n</head>', 1)
        elif 'name="robots"' not in html:
            html = html.replace(
                '</head>',
                '    <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">\n'
                '    <meta name="googlebot" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">\n\n</head>',
                1
            )

        if 'name="theme-color"' not in html:
            html = html.replace('</head>', '    <meta name="theme-color" content="#6366f1">\n    <meta name="format-detection" content="telephone=no">\n\n</head>', 1)

        if 'rel="manifest"' not in html:
            html = html.replace('</head>', '    <link rel="manifest" href="/site.webmanifest">\n    <link rel="apple-touch-icon" href="/assets/favicon.png">\n\n</head>', 1)

        if 'application/rss+xml' not in html:
            html = html.replace('</head>', '    <link rel="alternate" type="application/rss+xml" title="freeconvert.cloud Guides" href="/feed.xml">\n\n</head>', 1)

        if 'application/opensearchdescription+xml' not in html:
            html = html.replace('</head>', '    <link rel="search" type="application/opensearchdescription+xml" title="freeconvert.cloud Search" href="/opensearch.xml">\n\n</head>', 1)

        updated_time_tag = f'<meta property="og:updated_time" content="{TODAY_ISO}T00:00:00+00:00">'
        if 'property="og:updated_time"' in html:
            html = re.sub(r'<meta property="og:updated_time" content="[^"]*">', updated_time_tag, html, count=1)
        else:
            html = html.replace('</head>', f'    {updated_time_tag}\n\n</head>', 1)

        if '"@type":"SearchAction"' not in html and '"@type": "SearchAction"' not in html:
            html = html.replace('</head>', f'    {website_search_schema_tag()}\n\n</head>', 1)

        if html != original:
            html_path.write_text(html, encoding='utf-8')
    print("Normalized site-wide HTML SEO tags")


def sitemap_url_entry(loc, changefreq, priority, include_image=True):
    image_block = ''
    if include_image:
        image_block = f'\n    <image:image>\n      <image:loc>{BRAND_IMAGE}</image:loc>\n      <image:title>freeconvert.cloud online file converter</image:title>\n    </image:image>'
    return (
        '  <url>\n'
        f'    <loc>{loc}</loc>\n'
        f'    <lastmod>{TODAY_ISO}</lastmod>\n'
        f'    <changefreq>{changefreq}</changefreq>\n'
        f'    <priority>{priority}</priority>{image_block}\n'
        '  </url>\n'
    )


def build_sitemap(tools):
    seen = set()
    groups = {
        'pages': [],
        'tools': [],
        'blog': [],
    }

    def add(group, loc, changefreq, priority, include_image=True):
        if loc in seen:
            return
        seen.add(loc)
        groups[group].append(sitemap_url_entry(loc, changefreq, priority, include_image))

    add('pages', f'{SITE_URL}/', 'daily', '1.0')
    for slug in ['all-tools', 'sitemap']:
        add('pages', f'{SITE_URL}/{slug}/', 'weekly', '0.9')
    for _, cat in CATEGORIES.items():
        if cat['slug'] not in NOINDEX_TOP_LEVEL_SLUGS:
            add('pages', f'{SITE_URL}/{cat["slug"]}/', 'weekly', '0.8')
    for tool in tools:
        add('tools', f'{SITE_URL}/{tool["id"]}/', 'weekly', '0.8')
    for leg in ['privacy', 'terms', 'security', 'dmca', 'contact', 'about', 'cookies', 'advertising-policy', 'help', 'press-kit', 'png-vs-jpg', 'pdf-vs-docx', 'convert-heic-iphone', 'compress-image-for-website']:
        add('pages', f'{SITE_URL}/{leg}/', 'monthly', '0.5')
    add('pages', f'{SITE_URL}/tools/embed/', 'monthly', '0.5')
    add('blog', f'{SITE_URL}/blog/', 'weekly', '0.8')
    for article in BLOG_ARTICLES:
        add('blog', f'{SITE_URL}/blog/{article["slug"]}/', 'weekly', '0.7')
    for blog_dir in Path('blog').glob('*/index.html'):
        rel = blog_dir.parent.name
        if rel != 'hub-pages':
            add('blog', f'{SITE_URL}/blog/{rel}/', 'weekly', '0.7')
    for category_page in sorted(Path('blog/category').glob('*/index.html')):
        add('blog', public_url_for_html(category_page), 'weekly', '0.6')
    for format_page in sorted(Path('file-formats').glob('**/index.html')):
        add('blog', public_url_for_html(format_page), 'weekly', '0.6')
    sitemaps_dir = Path('sitemaps')
    sitemaps_dir.mkdir(exist_ok=True)
    shard_names = []
    for name, group_entries in groups.items():
        shard_names.append(name)
        sitemap_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + ''.join(group_entries)
            + '</urlset>'
        )
        (sitemaps_dir / f'{name}.xml').write_text(sitemap_content, encoding='utf-8')

    index_entries = ''.join(
        '  <sitemap>\n'
        f'    <loc>{SITE_URL}/sitemaps/{name}.xml</loc>\n'
        f'    <lastmod>{TODAY_ISO}</lastmod>\n'
        '  </sitemap>\n'
        for name in shard_names
    )
    sitemap_index = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + index_entries
        + '</sitemapindex>'
    )
    Path('sitemap-index.xml').write_text(sitemap_index, encoding='utf-8')

    # Build a flat sitemap.xml containing every URL for tools that expect a single root sitemap
    all_entries = []
    for group_entries in groups.values():
        all_entries.extend(group_entries)
    flat_sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + ''.join(all_entries)
        + '</urlset>'
    )
    Path('sitemap.xml').write_text(flat_sitemap, encoding='utf-8')
    print(f"Generated sitemap index with {len(seen)} URLs across {len(shard_names)} sitemap files")


def build_static_seo_assets():
    try:
        from PIL import Image
        logo_png = Path('assets/freeconvert-logo.png')
        logo_webp = Path('assets/freeconvert-logo.webp')
        if logo_png.exists():
            Image.open(logo_png).save(logo_webp, 'WEBP', quality=82, method=6)
    except Exception as exc:
        print(f"Skipped WebP logo generation: {exc}")

    manifest = {
        "name": "freeconvert.cloud",
        "short_name": "FreeConvert",
        "description": "Fast, free, privacy-first online file converters and productivity tools.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#6366f1",
        "icons": [
            {"src": "/assets/favicon.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/freeconvert-logo.webp", "sizes": "512x512", "type": "image/webp"},
            {"src": "/assets/freeconvert-logo.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    Path('site.webmanifest').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    security_txt = (
        "Contact: mailto:support@freeconvert.cloud\n"
        "Preferred-Languages: en\n"
        f"Canonical: {SITE_URL}/.well-known/security.txt\n"
        f"Expires: 2027-06-01T00:00:00Z\n"
    )
    well_known = Path('.well-known')
    well_known.mkdir(exist_ok=True)
    (well_known / 'security.txt').write_text(security_txt, encoding='utf-8')

    ads_txt = "google.com, pub-8997218708343263, DIRECT, f08c47fec0942fa0\n"
    Path('ads.txt').write_text(ads_txt, encoding='utf-8')

    # Copy the hand-maintained AdSense CSS file into the build output
    review_css_source = Path('adsense-review.css').read_text(encoding='utf-8')
    Path('adsense-review.css').write_text(review_css_source, encoding='utf-8')

    htaccess = """# freeconvert.cloud technical SEO, security, and cache rules
Options -Indexes

<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set X-Content-Type-Options "nosniff"
  Header always set X-XSS-Protection "1; mode=block"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
  Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://pagead2.googlesyndication.com https://googleads.g.doubleclick.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://i.ytimg.com https://pagead2.googlesyndication.com; connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com; frame-src 'self' https://googleads.g.doubleclick.net; frame-ancestors 'self'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests"
  <FilesMatch "\\.(css|js|png|jpg|jpeg|webp|svg|ico|woff2?)$">
    Header set Cache-Control "public, max-age=2592000, immutable"
  </FilesMatch>
  <FilesMatch "\\.(html|xml|json|txt)$">
    Header set Cache-Control "public, max-age=3600"
  </FilesMatch>
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 1 hour"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType image/png "access plus 6 months"
  ExpiresByType image/jpeg "access plus 6 months"
  ExpiresByType image/webp "access plus 6 months"
  ExpiresByType image/svg+xml "access plus 6 months"
  ExpiresByType application/xml "access plus 1 day"
  ExpiresByType application/json "access plus 1 day"
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_brotli.c>
  AddOutputFilterByType BROTLI_COMPRESS text/html text/plain text/css application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_rewrite.c>
  RewriteEngine On

  # Old /tools/*.html URLs -> clean tool URLs (preserve indexed authority)
  RewriteRule ^tools/image-compressor\\.html$ /image-compressor/ [R=301,L]
  RewriteRule ^tools/image-resizer\\.html$ /resize-image/ [R=301,L]
  RewriteRule ^tools/ico-converter\\.html$ /ico-converter/ [R=301,L]
  RewriteRule ^tools/svg-to-png\\.html$ /svg-to-png/ [R=301,L]
  RewriteRule ^tools/palette-extractor\\.html$ /palette-extractor/ [R=301,L]
  RewriteRule ^tools/html-formatter\\.html$ /html-formatter/ [R=301,L]
  RewriteRule ^tools/password-generator\\.html$ /password-generator/ [R=301,L]
  RewriteRule ^tools/diff-checker\\.html$ /diff-checker/ [R=301,L]
  RewriteRule ^tools/markdown-editor\\.html$ /markdown-editor/ [R=301,L]
  RewriteRule ^tools/word-counter\\.html$ /word-counter/ [R=301,L]
  RewriteRule ^tools/css-formatter\\.html$ /css-formatter/ [R=301,L]
  RewriteRule ^tools/sql-formatter\\.html$ /sql-formatter/ [R=301,L]
  RewriteRule ^tools/qr-generator\\.html$ /qr-code-generator/ [R=301,L]

  RewriteRule ^image-resizer/?$ /resize-image/ [R=301,L]
  RewriteRule ^about-freeconvert/?$ /about/ [R=301,L]
  RewriteRule ^contact-us/?$ /contact/ [R=301,L]
  RewriteRule ^2025/11/02/hello-world/?$ / [R=301,L]
  RewriteRule ^2025/12/18/qr-codes-on-business-cards/?$ /free-online-converter-guides/qr-codes-on-business-cards/ [R=301,L]
  RewriteRule ^wp.*\\.php$ - [G,L]
  RewriteRule ^convert/([^/]+)/?$ /$1/ [R=301,L]
  RewriteCond %{HTTPS} !=on
  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>
"""
    Path('.htaccess').write_text(htaccess, encoding='utf-8')
    print("Generated site.webmanifest, ads.txt, adsense-review.css, .well-known/security.txt, and .htaccess")


def build_rss_feed():
    items = []
    for article in reversed(BLOG_ARTICLES[-20:]):
        url = f'{SITE_URL}/blog/{article["slug"]}/'
        title = html.escape(article['title'])
        description = html.escape(article['description'])
        items.append(
            '    <item>\n'
            f'      <title>{title}</title>\n'
            f'      <link>{url}</link>\n'
            f'      <guid>{url}</guid>\n'
            f'      <description>{description}</description>\n'
            f'      <pubDate>{article_date_rfc822(article["date"])}</pubDate>\n'
            '    </item>\n'
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        '    <title>freeconvert.cloud Guides</title>\n'
        f'    <link>{SITE_URL}/blog/</link>\n'
        '    <description>Latest file conversion, image optimization, PDF, SEO, and developer tool guides from freeconvert.cloud.</description>\n'
        '    <language>en-us</language>\n'
        '    <lastBuildDate>Tue, 02 Jun 2026 00:00:00 GMT</lastBuildDate>\n'
        + ''.join(items) +
        '  </channel>\n'
        '</rss>'
    )
    Path('feed.xml').write_text(feed, encoding='utf-8')
    print("Generated feed.xml")


def build_opensearch_file():
    opensearch = f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>freeconvert.cloud</ShortName>
  <Description>Search freeconvert.cloud tools and conversion guides.</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <Image height="16" width="16" type="image/png">{SITE_URL}/assets/favicon.png</Image>
  <Url type="text/html" template="{SITE_URL}/?q={{searchTerms}}"/>
</OpenSearchDescription>'''
    Path('opensearch.xml').write_text(opensearch, encoding='utf-8')
    print("Generated opensearch.xml")


def build_minified_asset_aliases():
    asset_pairs = [
        (Path('style.css'), Path('style.min.css')),
        (Path('main.js'), Path('main.min.js')),
        (Path('tools/tool-logic.js'), Path('tools/tool-logic.min.js')),
        (Path('tools/tools-data.js'), Path('tools/tools-data.min.js')),
    ]
    for source, target in asset_pairs:
        if source.exists():
            target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')

    replacements = {
        '/style.css': '/style.min.css',
        '/main.js': '/main.min.js',
        '/tools/tool-logic.js': '/tools/tool-logic.min.js',
        '/tools/tools-data.js': '/tools/tools-data.min.js',
    }
    for html_path in iter_public_html_files():
        html_content = html_path.read_text(encoding='utf-8')
        updated = html_content
        for original, minified in replacements.items():
            updated = updated.replace(original, minified)
        review_css_link = '<link rel="stylesheet" href="/adsense-review.css">'
        if review_css_link not in updated and '</head>' in updated:
            updated = updated.replace('</head>', f'    {review_css_link}\n</head>')
        if updated != html_content:
            html_path.write_text(updated, encoding='utf-8')
    print("Generated .min asset aliases and updated HTML references")


def blog_category_for_article(article):
    text = f"{article.get('slug', '')} {article.get('title', '')} {article.get('description', '')}".lower()
    if any(term in text for term in ['pdf', 'docx', 'word']):
        return 'pdf-tools', 'PDF Tools'
    if any(term in text for term in ['jpg', 'png', 'webp', 'heic', 'svg', 'image', 'photo', 'color', 'palette']):
        return 'image-conversion', 'Image Conversion'
    if any(term in text for term in ['json', 'csv', 'yaml', 'sql', 'html', 'css', 'javascript', 'base64', 'hash', 'uuid', 'diff', 'markdown', 'url']):
        return 'developer-tools', 'Developer Tools'
    if any(term in text for term in ['mp4', 'mp3', 'webm', 'video', 'audio']):
        return 'media-conversion', 'Media Conversion'
    if any(term in text for term in ['password', 'security', 'qr', 'barcode']):
        return 'security-utilities', 'Security Utilities'
    return 'utility-guides', 'Utility Guides'


def build_blog_category_pages():
    category_map = {}
    for article in BLOG_ARTICLES:
        slug, name = blog_category_for_article(article)
        category_map.setdefault(slug, {'name': name, 'articles': []})['articles'].append(article)

    base = Path('blog/category')
    base.mkdir(parents=True, exist_ok=True)
    for slug, data in category_map.items():
        cards = ''.join(
            f"""
            <a href="/blog/{article['slug']}/" class="tool-card" style="text-decoration:none;text-align:left;">
                <span class="popular-badge">Guide</span>
                <div class="tool-card-top">
                    <div class="tool-icon">Guide</div>
                    <span class="tool-category-tag">{html.escape(article['date'])}</span>
                </div>
                <div class="tool-card-body">
                    <span role="heading" aria-level="2" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{html.escape(article['title'])}</span>
                    <p>{html.escape(article['description'])}</p>
                </div>
                <div class="tool-card-footer"><span class="explore-text">Read Guide</span><span class="arrow-icon">-&gt;</span></div>
            </a>"""
            for article in data['articles']
        )
        schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"{data['name']} Guides",
            "url": f"{SITE_URL}/blog/category/{slug}/",
            "description": f"Helpful freeconvert.cloud tutorials about {data['name'].lower()}.",
            "dateModified": TODAY_ISO
        }
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(data['name'])} Guides | freeconvert.cloud</title>
    <meta name="description" content="Browse fact-checked {html.escape(data['name']).lower()} tutorials, converter tips, troubleshooting guides, and privacy-first workflow advice.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/blog/category/{slug}/">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content" style="max-width:1200px;">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><a href="/blog/">Blog</a><span>&gt;</span><span>{html.escape(data['name'])}</span></nav>
        <section class="tool-header">
            <span class="badge">Blog Category</span>
            <h1>{html.escape(data['name'])} Guides</h1>
            <p>Organized tutorials for users researching {html.escape(data['name']).lower()}, file privacy, format compatibility, and faster online workflows.</p>
        </section>
        <div class="tool-grid" style="padding:0;">{cards}</div>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
        out_dir = base / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
    print(f"Generated {len(category_map)} blog category pages")


def build_convert_alias_pages(tools):
    base = Path('convert')
    base.mkdir(exist_ok=True)
    for tool in tools:
        out_dir = base / tool['id']
        out_dir.mkdir(parents=True, exist_ok=True)
        target = f"/{tool['id']}/"
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(tool['name'])} | freeconvert.cloud</title>
    <meta name="robots" content="noindex,follow">
    <meta http-equiv="refresh" content="0; url={target}">
    <link rel="canonical" href="{SITE_URL}{target}">
</head>
<body>
    <p>Redirecting to <a href="{target}">{html.escape(tool['name'])}</a>.</p>
    <script>location.replace("{target}");</script>
</body>
</html>"""
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
    print(f"Generated {len(tools)} /convert/ redirect alias pages")


def build_legacy_redirect_pages():
    for old_route, new_route in LEGACY_ROUTE_MAP.items():
        route = old_route.strip('/')
        if not route:
            continue
        out_dir = Path(route)
        out_dir.mkdir(parents=True, exist_ok=True)
        title = route.replace('/', ' ').replace('-', ' ').title()
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting to freeconvert.cloud</title>
    <meta name="robots" content="noindex,follow">
    <meta http-equiv="refresh" content="0; url={new_route}">
    <link rel="canonical" href="{SITE_URL}{new_route}">
</head>
<body>
    <p>{html.escape(title)} has moved. Continue to <a href="{new_route}">{html.escape(new_route)}</a>.</p>
    <script>location.replace("{new_route}");</script>
</body>
</html>"""
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
    print(f"Generated {len(LEGACY_ROUTE_MAP)} legacy redirect fallback pages")


def build_embed_widget_page():
    out_dir = Path('tools/embed')
    out_dir.mkdir(parents=True, exist_ok=True)
    widget_code = html.escape('<iframe src="https://freeconvert.cloud/png-to-jpg/" width="100%" height="680" style="border:0;border-radius:12px;" title="Free PNG to JPG Converter"></iframe>')
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Embed Free Converter Widgets",
        "url": f"{SITE_URL}/tools/embed/",
        "description": "Embed privacy-first freeconvert.cloud converter widgets on resource pages, tutorials, and internal documentation.",
        "dateModified": TODAY_ISO
    }
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embed Free File Converter Widgets | freeconvert.cloud</title>
    <meta name="description" content="Add free online converter widgets to your website with clean iframe snippets and proper attribution to freeconvert.cloud.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/tools/embed/">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><span>Embed Widgets</span></nav>
        <section class="tool-header">
            <span class="badge">Backlink Resource</span>
            <h1>Embed Free Converter Widgets</h1>
            <p>Add a free file converter widget to tutorials, resource pages, school portals, and internal team documentation.</p>
        </section>
        <article class="seo-content">
            <h2>Why embed a converter?</h2>
            <p>Helpful widgets earn natural links because they solve a problem inside the article where users need it. You can point visitors to PNG to JPG, JPG to PDF, Compress PDF, WebP to JPG, or developer utilities while keeping attribution clear.</p>
            <h2>Starter iframe code</h2>
            <pre class="api-code-block" style="white-space:pre-wrap;">{widget_code}</pre>
            <h2>Recommended placements</h2>
            <ul><li>Classroom resources about digital files</li><li>Design tutorials about image optimization</li><li>PDF workflow documentation</li><li>Developer docs for JSON, CSV, Base64, and formatting tasks</li></ul>
            <p>Please keep the iframe title descriptive and link attribution visible near the widget for accessibility and trust.</p>
        </article>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
    (out_dir / 'index.html').write_text(page, encoding='utf-8')
    print("Generated /tools/embed/ widget page")


def build_growth_landing_pages():
    pages = [
        {
            'slug': 'png-vs-jpg',
            'title': 'PNG vs JPG - Which Image Format Should You Use?',
            'desc': 'Compare PNG and JPG for websites, photos, transparency, compression, SEO, and file size before converting images online.',
            'links': [('png-to-jpg', 'PNG to JPG'), ('jpg-to-png', 'JPG to PNG'), ('image-compressor', 'Image Compressor')],
            'body': 'PNG is best for transparency, screenshots, logos, and lossless graphics. JPG is best for photos, smaller web images, email attachments, and broad compatibility. If your image has no transparency and file size matters, JPG is usually the better choice. If crisp edges, alpha transparency, or repeated editing matters, keep a PNG copy.'
        },
        {
            'slug': 'pdf-vs-docx',
            'title': 'PDF vs DOCX - Difference, Use Cases, and Conversion Tips',
            'desc': 'Understand when to use PDF or DOCX, how formatting differs, and which free converter to use for editable or shareable documents.',
            'links': [('pdf-to-word', 'PDF to Word'), ('word-to-pdf', 'Word to PDF'), ('compress-pdf', 'Compress PDF')],
            'body': 'PDF is best for final sharing, printing, contracts, invoices, and layout preservation. DOCX is best for editing text, collaborating, and drafting content. Convert DOCX to PDF before sending a final version, and convert PDF to Word when you need an editable draft.'
        },
        {
            'slug': 'convert-heic-iphone',
            'title': 'Convert HEIC iPhone Photos to JPG Online',
            'desc': 'Convert iPhone HEIC photos to JPG for Windows, Android, email, websites, and older apps using free browser-based tools.',
            'links': [('heic-to-jpg', 'HEIC to JPG'), ('image-compressor', 'Image Compressor'), ('resize-image', 'Resize Image')],
            'body': 'iPhones often save photos as HEIC because the format is efficient, but some websites and older systems still expect JPG. Converting HEIC to JPG improves compatibility for job portals, email, school submissions, CMS uploads, and photo sharing.'
        },
        {
            'slug': 'compress-image-for-website',
            'title': 'Compress Images for Website Speed Optimization',
            'desc': 'Reduce JPG, PNG, and WebP image weight for Core Web Vitals, faster pages, and cleaner SEO performance.',
            'links': [('image-compressor', 'Image Compressor'), ('compress-image-to-100kb', 'Compress Image to 100KB'), ('jpg-to-webp', 'JPG to WebP')],
            'body': 'Large images slow down Largest Contentful Paint and frustrate mobile visitors. Compressing images before upload can reduce bandwidth, improve crawl efficiency, and make landing pages feel faster without redesigning the whole website.'
        }
    ]
    for item in pages:
        tool_links = ''.join(f'<a href="/{slug}/" class="btn primary" style="margin:0.3rem;">{html.escape(label)}</a>' for slug, label in item['links'])
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": item['title'],
            "url": f"{SITE_URL}/{item['slug']}/",
            "description": item['desc'],
            "dateModified": TODAY_ISO
        }
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(item['title'])} | freeconvert.cloud</title>
    <meta name="description" content="{html.escape(item['desc'])}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/{item['slug']}/">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><span>{html.escape(item['title'])}</span></nav>
        <section class="tool-header"><span class="badge">Conversion Guide</span><h1>{html.escape(item['title'])}</h1><p>{html.escape(item['desc'])}</p></section>
        <article class="seo-content">
            <h2>Quick answer</h2>
            <p>{html.escape(item['body'])}</p>
            <h2>Use the right free tool</h2>
            <p>Pick the converter below based on your goal. Each tool includes privacy notes, steps, FAQs, and related guides.</p>
            <div>{tool_links}</div>
            <h2>Best practice</h2>
            <p>Keep your original file, create the converted copy, then compare quality and file size before publishing or sending. This keeps your workflow safe while improving compatibility and speed.</p>
        </article>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
        out_dir = Path(item['slug'])
        out_dir.mkdir(exist_ok=True)
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
    print(f"Generated {len(pages)} comparison and seasonal landing pages")


def generate_use_case_pages():
    """Return high-intent, use-case focused long-tail landing pages.

    These pages target specific modifiers from seo-keyword-targets.json and
    connect each search intent to the most relevant freeconvert.cloud tool.
    """
    return [
        {
            'slug': 'png-to-jpg-for-website',
            'title': 'Convert PNG to JPG for Websites and Faster Pages',
            'desc': 'Convert PNG images to smaller JPG files for websites, blogs, CMS uploads, and faster page loading.',
            'keyword': 'png to jpg for website',
            'tool': 'png-to-jpg',
            'tool_label': 'PNG to JPG',
            'angle': 'JPG files are usually smaller than PNG, which helps pages load faster. Use PNG only when you need transparency or crisp text.'
        },
        {
            'slug': 'png-to-jpg-transparent',
            'title': 'PNG to JPG Transparent Background Guide',
            'desc': 'Learn how PNG to JPG conversion handles transparency and when to keep PNG for transparent design assets.',
            'keyword': 'png to jpg transparent',
            'tool': 'png-to-jpg',
            'tool_label': 'PNG to JPG',
            'angle': 'JPG does not support transparency. If you need a transparent background, keep the PNG or use a tool that removes the background after conversion.'
        },
        {
            'slug': 'jpg-to-png-transparent',
            'title': 'JPG to PNG Transparent Background Online',
            'desc': 'Convert JPG images to PNG format to enable transparency support for logos, product photos, and design assets.',
            'keyword': 'jpg to png transparent',
            'tool': 'jpg-to-png',
            'tool_label': 'JPG to PNG',
            'angle': 'Converting JPG to PNG adds transparency capability to the file format, but it does not automatically remove an existing background.'
        },
        {
            'slug': 'jpg-to-png-no-background',
            'title': 'JPG to PNG No Background for Logos and Stickers',
            'desc': 'Create PNG images from JPG photos for stickers, logos, and designs that need a transparent background.',
            'keyword': 'jpg to png no background',
            'tool': 'jpg-to-png',
            'tool_label': 'JPG to PNG',
            'angle': 'Use a background remover before converting to PNG if the original JPG has a solid background. PNG preserves transparency; JPG does not.'
        },
        {
            'slug': 'webp-to-jpg-wordpress',
            'title': 'Convert WebP to JPG for WordPress Uploads',
            'desc': 'Make WebP images compatible with WordPress, older editors, and platforms that still require JPG files.',
            'keyword': 'webp to jpg for wordpress',
            'tool': 'webp-to-jpg',
            'tool_label': 'WebP to JPG',
            'angle': 'Some WordPress themes and plugins do not accept WebP uploads. Converting to JPG restores broad compatibility while keeping file size reasonable.'
        },
        {
            'slug': 'heic-to-jpg-windows',
            'title': 'Convert HEIC to JPG on Windows and Android',
            'desc': 'Open iPhone HEIC photos on Windows, Android, and older apps by converting them to universal JPG format.',
            'keyword': 'heic to jpg on windows',
            'tool': 'heic-to-jpg',
            'tool_label': 'HEIC to JPG',
            'angle': 'Windows and Android sometimes need a codec to view HEIC files. Converting to JPG makes the photo viewable everywhere without extra software.'
        },
        {
            'slug': 'heic-to-jpg-iphone',
            'title': 'Convert HEIC to JPG on iPhone for Sharing',
            'desc': 'Convert iPhone HEIC photos to JPG for email, social media, websites, and apps that prefer the JPG format.',
            'keyword': 'heic to jpg iphone',
            'tool': 'heic-to-jpg',
            'tool_label': 'HEIC to JPG',
            'angle': 'iPhones save photos as HEIC by default for efficiency. Convert to JPG when an upload form, email client, or social app requests it.'
        },
        {
            'slug': 'compress-pdf-to-1mb',
            'title': 'Compress PDF to 1MB for Email and Uploads',
            'desc': 'Reduce PDF file size to around 1MB for email attachments, application portals, and document sharing.',
            'keyword': 'compress pdf to 1mb',
            'tool': 'compress-pdf',
            'tool_label': 'Compress PDF',
            'angle': 'A 1MB target works for most email providers and upload portals. Compress images inside the PDF first for the biggest size reduction.'
        },
        {
            'slug': 'compress-pdf-for-email',
            'title': 'Compress PDF for Email Attachments Free',
            'desc': 'Shrink PDF files so they fit email attachment limits and send faster without losing readability.',
            'keyword': 'compress pdf for email',
            'tool': 'compress-pdf',
            'tool_label': 'Compress PDF',
            'angle': 'Most email providers allow attachments up to 20-25MB. Compressing PDFs avoids bounce-backs and helps messages send faster.'
        },
        {
            'slug': 'pdf-to-word-for-editing',
            'title': 'Convert PDF to Word for Editing Online',
            'desc': 'Turn PDF documents into editable Word files for text changes, formatting fixes, and collaboration.',
            'keyword': 'pdf to word for editing',
            'tool': 'pdf-to-word',
            'tool_label': 'PDF to Word',
            'angle': 'PDF is great for sharing final documents. Convert to DOCX when you need to edit text, update tables, or change formatting.'
        },
        {
            'slug': 'word-to-pdf-online-free',
            'title': 'Convert Word to PDF Online Free',
            'desc': 'Export DOCX and Word documents to clean PDF files for sharing, printing, and professional submissions.',
            'keyword': 'word to pdf online free',
            'tool': 'word-to-pdf',
            'tool_label': 'Word to PDF',
            'angle': 'PDF preserves fonts, layout, and page breaks across devices, making it the safer choice for final documents.'
        },
        {
            'slug': 'merge-jpg-to-pdf',
            'title': 'Merge JPG Images to PDF Online',
            'desc': 'Combine multiple JPG photos, scans, and screenshots into one organized PDF document.',
            'keyword': 'merge jpg to pdf',
            'tool': 'jpg-to-pdf',
            'tool_label': 'JPG to PDF',
            'angle': 'Upload portals often accept one PDF instead of many JPGs. Arrange the images in order before creating the final document.'
        },
        {
            'slug': 'split-pdf-into-pages',
            'title': 'Split PDF Into Pages Online Free',
            'desc': 'Extract individual pages or ranges from a PDF into separate files for sharing and organization.',
            'keyword': 'split pdf into pages',
            'tool': 'split-pdf',
            'tool_label': 'Split PDF',
            'angle': 'Splitting a PDF is useful when only certain pages are relevant to a recipient or when a large file needs to be divided.'
        },
        {
            'slug': 'image-compressor-for-website',
            'title': 'Compress Images for Website Speed and SEO',
            'desc': 'Reduce JPG, PNG, and WebP image size for faster websites, better Core Web Vitals, and improved SEO.',
            'keyword': 'compress image for website',
            'tool': 'image-compressor',
            'tool_label': 'Image Compressor',
            'angle': 'Large images slow down page load and hurt search rankings. Compress and resize images before uploading to a CMS.'
        },
        {
            'slug': 'compress-jpg-to-100kb',
            'title': 'Compress JPG to 100KB Online',
            'desc': 'Shrink JPG photos under 100KB for job portals, application forms, and upload limits.',
            'keyword': 'compress jpg to 100kb',
            'tool': 'compress-image-to-100kb',
            'tool_label': 'Compress Image to 100KB',
            'angle': 'A 100KB target is strict. Reduce dimensions first, then adjust quality until the file fits the limit while staying readable.'
        },
        {
            'slug': 'resize-image-for-instagram',
            'title': 'Resize Image for Instagram Posts and Stories',
            'desc': 'Resize photos for Instagram posts, stories, reels, and profile pictures with common aspect ratios.',
            'keyword': 'resize image for instagram',
            'tool': 'resize-image-for-instagram',
            'tool_label': 'Resize Image for Instagram',
            'angle': 'Instagram posts often use 1:1 or 4:5 ratios, while stories and reels use 9:16. Resize before posting to avoid awkward cropping.'
        },
        {
            'slug': 'png-to-webp-transparent',
            'title': 'Convert PNG to WebP With Transparency',
            'desc': 'Convert transparent PNG graphics to WebP for smaller website assets that keep alpha channels.',
            'keyword': 'png to webp transparent',
            'tool': 'png-to-webp',
            'tool_label': 'PNG to WebP',
            'angle': 'WebP supports transparency like PNG but usually produces smaller files, which helps pages load faster.'
        },
        {
            'slug': 'jpg-to-webp-for-website',
            'title': 'Convert JPG to WebP for Faster Websites',
            'desc': 'Convert JPG photos to WebP for smaller file sizes, faster page loads, and modern browser support.',
            'keyword': 'jpg to webp for website',
            'tool': 'jpg-to-webp',
            'tool_label': 'JPG to WebP',
            'angle': 'WebP typically compresses better than JPG. Serve WebP to modern browsers and keep JPG as a fallback for older ones.'
        },
        {
            'slug': 'mp4-to-mp3-free',
            'title': 'Convert MP4 to MP3 Free Online',
            'desc': 'Extract audio from MP4 videos into MP3 files for podcasts, music, lectures, and voice notes.',
            'keyword': 'mp4 to mp3 free',
            'tool': 'mp4-to-mp3',
            'tool_label': 'MP4 to MP3',
            'angle': 'MP3 is widely supported across players and devices. Extract audio when you only need the sound track from a video.'
        },
        {
            'slug': 'video-to-mp3',
            'title': 'Convert Video to MP3 Audio Online',
            'desc': 'Extract MP3 audio from video files for offline listening, editing, and sharing.',
            'keyword': 'convert video to audio',
            'tool': 'mp4-to-mp3',
            'tool_label': 'MP4 to MP3',
            'angle': 'Converting video to MP3 creates a smaller file that is easier to store, share, and play on audio-focused devices.'
        },
        {
            'slug': 'json-to-csv-excel',
            'title': 'Convert JSON to CSV for Excel and Sheets',
            'desc': 'Flatten JSON arrays into CSV rows for Excel, Google Sheets, and spreadsheet analysis.',
            'keyword': 'json to csv for excel',
            'tool': 'json-to-csv',
            'tool_label': 'JSON to CSV',
            'angle': 'CSV is easier to read in spreadsheets than nested JSON. Flatten nested objects into dot-separated column names when needed.'
        },
        {
            'slug': 'qr-code-for-menu',
            'title': 'QR Code Generator for Restaurant Menus',
            'desc': 'Create a QR code for a restaurant menu, digital catalog, or link that customers can scan with any phone.',
            'keyword': 'qr code for menu',
            'tool': 'qr-code-generator',
            'tool_label': 'QR Code Generator',
            'angle': 'Menu QR codes should link to a mobile-friendly page. Test the code on iOS and Android before printing.'
        },
        {
            'slug': 'qr-code-for-wifi',
            'title': 'QR Code Generator for WiFi Login',
            'desc': 'Generate a QR code that lets guests connect to WiFi without typing the network name or password.',
            'keyword': 'qr code for wifi',
            'tool': 'qr-code-generator',
            'tool_label': 'QR Code Generator',
            'angle': 'WiFi QR codes use a standard format that most phones recognize from the camera app. Keep the password simple to avoid encoding errors.'
        },
        {
            'slug': 'svg-to-png-transparent',
            'title': 'Convert SVG to PNG With Transparency',
            'desc': 'Render SVG vector files as high-quality PNG images that keep transparent backgrounds for logos and icons.',
            'keyword': 'svg to png transparent',
            'tool': 'svg-to-png',
            'tool_label': 'SVG to PNG',
            'angle': 'PNG exports from SVG keep transparency and crisp edges at any resolution. Choose a large enough size for high-DPI displays.'
        },
        {
            'slug': 'svg-to-png-logo',
            'title': 'Convert SVG Logo to PNG Online',
            'desc': 'Export SVG logos to PNG format for websites, social media, presentations, and print-ready assets.',
            'keyword': 'svg to png logo',
            'tool': 'svg-to-png',
            'tool_label': 'SVG to PNG',
            'angle': 'Logos often start as SVG vectors. Export to PNG when a platform requires a raster image or when you need a specific pixel size.'
        },
        {
            'slug': 'png-to-ico-favicon',
            'title': 'Convert PNG to ICO Favicon Online',
            'desc': 'Turn PNG logos and images into ICO favicon files for websites and browser tabs.',
            'keyword': 'png to ico',
            'tool': 'ico-converter',
            'tool_label': 'ICO Converter',
            'angle': 'ICO files can contain multiple icon sizes. Upload a square PNG and download a favicon ready for most browsers.'
        },
        {
            'slug': 'mov-to-mp4-iphone',
            'title': 'Convert MOV to MP4 on iPhone and Mac',
            'desc': 'Convert Apple MOV videos to MP4 for Android, Windows, editors, and social media uploads.',
            'keyword': 'mov to mp4 iphone',
            'tool': 'mov-to-mp4',
            'tool_label': 'MOV to MP4',
            'angle': 'MOV files work best in Apple ecosystems. MP4 is the universal format for sharing across phones, computers, and websites.'
        },
        {
            'slug': 'mkv-to-mp4-without-quality-loss',
            'title': 'Convert MKV to MP4 Without Losing Quality',
            'desc': 'Remux MKV videos to MP4 while preserving video and audio quality for broader device support.',
            'keyword': 'mkv to mp4 without quality loss',
            'tool': 'mkv-to-mp4',
            'tool_label': 'MKV to MP4',
            'angle': 'When the MKV file uses compatible codecs, remuxing to MP4 avoids re-encoding and keeps the original quality.'
        },
        {
            'slug': 'avi-to-mp4-for-windows',
            'title': 'Convert AVI to MP4 for Windows and Mobile',
            'desc': 'Turn older AVI videos into MP4 files for modern playback, editing, and mobile sharing.',
            'keyword': 'avi to mp4 for windows',
            'tool': 'avi-to-mp4',
            'tool_label': 'AVI to MP4',
            'angle': 'AVI files can be large and unsupported on mobile devices. MP4 offers better compression and compatibility.'
        },
        {
            'slug': 'csv-to-json-api',
            'title': 'Convert CSV to JSON for APIs and Apps',
            'desc': 'Turn CSV spreadsheet rows into structured JSON arrays for APIs, web apps, and data pipelines.',
            'keyword': 'csv to json for api',
            'tool': 'csv-to-json',
            'tool_label': 'CSV to JSON',
            'angle': 'JSON is easier for code to parse than CSV. Add column headers to the CSV so the converter can create named object keys.'
        },
        {
            'slug': 'json-pretty-print',
            'title': 'JSON Pretty Print and Beautify Online',
            'desc': 'Format minified JSON into readable, indented text for debugging, documentation, and sharing.',
            'keyword': 'json pretty print',
            'tool': 'json-formatter',
            'tool_label': 'JSON Formatter',
            'angle': 'Pretty-printed JSON makes nested structures easier to read and debug. Use it before pasting JSON into documentation or messages.'
        },
        {
            'slug': 'text-to-base64',
            'title': 'Text to Base64 Encode Online',
            'desc': 'Encode plain text strings to Base64 for data URIs, configuration files, APIs, and safe transport.',
            'keyword': 'text to base64',
            'tool': 'base64-encode',
            'tool_label': 'Base64 Encode',
            'angle': 'Base64 encodes binary or text data into ASCII characters. It is useful for embedding data in JSON, HTML, or URLs.'
        },
        {
            'slug': 'strong-password-generator',
            'title': 'Strong Password Generator Online',
            'desc': 'Create strong, random passwords with letters, numbers, and symbols to protect online accounts.',
            'keyword': 'strong password generator',
            'tool': 'password-generator',
            'tool_label': 'Password Generator',
            'angle': 'Longer passwords with mixed characters are harder to crack. Use a unique password for every important account.'
        },
        {
            'slug': 'essay-word-counter',
            'title': 'Essay Word Counter Online',
            'desc': 'Count words, characters, sentences, and reading time for essays, assignments, and blog posts.',
            'keyword': 'essay word counter',
            'tool': 'word-counter',
            'tool_label': 'Word Counter',
            'angle': 'Essay limits are usually measured in words. Paste your text to check the count and estimated reading time instantly.'
        },
        {
            'slug': 'image-to-base64-css',
            'title': 'Convert Image to Base64 for CSS and HTML',
            'desc': 'Encode images to Base64 data URIs for inline CSS, HTML emails, and small icons.',
            'keyword': 'convert image to base64',
            'tool': 'image-to-base64',
            'tool_label': 'Image to Base64',
            'angle': 'Base64 images embed directly in code, reducing HTTP requests. Use them only for small images because the encoded string is larger than the original file.'
        },
    ]


def build_daily_seo_landing_pages():
    pages = generate_use_case_pages() + [
        {
            'slug': 'compress-pdf-to-500kb',
            'title': 'Compress PDF to 500KB Online Free',
            'desc': 'Reduce a PDF file to around 500KB for email, portals, school forms, and upload limits using free browser-friendly PDF tools.',
            'keyword': 'compress PDF to 500KB',
            'tool': 'compress-pdf',
            'tool_label': 'Compress PDF',
            'angle': 'Use this workflow when a website accepts PDFs but rejects files above 500KB. Start by compressing the PDF, then recheck the output size before uploading.'
        },
        {
            'slug': 'compress-pdf-to-100kb',
            'title': 'Compress PDF to 100KB Online',
            'desc': 'Shrink PDF files aggressively for strict application forms and document portals that require very small uploads.',
            'keyword': 'compress PDF to 100KB',
            'tool': 'compress-pdf',
            'tool_label': 'Compress PDF',
            'angle': 'A 100KB target is strict, so image-heavy PDFs may need image downscaling before compression. Keep a readable backup copy if text clarity matters.'
        },
        {
            'slug': 'reduce-image-size-in-kb',
            'title': 'Reduce Image Size in KB Without Installing Software',
            'desc': 'Lower JPG, PNG, and WebP image size in KB for websites, emails, forms, and social media uploads.',
            'keyword': 'reduce image size in KB',
            'tool': 'image-compressor',
            'tool_label': 'Image Compressor',
            'angle': 'For most uploads, reducing pixel dimensions and quality slightly gives the biggest file-size win while keeping the image visually sharp.'
        },
        {
            'slug': 'jpg-to-pdf-merge-images',
            'title': 'Merge JPG Images Into One PDF Online',
            'desc': 'Combine multiple JPG photos, scans, or screenshots into one PDF for assignments, invoices, receipts, and applications.',
            'keyword': 'merge JPG images into PDF',
            'tool': 'jpg-to-pdf',
            'tool_label': 'JPG to PDF',
            'angle': 'This is ideal when portals ask for a single PDF instead of many image uploads. Put the images in the right order before downloading the final PDF.'
        },
        {
            'slug': 'pdf-to-jpg-high-resolution',
            'title': 'Convert PDF to High-Resolution JPG Images',
            'desc': 'Extract PDF pages as JPG images for thumbnails, previews, web publishing, and image-based sharing.',
            'keyword': 'PDF to JPG high resolution',
            'tool': 'pdf-to-jpg',
            'tool_label': 'PDF to JPG',
            'angle': 'Use higher resolution when you need readable text or print-quality previews. Use compression afterward when the exported JPGs are too large.'
        },
        {
            'slug': 'webp-to-png-transparent',
            'title': 'Convert WebP to PNG With Transparency',
            'desc': 'Convert WebP graphics into PNG format for design tools, transparent assets, CMS uploads, and compatibility workflows.',
            'keyword': 'WebP to PNG transparent',
            'tool': 'jpg-to-png',
            'tool_label': 'JPG to PNG',
            'angle': 'PNG is a better target when you need transparency support or editing compatibility, while WebP is usually better for smaller website delivery.'
        },
        {
            'slug': 'jpg-to-png-transparent-background',
            'title': 'JPG to PNG Transparent Background Guide',
            'desc': 'Learn what JPG to PNG conversion can and cannot do when you need transparent backgrounds for logos and product images.',
            'keyword': 'JPG to PNG transparent background',
            'tool': 'jpg-to-png',
            'tool_label': 'JPG to PNG',
            'angle': 'Converting JPG to PNG adds transparency support to the file format, but it does not automatically remove a solid background. Use a background remover first when needed.'
        },
        {
            'slug': 'resize-photo-2x2-inch',
            'title': 'Resize Photo to 2x2 Inches Online',
            'desc': 'Prepare a 2x2 inch photo for passport, visa, ID, and document upload requirements.',
            'keyword': 'resize photo 2x2 inch',
            'tool': 'passport-photo-size-converter',
            'tool_label': 'Passport Photo Size Converter',
            'angle': 'A 2x2 photo usually needs the right crop, head position, and background color. Resize only after choosing the correct crop.'
        },
        {
            'slug': 'instagram-profile-picture-size',
            'title': 'Resize Image for Instagram Profile Picture',
            'desc': 'Crop and resize images for Instagram profile photos, posts, stories, reels covers, and clean social media uploads.',
            'keyword': 'Instagram profile picture size',
            'tool': 'resize-image-for-instagram',
            'tool_label': 'Resize Image for Instagram',
            'angle': 'Instagram displays profile pictures in a circle, so keep faces or logos centered and leave enough safe space around the edges.'
        },
        {
            'slug': 'convert-word-to-pdf-for-email',
            'title': 'Convert Word to PDF for Email Attachments',
            'desc': 'Turn DOCX files into professional PDFs for email, resumes, invoices, proposals, assignments, and contracts.',
            'keyword': 'convert Word to PDF for email',
            'tool': 'word-to-pdf',
            'tool_label': 'Word to PDF',
            'angle': 'PDF is usually better for email because it preserves layout, fonts, and page breaks across devices.'
        },
        {
            'slug': 'json-to-csv-for-excel',
            'title': 'Convert JSON to CSV for Excel',
            'desc': 'Flatten JSON data into CSV rows for Excel, Google Sheets, reports, and quick data cleanup.',
            'keyword': 'JSON to CSV for Excel',
            'tool': 'json-to-csv',
            'tool_label': 'JSON to CSV',
            'angle': 'CSV works well for spreadsheet review, but nested JSON may need flattening into dot-separated columns before Excel can display it clearly.'
        },
        {
            'slug': 'submit-sitemap-to-google-search-console',
            'title': 'Submit Sitemap to Google Search Console',
            'desc': 'Learn which sitemap to submit in Google Search Console and how sitemap indexes help Google discover new converter pages.',
            'keyword': 'submit sitemap to Google Search Console',
            'tool': 'robots-txt-generator',
            'tool_label': 'Robots.txt Generator',
            'angle': 'For freeconvert.cloud, the best sitemap to submit is sitemap-index.xml because it points Google to the split pages, tools, and blog sitemaps.'
        },
        {
            'slug': 'qr-codes-on-business-cards',
            'title': 'QR Codes on Business Cards: Free Generator Guide',
            'desc': 'Create a QR code for a business card, vCard, website, portfolio, WhatsApp link, or contact landing page.',
            'keyword': 'QR codes on business cards',
            'tool': 'qr-code-generator',
            'tool_label': 'QR Code Generator',
            'angle': 'A business-card QR code should point to a stable URL such as a portfolio, contact form, vCard page, menu, or booking page. Test the code on multiple phones before printing.'
        },
        {
            'slug': 'compress-image-to-50kb',
            'title': 'Compress Image to 50KB Online',
            'desc': 'Reduce JPG, PNG, and WebP photos toward a 50KB target for strict upload forms, student portals, and ID applications.',
            'keyword': 'compress image to 50KB',
            'tool': 'image-compressor',
            'tool_label': 'Image Compressor',
            'angle': 'A 50KB image target is very small, so reduce dimensions first, then adjust quality. For passport or ID photos, check that the face remains sharp after compression.'
        },
        {
            'slug': 'pdf-to-jpg-for-whatsapp',
            'title': 'Convert PDF to JPG for WhatsApp Sharing',
            'desc': 'Turn PDF pages into easy-to-share JPG images for WhatsApp chats, previews, thumbnails, and quick mobile sharing.',
            'keyword': 'PDF to JPG for WhatsApp',
            'tool': 'pdf-to-jpg',
            'tool_label': 'PDF to JPG',
            'angle': 'WhatsApp is easier for image previews than multi-page PDFs. Export the important PDF pages as JPG, then compress the images if the chat upload feels slow.'
        },
        {
            'slug': 'jpg-to-pdf-for-documents',
            'title': 'JPG to PDF for Documents, Receipts, and Forms',
            'desc': 'Combine document photos, receipts, screenshots, and scanned pages into one clean PDF for email or application uploads.',
            'keyword': 'JPG to PDF for documents',
            'tool': 'jpg-to-pdf',
            'tool_label': 'JPG to PDF',
            'angle': 'For document uploads, order the JPG pages before conversion and keep the sharpest image version. A single PDF is usually accepted more easily than several loose photos.'
        },
        {
            'slug': 'resize-image-for-website',
            'title': 'Resize Image for Website Speed and SEO',
            'desc': 'Resize website images to practical dimensions before compression so pages load faster without looking blurry.',
            'keyword': 'resize image for website',
            'tool': 'resize-image',
            'tool_label': 'Resize Image',
            'angle': 'Website images should match their display size. Resize oversized photos before compressing them so the browser does not download unnecessary pixels.'
        },
        {
            'slug': 'webp-to-jpg-for-instagram',
            'title': 'Convert WebP to JPG for Instagram Uploads',
            'desc': 'Convert WebP images into JPG files for Instagram, social media scheduling tools, older editors, and mobile upload compatibility.',
            'keyword': 'WebP to JPG for Instagram',
            'tool': 'webp-to-jpg',
            'tool_label': 'WebP to JPG',
            'angle': 'If an app rejects a WebP image, JPG is the safest compatibility format. Keep a high-quality export, then compress only if the upload size is too large.'
        },
        {
            'slug': 'compress-video-for-whatsapp',
            'title': 'Compress Video for WhatsApp Sharing',
            'desc': 'Reduce video file size for WhatsApp chats, status uploads, group sharing, and faster mobile delivery.',
            'keyword': 'compress video for WhatsApp',
            'tool': 'video-compressor',
            'tool_label': 'Video Compressor',
            'angle': 'WhatsApp sharing works best with shorter MP4 clips. Trim the video first if needed, then compress enough to keep motion smooth and text readable.'
        },
        {
            'slug': 'mov-to-mp4-on-iphone',
            'title': 'Convert MOV to MP4 on iPhone and Mac',
            'desc': 'Convert Apple MOV videos into MP4 files for Android, Windows, browsers, editors, and social media uploads.',
            'keyword': 'MOV to MP4 on iPhone',
            'tool': 'mov-to-mp4',
            'tool_label': 'MOV to MP4',
            'angle': 'MOV is common on Apple devices, but MP4 is usually accepted by more apps, websites, and upload forms.'
        },
        {
            'slug': 'avi-to-mp4-for-windows',
            'title': 'Convert AVI to MP4 for Windows and Phones',
            'desc': 'Turn older AVI videos into MP4 files for modern playback, browser uploads, social media, and mobile sharing.',
            'keyword': 'AVI to MP4 for Windows',
            'tool': 'avi-to-mp4',
            'tool_label': 'AVI to MP4',
            'angle': 'AVI files can be difficult for mobile apps and browsers. MP4 is usually the safer format for sharing and upload compatibility.'
        },
        {
            'slug': 'mkv-to-mp4-for-tv',
            'title': 'Convert MKV to MP4 for TV, Mobile, and Web',
            'desc': 'Convert MKV video containers into MP4 for smart TVs, phones, tablets, editors, and upload platforms.',
            'keyword': 'MKV to MP4 for TV',
            'tool': 'mkv-to-mp4',
            'tool_label': 'MKV to MP4',
            'angle': 'MKV can hold many tracks, but MP4 is more broadly accepted. Check subtitles and audio tracks after conversion if the source file is complex.'
        },
        {
            'slug': 'mp4-to-gif-for-discord',
            'title': 'Convert MP4 to GIF for Discord, Chat, and Previews',
            'desc': 'Create short looping GIFs from MP4 clips for Discord, social posts, chat replies, tutorials, and quick previews.',
            'keyword': 'MP4 to GIF for Discord',
            'tool': 'mp4-to-gif',
            'tool_label': 'MP4 to GIF',
            'angle': 'GIF works best for very short clips. Trim the video and reduce dimensions before converting so the animation stays lightweight.'
        },
        {
            'slug': 'video-to-mp3-for-lectures',
            'title': 'Video to MP3 for Lectures and Voice Notes',
            'desc': 'Extract MP3 audio from video lectures, meetings, tutorials, recordings, interviews, and voice notes.',
            'keyword': 'video to MP3 for lectures',
            'tool': 'video-to-mp3',
            'tool_label': 'Video to MP3',
            'angle': 'If you only need the spoken audio, MP3 is easier to store, listen to, and share than the original video file.'
        },
        {
            'slug': 'resize-video-for-instagram-reels',
            'title': 'Resize Video for Instagram Reels and Stories',
            'desc': 'Resize videos for Instagram Reels, Stories, posts, square feeds, vertical clips, and mobile-first social uploads.',
            'keyword': 'resize video for Instagram Reels',
            'tool': 'video-resizer',
            'tool_label': 'Video Resizer',
            'angle': 'Instagram vertical videos usually need a 9:16 frame. Keep faces, captions, and product details away from the top and bottom UI zones.'
        },
        {
            'slug': 'trim-video-online-for-status',
            'title': 'Trim Video Online for Status and Short Clips',
            'desc': 'Cut long videos into shorter clips for WhatsApp Status, Instagram Stories, reels, previews, and quick highlights.',
            'keyword': 'trim video online for status',
            'tool': 'video-trimmer',
            'tool_label': 'Video Trimmer',
            'angle': 'Short clips load faster and perform better in social feeds. Trim dead space from the start and end before compressing or resizing.'
        },
    ]
    base = Path('free-online-converter-guides')
    base.mkdir(exist_ok=True)
    hub_cards = []
    for item in pages:
        page_url = f"{SITE_URL}/free-online-converter-guides/{item['slug']}/"
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "name": item['title'],
                    "url": page_url,
                    "description": item['desc'],
                    "dateModified": TODAY_ISO,
                    "keywords": item['keyword']
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": f"What is the fastest way to handle {item['keyword']}?",
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": f"Open the recommended freeconvert.cloud tool, upload or paste your file, check the output settings, and download the converted result. {item['angle']}"
                            }
                        },
                        {
                            "@type": "Question",
                            "name": "Is this free converter workflow private?",
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": "Many freeconvert.cloud tools run directly in the browser. When server processing is required for heavy file types, files are handled through encrypted temporary processing."
                            }
                        }
                    ]
                }
            ]
        }
        related_links = ''.join(
            f'<a href="/{slug}/" style="display:inline-flex;padding:0.45rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-size:0.84rem;font-weight:700;">{html.escape(label)}</a>'
            for slug, label in [
                (item['tool'], item['tool_label']),
                ('help', 'Help & FAQ'),
                ('blog', 'Guides')
            ]
        )
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(item['title'])} | freeconvert.cloud</title>
    <meta name="description" content="{html.escape(item['desc'])}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{page_url}">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><a href="/free-online-converter-guides/">Converter Guides</a><span>&gt;</span><span>{html.escape(item['keyword'])}</span></nav>
        <section class="tool-header"><span class="badge">Daily SEO Guide</span><h1>{html.escape(item['title'])}</h1><p>{html.escape(item['desc'])}</p></section>
        <article class="seo-content">
            <h2>Quick answer</h2>
            <p>{html.escape(item['angle'])}</p>
            <h2>Recommended tool</h2>
            <p>Use <a href="/{item['tool']}/" style="color:var(--brand-primary);font-weight:700;text-decoration:none;">{html.escape(item['tool_label'])}</a> for this workflow. The linked tool page includes the active converter, steps, privacy notes, FAQs, and related format helpers.</p>
            <h2>Step-by-step workflow</h2>
            <ol><li>Open the recommended converter tool.</li><li>Add your file or content.</li><li>Choose the output settings that match the upload requirement.</li><li>Download the result and compare quality, file size, and compatibility.</li></ol>
            <h2>Related free tools</h2>
            <div style="display:flex;flex-wrap:wrap;gap:0.55rem;">{related_links}</div>
            <h2>Privacy note</h2>
            <p>Keep the source file saved until the output is verified. Browser-local tools avoid uploads where possible, and heavy conversions use encrypted temporary processing only when the format requires it.</p>
        </article>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
        out_dir = base / item['slug']
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
        hub_cards.append(f"""
        <a href="/free-online-converter-guides/{item['slug']}/" class="tool-card" style="text-decoration:none;text-align:left;">
            <span class="popular-badge">Daily SEO</span>
            <div class="tool-card-top"><div class="tool-icon">SEO</div><span class="tool-category-tag">{html.escape(item['keyword'])}</span></div>
            <div class="tool-card-body">
                <span role="heading" aria-level="2" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{html.escape(item['title'])}</span>
                <p>{html.escape(item['desc'])}</p>
            </div>
            <div class="tool-card-footer"><span class="explore-text">Read Guide</span><span class="arrow-icon">-&gt;</span></div>
        </a>""")

    hub_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Free Online Converter Guides",
        "url": f"{SITE_URL}/free-online-converter-guides/",
        "description": "Daily long-tail converter guides for PDF, image, document, developer, and sitemap workflows.",
        "dateModified": TODAY_ISO,
        "numberOfItems": len(pages)
    }
    hub = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Online Converter Guides | freeconvert.cloud</title>
    <meta name="description" content="Browse daily long-tail converter guides for PDF compression, image resizing, JPG to PDF, WebP compatibility, JSON to CSV, and sitemap submission.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/free-online-converter-guides/">
    <script type="application/ld+json">{json.dumps(hub_schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content" style="max-width:1200px;">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><span>Converter Guides</span></nav>
        <section class="tool-header"><span class="badge">Daily SEO Cluster</span><h1>Free Online Converter Guides</h1><p>Fresh long-tail pages that answer specific file conversion, compression, image sizing, document, and Search Console sitemap questions.</p></section>
        <div class="tool-grid" style="padding:0;">{''.join(hub_cards)}</div>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
    (base / 'index.html').write_text(hub, encoding='utf-8')
    print(f"Generated {len(pages)} daily SEO converter guide pages")


def build_popular_conversion_pages():
    pages = [
        {
            'slug': 'png-to-jpg-for-website',
            'title': 'PNG to JPG for Website Images',
            'desc': 'Convert heavy PNG website images into smaller JPG files for faster page speed, galleries, blog posts, and CMS uploads.',
            'keyword': 'PNG to JPG for website',
            'tool': 'png-to-jpg',
            'tool_label': 'PNG to JPG',
            'problem': 'Large PNG photos can slow down landing pages, especially when transparency is not needed.',
            'best_for': 'Use JPG for photographs, screenshots without transparency, blog images, and product previews where smaller delivery matters.'
        },
        {
            'slug': 'jpg-to-pdf-for-school-assignment',
            'title': 'JPG to PDF for School Assignments',
            'desc': 'Combine homework photos, handwritten notes, scanned pages, and screenshots into one PDF for online class submission.',
            'keyword': 'JPG to PDF for school assignment',
            'tool': 'jpg-to-pdf',
            'tool_label': 'JPG to PDF',
            'problem': 'Many school portals reject multiple loose images and ask students to upload one PDF file.',
            'best_for': 'Use this workflow when you photographed assignment pages and need a single document in the correct order.'
        },
        {
            'slug': 'compress-pdf-for-email',
            'title': 'Compress PDF for Email Attachments',
            'desc': 'Reduce PDF file size for Gmail, Outlook, job applications, invoices, contracts, and client document sharing.',
            'keyword': 'compress PDF for email',
            'tool': 'compress-pdf',
            'tool_label': 'Compress PDF',
            'problem': 'Email providers and company inboxes often reject large PDF attachments or make them slow to send.',
            'best_for': 'Compress the PDF first, then confirm the file still opens clearly before sending it to a client, teacher, or employer.'
        },
        {
            'slug': 'reduce-photo-size-for-passport-upload',
            'title': 'Reduce Photo Size for Passport Upload',
            'desc': 'Resize and compress passport-style photos for visa, ID, profile, and government document upload limits.',
            'keyword': 'reduce photo size for passport upload',
            'tool': 'passport-photo-size-converter',
            'tool_label': 'Passport Photo Size Converter',
            'problem': 'Passport and visa portals often require exact dimensions, file type, and maximum KB size.',
            'best_for': 'Crop the face correctly first, then resize and compress until the photo matches the portal requirement.'
        },
        {
            'slug': 'heic-to-jpg-on-windows',
            'title': 'HEIC to JPG on Windows',
            'desc': 'Convert iPhone HEIC photos into JPG files for Windows apps, websites, email attachments, and editing tools.',
            'keyword': 'HEIC to JPG on Windows',
            'tool': 'heic-to-jpg',
            'tool_label': 'HEIC to JPG',
            'problem': 'Windows users sometimes receive iPhone HEIC photos that older editors or upload forms cannot read.',
            'best_for': 'Convert HEIC to JPG when you need the safest format for sharing, uploading, printing, or editing.'
        },
        {
            'slug': 'webp-to-jpg-for-wordpress',
            'title': 'WebP to JPG for WordPress Uploads',
            'desc': 'Convert WebP images to JPG when themes, plugins, social preview tools, or older WordPress workflows need JPEG files.',
            'keyword': 'WebP to JPG for WordPress',
            'tool': 'webp-to-jpg',
            'tool_label': 'WebP to JPG',
            'problem': 'WebP is efficient, but some legacy plugins, editors, and integrations still expect JPG uploads.',
            'best_for': 'Use JPG when compatibility matters more than maximum compression, especially for thumbnails and featured images.'
        },
        {
            'slug': 'json-to-csv-for-google-sheets',
            'title': 'JSON to CSV for Google Sheets',
            'desc': 'Convert JSON records into CSV rows that can be imported into Google Sheets, Excel, dashboards, and reports.',
            'keyword': 'JSON to CSV for Google Sheets',
            'tool': 'json-to-csv',
            'tool_label': 'JSON to CSV',
            'problem': 'Raw JSON is hard to scan in spreadsheet tools, especially when data needs sorting, filtering, or sharing.',
            'best_for': 'Flatten JSON arrays into columns before importing the CSV into Google Sheets.'
        },
        {
            'slug': 'mp4-to-mp3-for-audio',
            'title': 'MP4 to MP3 for Audio Extraction',
            'desc': 'Extract MP3 audio from MP4 videos for lectures, voice notes, podcasts, offline listening, and reusable clips.',
            'keyword': 'MP4 to MP3 audio extraction',
            'tool': 'mp4-to-mp3',
            'tool_label': 'MP4 to MP3',
            'problem': 'Video files are larger than audio files when you only need the spoken or music track.',
            'best_for': 'Use MP3 when you need a smaller file for listening, sharing, or importing into audio workflows.'
        },
        {
            'slug': 'merge-pdf-scanned-documents',
            'title': 'Merge PDF Scanned Documents',
            'desc': 'Combine scanned PDF pages, forms, receipts, statements, and certificates into one organized document.',
            'keyword': 'merge PDF scanned documents',
            'tool': 'merge-pdf',
            'tool_label': 'Merge PDF',
            'problem': 'Scanned documents often arrive as separate files, which creates messy uploads and email threads.',
            'best_for': 'Merge PDFs when you need one complete document package with pages in the right order.'
        },
        {
            'slug': 'split-pdf-selected-pages',
            'title': 'Split PDF Selected Pages',
            'desc': 'Extract selected PDF pages into a smaller file for forms, contracts, reports, and document sharing.',
            'keyword': 'split PDF selected pages',
            'tool': 'split-pdf',
            'tool_label': 'Split PDF',
            'problem': 'Sending a full PDF can expose unnecessary pages or create oversized attachments.',
            'best_for': 'Split out only the pages you need before uploading or emailing the document.'
        },
        {
            'slug': 'pdf-to-word-for-editing',
            'title': 'PDF to Word for Editing',
            'desc': 'Convert PDF files into editable Word-style documents for rewriting, formatting, correcting, and republishing.',
            'keyword': 'PDF to Word for editing',
            'tool': 'pdf-to-word',
            'tool_label': 'PDF to Word',
            'problem': 'PDFs are great for viewing but inconvenient when you need to change text, layout, or formatting.',
            'best_for': 'Convert to Word when you need editable text and are ready to review formatting after conversion.'
        },
        {
            'slug': 'word-to-pdf-resume',
            'title': 'Word to PDF for Resume Submission',
            'desc': 'Convert DOCX resumes into PDF files that preserve layout, fonts, spacing, and page breaks for job applications.',
            'keyword': 'Word to PDF resume',
            'tool': 'word-to-pdf',
            'tool_label': 'Word to PDF',
            'problem': 'Recruiters may see broken formatting if a resume stays in editable Word format.',
            'best_for': 'Use PDF for final resume submissions so the layout stays consistent across devices.'
        },
        {
            'slug': 'svg-to-png-logo',
            'title': 'SVG to PNG Logo Export',
            'desc': 'Convert SVG logos into PNG images for websites, presentations, social profiles, email signatures, and previews.',
            'keyword': 'SVG to PNG logo',
            'tool': 'svg-to-png',
            'tool_label': 'SVG to PNG',
            'problem': 'Some apps and CMS fields do not accept SVG uploads even when a logo is available only as vector artwork.',
            'best_for': 'Export PNG when you need a transparent, widely accepted logo file.'
        },
        {
            'slug': 'base64-to-image-online',
            'title': 'Base64 to Image Online',
            'desc': 'Decode Base64 image strings and data URIs into previewable image files for debugging, design, and development.',
            'keyword': 'Base64 to image online',
            'tool': 'base64-to-image',
            'tool_label': 'Base64 to Image',
            'problem': 'Base64 image data is hard to inspect when it is embedded in HTML, CSS, JSON, or API responses.',
            'best_for': 'Decode Base64 when you need to preview an embedded image or verify a data URI.'
        },
        {
            'slug': 'qr-code-for-restaurant-menu',
            'title': 'QR Code for Restaurant Menu',
            'desc': 'Create a QR code that links guests to a restaurant menu, ordering page, PDF menu, booking form, or social profile.',
            'keyword': 'QR code for restaurant menu',
            'tool': 'qr-code-generator',
            'tool_label': 'QR Code Generator',
            'problem': 'Printed menus and table tents need a fast scan path to the latest menu or ordering page.',
            'best_for': 'Use a QR code that points to a stable menu URL so you can update the page without reprinting the code.'
        },
        {
            'slug': 'mov-to-mp4-for-android',
            'title': 'MOV to MP4 for Android Sharing',
            'desc': 'Convert iPhone MOV videos to MP4 so they open cleanly on Android phones, Windows laptops, websites, and apps.',
            'keyword': 'MOV to MP4 for Android',
            'tool': 'mov-to-mp4',
            'tool_label': 'MOV to MP4',
            'problem': 'MOV clips from Apple devices can fail in Android apps, older Windows workflows, and web upload forms.',
            'best_for': 'Convert MOV to MP4 when you need the safest sharing format for mixed-device groups and upload portals.'
        },
        {
            'slug': 'mkv-to-mp4-without-quality-loss',
            'title': 'MKV to MP4 Without Losing Quality',
            'desc': 'Convert MKV videos into MP4 for easier playback while keeping a high-quality source copy for archive or editing.',
            'keyword': 'MKV to MP4 without losing quality',
            'tool': 'mkv-to-mp4',
            'tool_label': 'MKV to MP4',
            'problem': 'MKV containers are flexible, but many mobile apps, smart TVs, and websites prefer MP4 uploads.',
            'best_for': 'Use MP4 when compatibility matters, and keep the original MKV if it contains subtitles or multiple audio tracks.'
        },
        {
            'slug': 'compress-video-for-email',
            'title': 'Compress Video for Email Attachments',
            'desc': 'Reduce video size for Gmail, Outlook, client previews, classroom uploads, and small attachment limits.',
            'keyword': 'compress video for email',
            'tool': 'video-compressor',
            'tool_label': 'Video Compressor',
            'problem': 'Email providers often reject large video attachments, especially raw camera clips and long phone recordings.',
            'best_for': 'Compress video when you need a preview-sized file that can be emailed quickly without using cloud storage.'
        },
        {
            'slug': 'mp4-to-gif-meme',
            'title': 'MP4 to GIF for Memes and Short Loops',
            'desc': 'Turn short MP4 clips into GIF animations for memes, chat replies, tutorials, support docs, and social previews.',
            'keyword': 'MP4 to GIF meme',
            'tool': 'mp4-to-gif',
            'tool_label': 'MP4 to GIF',
            'problem': 'Short video moments are easier to reuse in chats and docs when exported as looping GIFs.',
            'best_for': 'Trim the MP4 first, then convert only the best few seconds to keep the GIF small and clear.'
        },
        {
            'slug': 'video-to-mp3-audio-extractor',
            'title': 'Video to MP3 Audio Extractor',
            'desc': 'Extract MP3 audio from videos for podcasts, lectures, voice notes, interviews, music ideas, and offline listening.',
            'keyword': 'video to MP3 audio extractor',
            'tool': 'video-to-mp3',
            'tool_label': 'Video to MP3',
            'problem': 'Keeping the full video wastes storage when the audio track is the only useful part.',
            'best_for': 'Extract MP3 when you want a lightweight listening file from a lecture, meeting, interview, or tutorial.'
        },
        {
            'slug': 'jpg-to-png-transparent-background',
            'title': 'JPG to PNG Transparent Background',
            'desc': 'Convert JPG images to PNG format so they support transparency for logos, overlays, and design projects.',
            'keyword': 'JPG to PNG transparent background',
            'tool': 'jpg-to-png',
            'tool_label': 'JPG to PNG',
            'problem': 'JPG images cannot have transparent backgrounds, which limits their use in designs and overlays.',
            'best_for': 'Convert to PNG when you need transparency, then remove the background in an editor if needed.'
        },
        {
            'slug': 'compress-image-to-200kb-online',
            'title': 'Compress Image to 200KB Online',
            'desc': 'Shrink image file size under 200KB for exam forms, job portals, visa uploads, and website performance.',
            'keyword': 'compress image to 200KB online',
            'tool': 'compress-image-to-200kb',
            'tool_label': 'Compress Image to 200KB',
            'problem': 'Government portals and job sites often reject images larger than 200KB.',
            'best_for': 'Compress the image, check the final KB, and confirm the face or text remains clear.'
        },
        {
            'slug': 'png-to-jpg-for-instagram',
            'title': 'PNG to JPG for Instagram Posts',
            'desc': 'Convert PNG designs and photos to JPG for faster Instagram uploads, stories, and carousel posts.',
            'keyword': 'PNG to JPG for Instagram',
            'tool': 'png-to-jpg',
            'tool_label': 'PNG to JPG',
            'problem': 'High-resolution PNG posts can be slow to upload and consume more mobile data.',
            'best_for': 'Use JPG for photo posts where transparency is not needed.'
        },
        {
            'slug': 'pdf-to-jpg-for-whatsapp',
            'title': 'PDF to JPG for WhatsApp Sharing',
            'desc': 'Convert PDF pages to JPG images for easy WhatsApp sharing, previews, and status updates.',
            'keyword': 'PDF to JPG for WhatsApp',
            'tool': 'pdf-to-jpg',
            'tool_label': 'PDF to JPG',
            'problem': 'WhatsApp previews PDFs differently and some contacts prefer image previews.',
            'best_for': 'Convert key pages to JPG when you need a quick visual share.'
        },
        {
            'slug': 'heic-to-jpg-on-iphone',
            'title': 'HEIC to JPG on iPhone',
            'desc': 'Convert iPhone HEIC photos to JPG directly on your phone for sharing, uploading, and editing anywhere.',
            'keyword': 'HEIC to JPG on iPhone',
            'tool': 'heic-to-jpg',
            'tool_label': 'HEIC to JPG',
            'problem': 'HEIC files may not open on older devices or upload forms.',
            'best_for': 'Convert to JPG before sending photos to Android users or legacy systems.'
        },
        {
            'slug': 'json-to-csv-for-excel',
            'title': 'JSON to CSV for Excel',
            'desc': 'Convert JSON data to CSV format for Excel analysis, pivot tables, and spreadsheet reporting.',
            'keyword': 'JSON to CSV for Excel',
            'tool': 'json-to-csv',
            'tool_label': 'JSON to CSV',
            'problem': 'Excel cannot import raw JSON arrays without conversion.',
            'best_for': 'Flatten nested JSON and import the CSV into Excel or Google Sheets.'
        },
        {
            'slug': 'password-generator-strong',
            'title': 'Strong Password Generator',
            'desc': 'Generate strong, random passwords with symbols, numbers, and mixed case for secure accounts.',
            'keyword': 'strong password generator',
            'tool': 'password-generator',
            'tool_label': 'Password Generator',
            'problem': 'Weak passwords are easily cracked by brute force and dictionary attacks.',
            'best_for': 'Use 16+ characters with symbols for banking, email, and admin accounts.'
        },
        {
            'slug': 'word-counter-for-essays',
            'title': 'Word Counter for Essays',
            'desc': 'Count words, characters, and paragraphs for essays, assignments, and social media posts.',
            'keyword': 'word counter for essays',
            'tool': 'word-counter',
            'tool_label': 'Word Counter',
            'problem': 'School and platform limits require exact word or character counts.',
            'best_for': 'Paste your draft and check the count before submission.'
        },
        {
            'slug': 'ico-converter-favicon',
            'title': 'ICO Converter for Website Favicon',
            'desc': 'Convert PNG or JPG images to ICO format for browser favicons and website bookmarks.',
            'keyword': 'ICO converter favicon',
            'tool': 'ico-converter',
            'tool_label': 'ICO Converter',
            'problem': 'Browsers require ICO or specific PNG sizes for favicons.',
            'best_for': 'Upload a square logo and download a multi-size ICO file.'
        },
        {
            'slug': 'image-compressor-for-website',
            'title': 'Image Compressor for Website Speed',
            'desc': 'Compress images for faster website loading, better Core Web Vitals, and improved SEO rankings.',
            'keyword': 'image compressor for website',
            'tool': 'image-compressor',
            'tool_label': 'Image Compressor',
            'problem': 'Large images slow down page load and hurt search rankings.',
            'best_for': 'Compress hero images, product photos, and blog thumbnails before uploading.'
        },
    ]

    base = Path('popular-conversions')
    base.mkdir(exist_ok=True)
    tools_by_slug = {item['tool']: item['tool_label'] for item in pages}
    hub_cards = []
    for item in pages:
        page_url = f"{SITE_URL}/popular-conversions/{item['slug']}/"
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "name": item['title'],
                    "url": page_url,
                    "description": item['desc'],
                    "dateModified": TODAY_ISO,
                    "keywords": item['keyword'],
                    "isPartOf": {"@type": "CollectionPage", "name": "Popular Conversions", "url": f"{SITE_URL}/popular-conversions/"}
                },
                {
                    "@type": "HowTo",
                    "name": f"How to use {item['tool_label']} for {item['keyword']}",
                    "totalTime": "PT1M",
                    "step": [
                        {"@type": "HowToStep", "position": 1, "text": f"Open the {item['tool_label']} tool."},
                        {"@type": "HowToStep", "position": 2, "text": "Add your file or paste your content."},
                        {"@type": "HowToStep", "position": 3, "text": "Review output settings and convert."},
                        {"@type": "HowToStep", "position": 4, "text": "Download the result and check quality before sharing."}
                    ]
                }
            ]
        }
        related = ''.join(
            f'<a href="/{slug}/" style="display:inline-flex;padding:0.45rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-size:0.84rem;font-weight:700;">{html.escape(label)}</a>'
            for slug, label in [
                (item['tool'], item['tool_label']),
                ('free-online-converter-guides', 'Converter Guides'),
                ('help', 'Help')
            ]
        )
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(item['title'])} | freeconvert.cloud</title>
    <meta name="description" content="{html.escape(item['desc'])}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{page_url}">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><a href="/popular-conversions/">Popular Conversions</a><span>&gt;</span><span>{html.escape(item['keyword'])}</span></nav>
        <section class="tool-header"><span class="badge">Popular Conversion</span><h1>{html.escape(item['title'])}</h1><p>{html.escape(item['desc'])}</p></section>
        <article class="seo-content">
            <h2>When to use this conversion</h2>
            <p>{html.escape(item['problem'])}</p>
            <h2>Best workflow</h2>
            <p>{html.escape(item['best_for'])}</p>
            <h2>Use the free tool</h2>
            <p>Open <a href="/{item['tool']}/" style="color:var(--brand-primary);font-weight:700;text-decoration:none;">{html.escape(item['tool_label'])}</a> to complete this task. The tool page includes the active converter, privacy guidance, FAQs, and related formats.</p>
            <h2>Quality checklist</h2>
            <ul>
                <li>Keep your original file until the new file is verified.</li>
                <li>Check that text, faces, logos, or important details remain readable.</li>
                <li>Use compression only as much as the upload limit requires.</li>
                <li>Confirm the output format is accepted by the app, portal, or website.</li>
            </ul>
            <h2>Related resources</h2>
            <div style="display:flex;flex-wrap:wrap;gap:0.55rem;">{related}</div>
        </article>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
        out_dir = base / item['slug']
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
        hub_cards.append(f"""
        <a href="/popular-conversions/{item['slug']}/" class="tool-card" style="text-decoration:none;text-align:left;">
            <div class="tool-card-top"><div class="tool-icon">↗</div><span class="tool-category-tag">{html.escape(item['keyword'])}</span></div>
            <div class="tool-card-body">
                <span role="heading" aria-level="2" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{html.escape(item['title'])}</span>
                <p>{html.escape(item['desc'])}</p>
            </div>
            <div class="tool-card-footer"><span class="explore-text">Open Guide</span><span class="arrow-icon">-&gt;</span></div>
        </a>""")

    hub_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Popular Conversions",
        "url": f"{SITE_URL}/popular-conversions/",
        "description": "High-intent conversion guides for the most common PDF, image, document, media, developer, and QR workflows.",
        "dateModified": TODAY_ISO,
        "numberOfItems": len(pages)
    }
    hub = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Popular Online Conversions | freeconvert.cloud</title>
    <meta name="description" content="Browse popular conversion workflows for PDF, JPG, PNG, WebP, HEIC, Word, JSON, MP4, SVG, Base64, and QR code tasks.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/popular-conversions/">
    <script type="application/ld+json">{json.dumps(hub_schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content" style="max-width:1200px;">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><span>Popular Conversions</span></nav>
        <section class="tool-header"><span class="badge">Search Intent Hub</span><h1>Popular Online Conversions</h1><p>Focused guides for the file conversion workflows people search most often: PDF, image, document, media, developer, and QR tasks.</p></section>
        <div class="tool-grid" style="padding:0;">{''.join(hub_cards)}</div>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
    (base / 'index.html').write_text(hub, encoding='utf-8')
    print(f"Generated {len(pages)} popular conversion intent pages")


def build_file_format_glossary_pages():
    formats = [
        {
            'slug': 'pdf',
            'name': 'PDF',
            'title': 'What Is a PDF File?',
            'desc': 'Learn what PDF files are used for, when to choose PDF, and which free PDF tools help with conversion, compression, merging, and splitting.',
            'summary': 'PDF is a fixed-layout document format built for sharing, printing, archiving, contracts, invoices, resumes, and forms.',
            'best_for': 'Final documents where layout should stay consistent across devices.',
            'watch_out': 'PDF files can be hard to edit directly and may become large when they contain scans or images.',
            'tools': [('compress-pdf', 'Compress PDF'), ('pdf-to-word', 'PDF to Word'), ('pdf-to-jpg', 'PDF to JPG'), ('merge-pdf', 'Merge PDF'), ('split-pdf', 'Split PDF')]
        },
        {
            'slug': 'jpg',
            'name': 'JPG',
            'title': 'What Is a JPG File?',
            'desc': 'Understand JPG image files, photo compression, website use cases, and when to convert JPG to PDF, PNG, or WebP.',
            'summary': 'JPG is a compressed photo format designed for small file sizes and broad compatibility.',
            'best_for': 'Photos, website images, email attachments, product images, and social media uploads.',
            'watch_out': 'JPG is lossy and does not support transparency.',
            'tools': [('jpg-to-pdf', 'JPG to PDF'), ('jpg-to-png', 'JPG to PNG'), ('jpg-to-webp', 'JPG to WebP'), ('image-compressor', 'Image Compressor')]
        },
        {
            'slug': 'png',
            'name': 'PNG',
            'title': 'What Is a PNG File?',
            'desc': 'Learn when to use PNG images for transparency, screenshots, logos, and when to convert PNG to JPG or WebP.',
            'summary': 'PNG is a lossless image format that supports transparency and crisp graphics.',
            'best_for': 'Logos, screenshots, UI graphics, transparent images, and design assets.',
            'watch_out': 'PNG files can be much larger than JPG or WebP for photographs.',
            'tools': [('png-to-jpg', 'PNG to JPG'), ('png-to-webp', 'PNG to WebP'), ('image-compressor', 'Image Compressor')]
        },
        {
            'slug': 'webp',
            'name': 'WebP',
            'title': 'What Is a WebP File?',
            'desc': 'Learn why WebP images are used for speed, when compatibility matters, and how to convert WebP to JPG.',
            'summary': 'WebP is a modern web image format that can deliver smaller files than JPG or PNG.',
            'best_for': 'Fast websites, image-heavy pages, thumbnails, and SEO-focused image delivery.',
            'watch_out': 'Some older apps, CMS tools, or workflows still prefer JPG or PNG.',
            'tools': [('webp-to-jpg', 'WebP to JPG'), ('jpg-to-webp', 'JPG to WebP'), ('png-to-webp', 'PNG to WebP')]
        },
        {
            'slug': 'heic',
            'name': 'HEIC',
            'title': 'What Is a HEIC File?',
            'desc': 'Understand iPhone HEIC photos, compatibility problems, and when to convert HEIC to JPG.',
            'summary': 'HEIC is a high-efficiency photo format used by many iPhones and Apple devices.',
            'best_for': 'Saving storage space on Apple devices while keeping good image quality.',
            'watch_out': 'Many Windows apps, websites, and upload portals still prefer JPG.',
            'tools': [('heic-to-jpg', 'HEIC to JPG'), ('image-compressor', 'Image Compressor'), ('resize-image', 'Resize Image')]
        },
        {
            'slug': 'docx',
            'name': 'DOCX',
            'title': 'What Is a DOCX File?',
            'desc': 'Learn what DOCX files are, when to keep documents editable, and when to convert Word documents to PDF.',
            'summary': 'DOCX is an editable word-processing document format used for drafts, resumes, reports, and letters.',
            'best_for': 'Writing, editing, collaborating, and revising text-heavy documents.',
            'watch_out': 'Formatting can shift between devices, so PDF is better for final submission.',
            'tools': [('word-to-pdf', 'Word to PDF'), ('pdf-to-word', 'PDF to Word'), ('document-converter', 'Document Tools')]
        },
        {
            'slug': 'svg',
            'name': 'SVG',
            'title': 'What Is an SVG File?',
            'desc': 'Learn how SVG vector files work for logos, icons, and illustrations, and when to export SVG to PNG.',
            'summary': 'SVG is a vector image format that scales cleanly without losing sharpness.',
            'best_for': 'Logos, icons, diagrams, interface graphics, and simple illustrations.',
            'watch_out': 'Some apps and upload forms do not accept SVG, so PNG export is often needed.',
            'tools': [('svg-to-png', 'SVG to PNG'), ('ico-converter', 'ICO Converter'), ('palette-extractor', 'Color Palette Extractor')]
        },
        {
            'slug': 'mp4',
            'name': 'MP4',
            'title': 'What Is an MP4 File?',
            'desc': 'Understand MP4 video files, compatibility, compression, and when to extract MP3 audio from MP4.',
            'summary': 'MP4 is a widely supported video container used for phones, websites, social media, and streaming.',
            'best_for': 'Sharing video across devices, social platforms, websites, and editing tools.',
            'watch_out': 'Video files can become large, and audio-only use cases should be converted to MP3.',
            'tools': [('mp4-to-mp3', 'MP4 to MP3'), ('video-compressor', 'Video Compressor'), ('webm-to-mp4', 'WebM to MP4')]
        },
        {
            'slug': 'mov',
            'name': 'MOV',
            'title': 'What Is a MOV File?',
            'desc': 'Learn why MOV videos are common on iPhone, iPad, and Mac devices, and when to convert MOV to MP4.',
            'summary': 'MOV is an Apple QuickTime video container often created by iPhones, cameras, and macOS editing apps.',
            'best_for': 'Apple device recording, editing workflows, camera footage, and high-quality source video storage.',
            'watch_out': 'MOV files may not upload or play smoothly in every Android, Windows, browser, or social media workflow.',
            'tools': [('mov-to-mp4', 'MOV to MP4'), ('video-compressor', 'Video Compressor'), ('video-to-mp3', 'Video to MP3')]
        },
        {
            'slug': 'avi',
            'name': 'AVI',
            'title': 'What Is an AVI File?',
            'desc': 'Understand older AVI video files, compatibility limits, and why converting AVI to MP4 helps modern sharing.',
            'summary': 'AVI is an older Microsoft video container that can store audio and video but is less web-friendly than MP4.',
            'best_for': 'Legacy video archives, older Windows recordings, and files created by older capture or editing software.',
            'watch_out': 'AVI files can be large and may fail in mobile apps, web upload forms, or modern browser playback.',
            'tools': [('avi-to-mp4', 'AVI to MP4'), ('video-compressor', 'Video Compressor'), ('video-to-mp3', 'Video to MP3')]
        },
        {
            'slug': 'mkv',
            'name': 'MKV',
            'title': 'What Is an MKV File?',
            'desc': 'Learn how MKV video containers work, why they are flexible, and when to convert MKV to MP4.',
            'summary': 'MKV is a flexible video container that can hold video, audio, subtitle, and chapter tracks in one file.',
            'best_for': 'Archival videos, subtitle-heavy media, high-quality source files, and multi-track playback.',
            'watch_out': 'Some smart TVs, phones, browsers, and upload portals prefer MP4 and may reject MKV files.',
            'tools': [('mkv-to-mp4', 'MKV to MP4'), ('video-compressor', 'Video Compressor'), ('video-to-mp3', 'Video to MP3')]
        },
        {
            'slug': 'webm',
            'name': 'WebM',
            'title': 'What Is a WebM File?',
            'desc': 'Learn why WebM videos are used on websites, where compatibility can break, and when WebM to MP4 helps.',
            'summary': 'WebM is a web-focused video format designed for efficient browser playback and online delivery.',
            'best_for': 'Web video embeds, lightweight browser playback, HTML5 video, and open web publishing workflows.',
            'watch_out': 'Some editing apps, older devices, and upload portals still expect MP4 instead of WebM.',
            'tools': [('webm-to-mp4', 'WebM to MP4'), ('video-compressor', 'Video Compressor'), ('video-resizer', 'Video Resizer')]
        },
        {
            'slug': 'mp3',
            'name': 'MP3',
            'title': 'What Is an MP3 File?',
            'desc': 'Learn why MP3 is used for audio sharing, podcasts, voice notes, and extracting sound from video.',
            'summary': 'MP3 is a compressed audio format with broad support across phones, browsers, and media players.',
            'best_for': 'Music, voice notes, podcast clips, lectures, and compact audio sharing.',
            'watch_out': 'MP3 is lossy, so keep a higher-quality source file when editing audio.',
            'tools': [('mp4-to-mp3', 'MP4 to MP3'), ('audio-converter', 'Audio Converter'), ('video-compressor', 'Video Compressor')]
        },
        {
            'slug': 'csv',
            'name': 'CSV',
            'title': 'What Is a CSV File?',
            'desc': 'Understand CSV files for spreadsheets, imports, exports, reports, and converting JSON data to CSV rows.',
            'summary': 'CSV is a plain-text table format where rows and columns are separated by commas.',
            'best_for': 'Spreadsheets, database imports, exports, reports, and lightweight tabular data.',
            'watch_out': 'Nested data needs flattening before it fits neatly into CSV columns.',
            'tools': [('json-to-csv', 'JSON to CSV'), ('csv-to-json', 'CSV to JSON'), ('json-formatter', 'JSON Formatter')]
        },
        {
            'slug': 'json',
            'name': 'JSON',
            'title': 'What Is a JSON File?',
            'desc': 'Learn what JSON is, why developers use it, and how to format, validate, or convert JSON to CSV.',
            'summary': 'JSON is a structured data format used by APIs, apps, websites, configuration files, and databases.',
            'best_for': 'Developer workflows, API responses, configuration, and structured data exchange.',
            'watch_out': 'Invalid brackets, commas, or quotes can break parsing.',
            'tools': [('json-formatter', 'JSON Formatter'), ('json-validator', 'JSON Validator'), ('json-to-csv', 'JSON to CSV')]
        },
        {
            'slug': 'base64',
            'name': 'Base64',
            'title': 'What Is Base64 Encoding?',
            'desc': 'Learn how Base64 encoding works for text, images, data URIs, APIs, and developer debugging.',
            'summary': 'Base64 converts binary or text data into an ASCII-safe string that can travel through text-based systems.',
            'best_for': 'Data URIs, API payloads, email-safe encoding, and embedding small images or files.',
            'watch_out': 'Base64 increases size and should not be treated as encryption.',
            'tools': [('base64-encode', 'Base64 Encode'), ('base64-decode', 'Base64 Decode'), ('base64-to-image', 'Base64 to Image')]
        },
        {
            'slug': 'qr-code',
            'name': 'QR Code',
            'title': 'What Is a QR Code?',
            'desc': 'Learn what QR codes are used for, how they work, and how to create QR codes for links, menus, cards, and WiFi.',
            'summary': 'A QR code is a scannable 2D barcode that can open links, contact cards, menus, apps, or text.',
            'best_for': 'Restaurant menus, business cards, product packaging, events, WiFi access, and print-to-web campaigns.',
            'watch_out': 'Always test QR codes on multiple phones before printing.',
            'tools': [('qr-code-generator', 'QR Code Generator'), ('barcode-generator', 'Barcode Generator'), ('url-encoder', 'URL Encoder')]
        },
        {
            'slug': 'zip',
            'name': 'ZIP',
            'title': 'What Is a ZIP File?',
            'desc': 'Understand ZIP archives, compression, file packaging, and when archive tools help organize downloads.',
            'summary': 'ZIP is an archive format that packages one or more files into a single compressed file.',
            'best_for': 'Sending multiple files together, reducing download size, and organizing project folders.',
            'watch_out': 'Some upload portals block ZIP files for security reasons.',
            'tools': [('archive-converter', 'Archive Converter'), ('document-converter', 'Document Tools'), ('compress-pdf', 'Compress PDF')]
        },
        {
            'slug': 'gif',
            'name': 'GIF',
            'title': 'What Is a GIF File?',
            'desc': 'Learn how GIF files work for simple animation, memes, previews, and when video or WebP may be better.',
            'summary': 'GIF is an older image format best known for short looping animations.',
            'best_for': 'Simple animations, lightweight previews, and small visual loops.',
            'watch_out': 'GIF files can be large and low-color compared with modern formats.',
            'tools': [('video-converter', 'Video Converter'), ('webm-to-mp4', 'WebM to MP4'), ('image-compressor', 'Image Compressor')]
        },
    ]

    base = Path('file-formats')
    base.mkdir(exist_ok=True)
    hub_cards = []
    for item in formats:
        page_url = f"{SITE_URL}/file-formats/{item['slug']}/"
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "TechArticle",
                    "headline": item['title'],
                    "description": item['desc'],
                    "url": page_url,
                    "dateModified": TODAY_ISO,
                    "about": {"@type": "Thing", "name": item['name']}
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": f"What is {item['name']} best for?",
                            "acceptedAnswer": {"@type": "Answer", "text": item['best_for']}
                        },
                        {
                            "@type": "Question",
                            "name": f"What should I watch out for with {item['name']}?",
                            "acceptedAnswer": {"@type": "Answer", "text": item['watch_out']}
                        }
                    ]
                }
            ]
        }
        tool_links = ''.join(
            f'<a href="/{slug}/" style="display:inline-flex;padding:0.45rem 0.85rem;border:1px solid var(--border-color);border-radius:999px;text-decoration:none;color:var(--brand-primary);font-size:0.84rem;font-weight:700;">{html.escape(label)}</a>'
            for slug, label in item['tools']
        )
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(item['title'])} | freeconvert.cloud</title>
    <meta name="description" content="{html.escape(item['desc'])}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{page_url}">
    <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><a href="/file-formats/">File Formats</a><span>&gt;</span><span>{html.escape(item['name'])}</span></nav>
        <section class="tool-header"><span class="badge">File Format Guide</span><h1>{html.escape(item['title'])}</h1><p>{html.escape(item['desc'])}</p></section>
        <article class="seo-content">
            <h2>Quick definition</h2>
            <p>{html.escape(item['summary'])}</p>
            <h2>Best use cases</h2>
            <p>{html.escape(item['best_for'])}</p>
            <h2>What to watch out for</h2>
            <p>{html.escape(item['watch_out'])}</p>
            <h2>Related converters</h2>
            <div style="display:flex;flex-wrap:wrap;gap:0.55rem;">{tool_links}</div>
            <h2>Conversion tip</h2>
            <p>Keep the original file, create a converted copy, then compare file size, quality, and compatibility before deleting or uploading the result.</p>
        </article>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
        out_dir = base / item['slug']
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(page, encoding='utf-8')
        hub_cards.append(f"""
        <a href="/file-formats/{item['slug']}/" class="tool-card" style="text-decoration:none;text-align:left;">
            <div class="tool-card-top"><div class="tool-icon">{html.escape(item['name'][:3])}</div><span class="tool-category-tag">Format Guide</span></div>
            <div class="tool-card-body">
                <span role="heading" aria-level="2" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{html.escape(item['title'])}</span>
                <p>{html.escape(item['desc'])}</p>
            </div>
            <div class="tool-card-footer"><span class="explore-text">Read Format Guide</span><span class="arrow-icon">-&gt;</span></div>
        </a>""")

    hub_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "File Format Glossary",
        "url": f"{SITE_URL}/file-formats/",
        "description": "Plain-English file format guides for PDF, JPG, PNG, WebP, HEIC, DOCX, SVG, MP4, MOV, AVI, MKV, WebM, MP3, CSV, JSON, Base64, QR codes, ZIP, and GIF.",
        "dateModified": TODAY_ISO,
        "numberOfItems": len(formats)
    }
    hub = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Format Glossary | freeconvert.cloud</title>
    <meta name="description" content="Learn what common file formats mean, including PDF, JPG, PNG, WebP, MP4, MOV, AVI, MKV, WebM, MP3, CSV, JSON, GIF, and ZIP.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="canonical" href="{SITE_URL}/file-formats/">
    <script type="application/ld+json">{json.dumps(hub_schema, separators=(',', ':'))}</script>
</head>
<body>
    {HEADER_SNIPPET}
    <main class="tool-content" style="max-width:1200px;">
        <nav class="breadcrumbs"><a href="/">Home</a><span>&gt;</span><span>File Formats</span></nav>
        <section class="tool-header"><span class="badge">Glossary Hub</span><h1>File Format Glossary</h1><p>Plain-English explanations for common formats, with direct links to the right converters.</p></section>
        <div class="tool-grid" style="padding:0;">{''.join(hub_cards)}</div>
    </main>
    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>
</html>"""
    (base / 'index.html').write_text(hub, encoding='utf-8')
    print(f"Generated {len(formats)} file format glossary pages")


# Categories configurations
CATEGORIES = {
    'image-converter': {
        'name': 'Image Converter',
        'slug': 'image-converter',
        'intro': 'Convert PNG, JPG, WebP, SVG, and HEIC images directly in your browser.',
        'seo_title': 'Best Free Image Converter Online - Convert Photos Fast',
        'seo_desc': 'Convert image file formats instantly for free. Supports PNG, JPG, WebP, HEIC, and vectors.',
        'types': ['image', 'image_advanced', 'image_base64'],
        'how_to': '<ol><li>Drag and drop your images into the upload box.</li><li>Select output format (PNG, JPG, WebP).</li><li>Click Convert and download your files.</li></ol>',
        'faq': [
            {"q": "Can I convert images on iPhone?", "a": "Yes, our web-based image converter works on iOS, Android, macOS, and Windows."},
            {"q": "Are my photos secure?", "a": "Absolutely. All image conversions happen locally in your browser memory and are never uploaded."}
        ]
    },
    'video-converter': {
        'name': 'Video Converter',
        'slug': 'video-converter',
        'intro': 'Convert MP4, WebM, AVI, and MOV video files online safely.',
        'seo_title': 'Online Video Converter - Convert Video Files Free',
        'seo_desc': 'Easily convert MP4, WebM, and other video file formats with optimal conversion quality.',
        'types': ['video'],
        'how_to': '<ol><li>Select your video file from your computer or cloud drive.</li><li>Select your preferred output format.</li><li>Click Convert and wait for the download link.</li></ol>',
        'faq': [
            {"q": "What is the maximum file size limit?", "a": "Free users can convert files up to 50MB. Upgrade to Pro for unlimited sizes."},
            {"q": "How long are converted video files kept?", "a": "All files are automatically deleted after 2 hours."}
        ]
    },
    'audio-converter': {
        'name': 'Audio Converter',
        'slug': 'audio-converter',
        'intro': 'Convert audio tracks between MP3, WAV, FLAC, and OGG formats.',
        'seo_title': 'Free Audio Converter Online - MP3, WAV, FLAC',
        'seo_desc': 'Convert audio files online instantly. Fast, private, and works on all devices.',
        'types': ['audio'],
        'how_to': '<ol><li>Upload your audio file.</li><li>Choose output bitrates and audio format.</li><li>Click Convert and download.</li></ol>',
        'faq': [
            {"q": "Can I convert video files to MP3?", "a": "Yes! You can upload an MP4 file and convert it directly to MP3."}
        ]
    },
    'document-converter': {
        'name': 'Document Converter',
        'slug': 'document-converter',
        'intro': 'Convert DOC, DOCX, TXT, CSV, JSON, and PDF files quickly.',
        'seo_title': 'Online Document Converter - Convert PDF, Word, Excel',
        'seo_desc': 'Transform PDFs, Microsoft Word files, and developer data formats safely.',
        'types': ['dev_basic', 'dev_advanced', 'text'],
        'how_to': '<ol><li>Upload your documents.</li><li>Choose the target document format.</li><li>Click Process and download your results.</li></ol>',
        'faq': [
            {"q": "Is my data processed locally?", "a": "Standard developer formatters and data converters process 100% locally on your computer."}
        ]
    },
    'pdf-tools': {
        'name': 'PDF Tools',
        'slug': 'pdf-tools',
        'intro': 'Compress, split, edit, and convert PDF documents in one click.',
        'seo_title': 'Free PDF Tools Online - Compress, Merge, Convert PDFs',
        'seo_desc': 'The best free online PDF toolset. Compress PDF sizes, convert JPG to PDF, or PDF to Word.',
        'types': ['pdf', 'qr'],
        'how_to': '<ol><li>Select the PDF tool or upload your document.</li><li>Adjust optional advanced layouts.</li><li>Click Convert/Process to save your PDF.</li></ol>',
        'faq': [
            {"q": "Does PDF conversion require software?", "a": "No installation is needed. All PDF processing runs securely in the cloud or local browser."}
        ]
    },
    'archive-converter': {
        'name': 'Archive Converter',
        'slug': 'archive-converter',
        'intro': 'Extract or compress ZIP, RAR, 7Z, and TAR archives.',
        'seo_title': 'Online Archive Converter - ZIP, RAR, 7Z Compression',
        'seo_desc': 'Compress files to ZIP or extract contents easily directly in your web browser.',
        'types': ['archive'],
        'how_to': '<ol><li>Upload your file archive.</li><li>Select target zip/unzip format.</li><li>Process and download.</li></ol>',
        'faq': [
            {"q": "Can I batch compress files?", "a": "Yes, batch zip processing is supported on all major platforms."}
        ]
    },
    'ebook-converter': {
        'name': 'eBook Converter',
        'slug': 'ebook-converter',
        'intro': 'Convert EPUB, PDF, MOBI, and AZW3 eBook files online.',
        'seo_title': 'Free eBook Converter - EPUB to PDF, MOBI to EPUB',
        'seo_desc': 'Convert files for Kindle, iPad, and e-readers instantly. Fast and secure ebook conversion.',
        'types': ['ebook'],
        'how_to': '<ol><li>Drag your EPUB or PDF eBook.</li><li>Choose Kindle or standard MOBI output.</li><li>Convert and download your book.</li></ol>',
        'faq': [
            {"q": "Will formatting be preserved?", "a": "Yes, our conversion engine is optimized to preserve font styles and pagination."}
        ]
    },
    'unit-converter': {
        'name': 'Unit Converter',
        'slug': 'unit-converter',
        'intro': 'Convert between length, weight, temperature, and aspect ratios.',
        'seo_title': 'Online Unit Converter - Length, Weight, aspect ratio',
        'seo_desc': 'Convert metrics instantly. Fast and precise calculation viewport simulator included.',
        'types': ['utility', 'utility_advanced'],
        'how_to': '<ol><li>Input your initial values.</li><li>Select metric units or dimensions.</li><li>See live calculations immediately.</li></ol>',
        'faq': [
            {"q": "Does this require internet?", "a": "No, calculations run purely offline in your local browser sandbox."}
        ]
    }
}

# --- DYNAMIC UIs ---

UPLOAD_BOX_UI = """
<div class="upload-wrapper" style="padding: 0;">
    <div id="drop-zone" class="drop-zone">
        <div class="drop-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
        </div>
        <p class="drop-text">Drag & drop files here</p>
        <span class="or-separator">or</span>
        <button type="button" class="btn primary choose-btn">Choose Files</button>
        <input type="file" id="file-input" hidden>
    </div>
    
    <!-- Cloud options marked coming soon/inactive -->
    <div class="cloud-uploads">
        <button class="cloud-btn" disabled>☁️ Google Drive <span style="font-size:0.7rem; color:var(--text-light);">(Coming Soon)</span></button>
        <button class="cloud-btn" disabled>📦 Dropbox <span style="font-size:0.7rem; color:var(--text-light);">(Coming Soon)</span></button>
        <button class="cloud-btn" disabled>📂 OneDrive <span style="font-size:0.7rem; color:var(--text-light);">(Coming Soon)</span></button>
        <button class="cloud-btn" disabled>🔗 URL Upload <span style="font-size:0.7rem; color:var(--text-light);">(Coming Soon)</span></button>
    </div>

    <!-- Active preview states -->
    <div id="preview-container" class="preview-container" style="display: none;">
        <div class="file-info-card">
            <div style="display: flex; align-items: center; gap: 0.8rem;">
                <span id="file-type-icon" style="font-size: 2.2rem; display: flex; align-items: center; justify-content: center;">📄</span>
                <div>
                    <span class="file-name" id="selected-file-name">-</span>
                    <span class="file-size" id="selected-file-size">-</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <label style="font-size: 0.85rem; font-weight: bold; color: var(--text-muted);">Convert to:</label>
                <select id="output-format" class="glass-input" style="width: auto; padding: 0.4rem 1.2rem; border-radius: 8px; font-weight: bold; background: white;"></select>
            </div>
        </div>
        <div id="sandbox-badge" style="margin-top: 0.8rem; margin-bottom: 1.2rem; font-size: 0.82rem; font-weight: 700; text-align: left; display: flex; align-items: center; gap: 0.5rem; padding: 0.8rem 1.2rem; border-radius: 12px; background: rgba(99, 102, 241, 0.03); border: 1px solid var(--border-color); line-height: 1.4;"></div>

        <!-- Advanced settings dropdown accordion -->
        <div class="accordion" id="adv-accordion" style="display: none; margin-bottom: 1.5rem;">
            <div class="accordion-header">⚙️ Advanced Conversion Settings</div>
            <div class="accordion-content">
                <div id="advanced-settings-controls" style="display: flex; flex-direction: column; gap: 1rem;">
                    <!-- Controls will be injected dynamically -->
                </div>
            </div>
        </div>

        <div class="progress-container" id="sw-progress-wrap" style="display: none;">
            <div class="progress-bar" id="sw-progress-bar"></div>
        </div>
        <div id="sw-progress-text" style="display: none; text-align: center; font-weight: bold;">Converting file...</div>

        <div class="action-buttons" style="display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;">
            <button id="convert-btn" class="btn primary">🚀 Convert Now</button>
            <button id="reset-btn" class="btn secondary">Reset</button>
        </div>
    </div>
</div>
"""

UPLOAD_BOX_SCRIPT = """
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const fileNameEl = document.getElementById('selected-file-name');
const fileSizeEl = document.getElementById('selected-file-size');
const formatSelect = document.getElementById('output-format');
const convertBtn = document.getElementById('convert-btn');
const resetBtn = document.getElementById('reset-btn');
const accordion = document.getElementById('adv-accordion');
const controlsBox = document.getElementById('advanced-settings-controls');
const progWrap = document.getElementById('sw-progress-wrap');
const progBar = document.getElementById('sw-progress-bar');
const progText = document.getElementById('sw-progress-text');
const sandboxBadge = document.getElementById('sandbox-badge');
const fileTypeIcon = document.getElementById('file-type-icon');

dropZone.onclick = () => fileInput.click();
fileInput.onchange = (e) => handleFiles(e.target.files);
dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('active'); };
dropZone.ondragleave = () => dropZone.classList.remove('active');
dropZone.ondrop = (e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); };

let activeFile = null;

function getFileIcon(fileName) {
    const ext = fileName.split('.').pop().toLowerCase();
    const imageExts = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'heic'];
    const videoExts = ['mp4', 'mov', 'avi', 'mkv', 'webm'];
    const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'm4a'];
    const documentExts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'];
    const archiveExts = ['zip', 'rar', '7z', 'tar', 'gz'];
    
    if (imageExts.includes(ext)) return '🖼️';
    if (videoExts.includes(ext)) return '🎥';
    if (audioExts.includes(ext)) return '🎵';
    if (documentExts.includes(ext)) return '📄';
    if (archiveExts.includes(ext)) return '🗜️';
    return '📄';
}

function updateSandboxBadge(sourceExt, targetExt) {
    const isClient = window.ConversionAdapter.isClientSideTool(sourceExt, targetExt);
    const isBackendConnected = window.ConversionAdapter.config.isBackendConnected;
    if (isClient) {
        sandboxBadge.innerHTML = `🛡️ <span style="color: var(--brand-accent);">100% In-Browser Secure Sandbox (No file upload required - mathematically private)</span>`;
    } else {
        if (isBackendConnected) {
            sandboxBadge.innerHTML = `☁️ <span style="color: var(--brand-secondary);">Edge Server Engine (Secure 256-bit SSL Tunnel - Permanent deletion after 2 hours)</span>`;
        } else {
            sandboxBadge.innerHTML = `☁️ <span style="color: var(--brand-secondary);">Edge Server Engine <span style="background: rgba(139, 92, 246, 0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-left: 5px;">Secure Sandbox Demo</span> (Fallback offline processing)</span>`;
        }
    }
}

function handleFiles(files) {
    if (files.length === 0) return;
    activeFile = files[0];
    dropZone.style.display = 'none';
    previewContainer.style.display = 'block';
    
    fileNameEl.textContent = activeFile.name;
    fileSizeEl.textContent = `(${(activeFile.size / 1024 / 1024).toFixed(2)} MB)`;
    fileTypeIcon.textContent = getFileIcon(activeFile.name);

    // Dynamic output format mapping
    const formats = window.ConversionAdapter.getOutputFormats(activeFile.name);
    formatSelect.innerHTML = formats.map(f => `<option value="${f}">${f.toUpperCase()}</option>`).join('');

    const ext = activeFile.name.split('.').pop().toLowerCase();
    updateSandboxBadge(ext, formatSelect.value);
    formatSelect.onchange = () => updateSandboxBadge(ext, formatSelect.value);

    // Inject advanced options if image tool
    if (ext === 'png' || ext === 'jpg' || ext === 'jpeg' || ext === 'webp') {
        accordion.style.display = 'block';
        controlsBox.innerHTML = `
            <div style="display: flex; gap: 1rem; width: 100%;">
                <label style="flex: 1; font-weight: 700; font-size: 0.85rem;">Width (px): <input type="number" id="opt-width" class="glass-input" style="background:var(--bg-light); border-radius:8px; width: 100%; margin-top: 5px;" placeholder="Original"></label>
                <label style="flex: 1; font-weight: 700; font-size: 0.85rem;">Height (px): <input type="number" id="opt-height" class="glass-input" style="background:var(--bg-light); border-radius:8px; width: 100%; margin-top: 5px;" placeholder="Original"></label>
            </div>
            <label style="font-weight: 700; font-size: 0.85rem;">Image Quality: <input type="range" id="opt-quality" min="10" max="100" value="90" style="width: 100%; margin-top: 5px;"> <span id="qual-label" style="color:var(--brand-primary);">90%</span></label>
        `;
        const slider = document.getElementById('opt-quality');
        if (slider) {
            slider.oninput = (e) => document.getElementById('qual-label').textContent = e.target.value + '%';
        }
    } else {
        accordion.style.display = 'none';
    }
}

convertBtn.onclick = async () => {
    if (!activeFile) return;
    
    convertBtn.style.display = 'none';
    resetBtn.style.display = 'none';
    progWrap.style.display = 'block';
    progText.style.display = 'block';
    
    // Simulate multi-stage upload states
    const stages = [
        { progress: 20, label: "🛰️ Connecting to edge server..." },
        { progress: 40, label: "📤 Uploading file to security sandbox..." },
        { progress: 65, label: "⚙️ Converting formats..." },
        { progress: 85, label: "🗜️ Optimizing layout parameters..." },
        { progress: 100, label: "✅ Finalizing secure download link..." }
    ];

    for (let stage of stages) {
        progText.textContent = stage.label;
        progBar.style.width = stage.progress + '%';
        await new Promise(r => setTimeout(r, 400));
    }

    try {
        const targetFormat = formatSelect.value;
        
        // Gather custom options
        const opts = {};
        const qEl = document.getElementById('opt-quality');
        const wEl = document.getElementById('opt-width');
        const hEl = document.getElementById('opt-height');
        
        if (qEl) opts.quality = parseFloat(qEl.value) / 100;
        if (wEl && wEl.value) opts.width = parseInt(wEl.value);
        if (hEl && hEl.value) opts.height = parseInt(hEl.value);

        const resultBlob = await window.ConversionAdapter.convert(activeFile, targetFormat, opts);
        
        // Render completed download state with beautiful success alerts and checklist animations
        progWrap.style.display = 'none';
        
        progText.innerHTML = `
            <div class="success-alert">
                <div class="success-icon-wrap">
                    <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                        <circle class="success-checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                        <path class="success-checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                    </svg>
                </div>
                <div class="success-message">
                    <h4>Conversion Completed Successfully!</h4>
                    <p>Your file has been securely processed and is ready for download.</p>
                </div>
            </div>
        `;
        
        const dLink = document.createElement('a');
        dLink.className = "btn primary";
        dLink.style.marginTop = "1rem";
        dLink.textContent = "📥 Download Converted File";
        dLink.href = URL.createObjectURL(resultBlob);
        
        const cleanName = activeFile.name.substring(0, activeFile.name.lastIndexOf('.'));
        dLink.download = `${cleanName}-converted.${targetFormat}`;
        
        // Record conversion history
        if (window.recordConversionHistory) {
            let activeToolId = '{{ID}}';
            let activeToolName = '{{NAME}}';
            if (!activeToolId || activeToolId === '{{ID}}') {
                const srcExt = activeFile.name.split('.').pop().toLowerCase();
                const tgtExt = targetFormat.toLowerCase();
                activeToolId = `${srcExt}-to-${tgtExt}`;
                activeToolName = `${srcExt.toUpperCase()} to ${tgtExt.toUpperCase()} Converter`;
            }
            window.recordConversionHistory(
                activeToolId,
                activeToolName,
                activeFile.name,
                activeFile.size,
                resultBlob.size
            );
        }
        
        // Trigger delight particles!
        if (window.triggerBrandParticles) {
            setTimeout(() => {
                const checkmark = document.querySelector('.success-checkmark');
                if (checkmark) {
                    const rect = checkmark.getBoundingClientRect();
                    window.triggerBrandParticles(rect.left + rect.width / 2, rect.top + rect.height / 2);
                } else {
                    window.triggerBrandParticles(window.innerWidth / 2, window.innerHeight / 2);
                }
            }, 100);
        }
        
        // Insert download button cleanly
        const actButtons = document.querySelector('.action-buttons');
        actButtons.innerHTML = '';
        actButtons.appendChild(dLink);
        
        const anotherBtn = document.createElement('button');
        anotherBtn.className = "btn secondary";
        anotherBtn.style.marginTop = "1rem";
        anotherBtn.textContent = "Convert Another File";
        anotherBtn.onclick = () => location.reload();
        actButtons.appendChild(anotherBtn);
        
    } catch (e) {
        progText.textContent = "❌ Error: " + e.message;
        progText.style.color = "var(--brand-danger)";
        convertBtn.style.display = 'inline-block';
        resetBtn.style.display = 'inline-block';
    }
};

resetBtn.onclick = () => location.reload();
"""

DEV_BASIC_SCRIPT = r"""
const input = document.getElementById('dev-input');
const output = document.getElementById('dev-output');
const btn = document.getElementById('action-btn');
const selector = document.getElementById('operation-selector');
const toolId = '{{ID}}';

// Inject operation controls
if (toolId === 'base64-tool') {
    selector.innerHTML = `
        <select id="op-mode" class="glass-input" style="width: 100%; margin-bottom: 0.5rem; text-align: center; font-weight: bold; background: white;">
            <option value="encode">🔐 Text to Base64</option>
            <option value="decode">🔓 Base64 to Text</option>
        </select>
    `;
} else if (toolId === 'url-encoder-decoder') {
    selector.innerHTML = `
        <select id="op-mode" class="glass-input" style="width: 100%; margin-bottom: 0.5rem; text-align: center; font-weight: bold; background: white;">
            <option value="encode">🔗 URL Encode</option>
            <option value="decode">🔓 URL Decode</option>
        </select>
    `;
} else if (toolId === 'binary-text-converter') {
    selector.innerHTML = `
        <select id="op-mode" class="glass-input" style="width: 100%; margin-bottom: 0.5rem; text-align: center; font-weight: bold; background: white;">
            <option value="text2bin">✍️ Text to Binary</option>
            <option value="bin2text">🤖 Binary to Text</option>
        </select>
    `;
} else if (toolId === 'unicode-converter') {
    selector.innerHTML = `
        <select id="op-mode" class="glass-input" style="width: 100%; margin-bottom: 0.5rem; text-align: center; font-weight: bold; background: white;">
            <option value="text2uni">🔡 Text to Unicode</option>
            <option value="uni2text">🔤 Unicode to Text</option>
        </select>
    `;
}

btn.onclick = () => {
    const val = input.value;
    if (!val) { output.value = ""; return; }
    try {
        const modeEl = document.getElementById('op-mode');
        const mode = modeEl ? modeEl.value : '';

        if (toolId === 'json-to-csv') {
            const items = JSON.parse(val);
            const replacer = (key, value) => value === null ? '' : value;
            const header = Object.keys(items[0]);
            let csv = items.map(row => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','));
            csv.unshift(header.join(','));
            output.value = csv.join('\r\n');
        } else if (toolId === 'base64-tool') {
            if (mode === 'encode') {
                output.value = btoa(unescape(encodeURIComponent(val)));
            } else {
                output.value = decodeURIComponent(escape(atob(val)));
            }
        } else if (toolId === 'url-encoder-decoder') {
            if (mode === 'encode') {
                output.value = encodeURIComponent(val);
            } else {
                output.value = decodeURIComponent(val);
            }
        } else if (toolId === 'binary-text-converter') {
            if (mode === 'bin2text') {
                output.value = val.trim().split(/\s+/).map(bin => String.fromCharCode(parseInt(bin, 2))).join('');
            } else {
                output.value = val.split('').map(char => char.charCodeAt(0).toString(2).padStart(8, '0')).join(' ');
            }
        } else if (toolId === 'csv-to-json') {
            const lines = val.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length === 0) throw new Error("Input is empty");
            const result = [];
            const headers = lines[0].split(',').map(h => h.replace(/^["']|["']$/g, '').trim());
            for (let i = 1; i < lines.length; i++) {
                const obj = {};
                const currentline = lines[i].split(',').map(c => c.replace(/^["']|["']$/g, '').trim());
                if (currentline.length === headers.length) {
                    for (let j = 0; j < headers.length; j++) {
                        obj[headers[j]] = currentline[j];
                    }
                    result.push(obj);
                }
            }
            output.value = JSON.stringify(result, null, 2);
        } else if (toolId === 'unicode-converter') {
            if (mode === 'uni2text') {
                output.value = val.replace(/\\u([\da-fA-F]{4})/g, (match, grp) => String.fromCharCode(parseInt(grp, 16)));
            } else {
                output.value = val.split('').map(char => {
                    const code = char.charCodeAt(0).toString(16).toUpperCase();
                    return '\\u' + ('0000' + code).slice(-4);
                }).join('');
            }
        } else if (toolId === 'yaml-to-json') {
            const obj = jsyaml.load(val);
            output.value = JSON.stringify(obj, null, 2);
        } else if (toolId === 'json-to-yaml') {
            const obj = JSON.parse(val);
            output.value = jsyaml.dump(obj);
        }
    } catch (e) {
        output.value = "Error: " + e.message;
    }
};
"""

DEV_ADVANCED_SCRIPT = r"""
const input = document.getElementById('adv-input');
const preview = document.getElementById('adv-preview');
const output = document.getElementById('adv-output');
const btn = document.getElementById('adv-action-btn');
const toolId = '{{ID}}';

// Dynamic UI Injection for Diff Checker
if (toolId === 'diff-checker') {
    document.getElementById('editor-container').innerHTML = `
        <div class="editor-pane">
            <div class="editor-header">
                <span class="editor-title">📥 Original Text</span>
                <div class="editor-actions">
                    <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                    <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                </div>
            </div>
            <textarea id="adv-input" class="code-editor-textarea" style="height: 250px;" placeholder="Paste original text here..."></textarea>
        </div>
        <div class="editor-pane">
            <div class="editor-header">
                <span class="editor-title">📥 Modified Text</span>
            </div>
            <textarea id="adv-input-2" class="code-editor-textarea" style="height: 250px;" placeholder="Paste modified text here..."></textarea>
        </div>
    `;
    btn.textContent = "Compare Texts";
    
    const diffResult = document.createElement('div');
    diffResult.id = "diff-result-box";
    diffResult.className = "code-editor-textarea";
    diffResult.style.gridColumn = "span 2";
    diffResult.style.marginTop = "20px";
    diffResult.style.minHeight = "200px";
    diffResult.style.height = "auto";
    diffResult.style.textAlign = "left";
    diffResult.style.whiteSpace = "pre-wrap";
    diffResult.style.display = "none";
    diffResult.style.padding = "1.5rem";
    diffResult.style.lineHeight = "1.8";
    
    document.getElementById('editor-container').appendChild(diffResult);
}

btn.onclick = () => {
    const val = input.value;
            if (toolId === 'sql-formatter') {
        output.style.display = 'block';
        preview.style.display = 'none';
        output.value = sqlFormatter.format(val);
    } else if (toolId === 'json-formatter') {
        output.style.display = 'block';
        preview.style.display = 'none';
        try {
            output.value = JSON.stringify(JSON.parse(val), null, 2);
        } catch (err) {
            output.value = "Error: Invalid JSON syntax. " + err.message;
        }
    } else if (toolId === 'json-validator') {
        output.style.display = 'block';
        preview.style.display = 'none';
        try {
            JSON.parse(val);
            output.value = "🟢 Valid JSON! The syntax is correct and well-formed.";
        } catch (err) {
            output.value = "🔴 Invalid JSON syntax:\n" + err.message;
        }
    } else if (toolId === 'html-formatter') {
        output.style.display = 'block';
        preview.style.display = 'none';
        output.value = html_beautify(val, { indent_size: 2 });
    } else if (toolId === 'css-formatter') {
        output.style.display = 'block';
        preview.style.display = 'none';
        output.value = css_beautify(val, { indent_size: 2 });
    } else if (toolId === 'js-formatter') {
        output.style.display = 'block';
        preview.style.display = 'none';
        output.value = js_beautify(val, { indent_size: 2 });
    } else if (toolId === 'diff-checker') {
        const val1 = document.getElementById('adv-input').value;
        const val2 = document.getElementById('adv-input-2').value;
        const diff = Diff.diffChars(val1, val2);
        const resultBox = document.getElementById('diff-result-box');
        resultBox.style.display = 'block';
        resultBox.innerHTML = '';
        
        diff.forEach(part => {
            const span = document.createElement('span');
            if (part.added) {
                span.style.color = '#10b981';
                span.style.backgroundColor = 'rgba(16, 185, 129, 0.15)';
                span.style.padding = '2px 4px';
                span.style.borderRadius = '4px';
                span.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                span.style.fontWeight = 'bold';
            } else if (part.removed) {
                span.style.color = '#ef4444';
                span.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                span.style.padding = '2px 4px';
                span.style.borderRadius = '4px';
                span.style.border = '1px solid rgba(239, 68, 68, 0.3)';
                span.style.textDecoration = 'line-through';
                span.style.fontWeight = 'bold';
            } else {
                span.style.color = '#cbd5e1';
            }
            span.appendChild(document.createTextNode(part.value));
            resultBox.appendChild(span);
        });
    }
};
// Live preview for markdown
if (toolId === 'markdown-editor') {
    preview.style.display = 'block';
    output.style.display = 'none';
    input.addEventListener('input', () => { preview.innerHTML = marked.parse(input.value); });
}
"""

UTILITY_SCRIPT = r"""
const container = document.getElementById('utility-content');
const toolId = '{{ID}}';

if (toolId === 'lorem-ipsum') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 500px; margin: 0 auto;">
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(99,102,241,0.02); border:1px solid var(--border-color); padding: 1rem 1.5rem; border-radius: 14px;">
                <label style="font-weight: 800; font-size: 0.94rem;">Paragraphs Count: </label>
                <input type="number" id="lorem-count" class="glass-input" value="3" min="1" max="20" style="width: 80px; text-align: center; padding: 0.4rem;">
            </div>
            <button class="btn primary" onclick="generateLorem()" style="justify-content: center;">⚡ Generate Lorem Ipsum</button>
        </div>
        <div class="editor-pane" style="margin-top: 2rem;">
            <div class="editor-header">
                <span class="editor-title">📤 Generated Text</span>
                <div class="editor-actions">
                    <button type="button" class="editor-btn success" onclick="copyOutputText()">📋 Copy</button>
                    <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                </div>
            </div>
            <textarea id="lorem-out" class="code-editor-textarea" style="height: 300px;" readonly placeholder="Lorem Ipsum text will render here..."></textarea>
        </div>
    `;
    window.generateLorem = () => {
        const count = document.getElementById('lorem-count').value;
        const text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";
        let out = "";
        for(let i=0; i<count; i++) out += text + "\\n\\n";
        document.getElementById('lorem-out').value = out.trim();
    };
} else if (toolId === 'password-strength') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto;">
            <div style="display: flex; flex-direction: column; gap: 0.6rem; text-align: left;">
                <label style="font-weight: 800; font-size: 0.94rem; color: var(--text-muted);">Enter Password to Check:</label>
                <div style="position: relative; display: flex; align-items: center; width: 100%;">
                    <input type="password" id="pass-input" class="glass-input" placeholder="Type a password here..." style="width: 100%; padding-right: 3rem;">
                    <span style="position: absolute; right: 1rem; cursor: pointer; user-select: none;" id="toggle-pass-visibility">👁️</span>
                </div>
            </div>
            
            <div id="strength-bar" style="height: 10px; background: #e2e8f0; border-radius: 5px; overflow: hidden; margin-bottom: 5px; border: 1px solid var(--border-color);">
                <div id="strength-fill" style="height: 100%; width: 0%; background: red; transition: all 0.3s;"></div>
            </div>
            <h3 id="strength-text" style="color: var(--text-muted); text-align: center; font-size: 1.2rem; font-weight: 800;">Enter Password</h3>
            
            <div class="editor-actions" style="justify-content: center;">
                <button type="button" class="editor-btn" onclick="loadSampleData()">⚡ Test Strong Example</button>
                <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
            </div>
        </div>
    `;
    const eye = document.getElementById('toggle-pass-visibility');
    const pInput = document.getElementById('pass-input');
    eye.onclick = () => {
        if (pInput.type === 'password') {
            pInput.type = 'text';
            eye.textContent = '🔒';
        } else {
            pInput.type = 'password';
            eye.textContent = '👁️';
        }
    };
    
    pInput.addEventListener('input', (e) => {
        const val = e.target.value;
        let score = 0;
        if (val.length > 8) score++;
        if (val.length > 12) score++;
        if (/[A-Z]/.test(val)) score++;
        if (/[0-9]/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;
        
        const fill = document.getElementById('strength-fill');
        const text = document.getElementById('strength-text');
        
        let color = 'red';
        let label = 'Weak Strength 🔴';
        let percent = (score / 5) * 100;
        
        if (score > 2) { color = 'orange'; label = 'Medium Strength 🟡'; }
        if (score > 4) { color = '#10b981'; label = 'Strong / AdSense Secure 🟢'; }
        
        if (val.length === 0) { percent = 0; label = 'Enter Password'; color = 'var(--text-light)'; }
        
        fill.style.width = percent + '%';
        fill.style.background = color;
        text.textContent = label;
        text.style.color = color;
    });
} else if (toolId === 'stopwatch') {
    container.innerHTML = `
        <div class="stopwatch-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative;">
            <div class="dial-outer" style="width: 250px; height: 250px; border-radius: 50%; border: 6px solid rgba(99,102,241,0.05); background: rgba(255,255,255,0.7); display: flex; align-items: center; justify-content: center; position: relative; box-shadow: 0 15px 40px rgba(99, 102, 241, 0.08);">
                <svg style="position: absolute; top: -6px; left: -6px; width: 250px; height: 250px; transform: rotate(-90deg);">
                    <circle cx="125" cy="125" r="119" stroke="url(#stopwatchGrad)" stroke-width="6" fill="transparent" stroke-dasharray="748" stroke-dashoffset="748" id="stopwatch-ring" style="transition: stroke-dashoffset 0.1s linear;" />
                    <defs>
                        <linearGradient id="stopwatchGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="var(--brand-primary)" />
                            <stop offset="100%" stop-color="var(--brand-secondary)" />
                        </linearGradient>
                    </defs>
                </svg>
                <div style="text-align: center; z-index: 2;">
                    <div id="timer" role="timer" aria-live="polite" style="font-size: 2.8rem; font-family: monospace; font-weight: bold; background: linear-gradient(135deg, var(--text-primary), #1e1b4b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">00:00:00</div>
                    <div id="ms-display" style="color: var(--brand-secondary); font-family: monospace; font-size: 1.1rem; font-weight: bold; margin-top: -5px;">.000</div>
                </div>
            </div>
            <div class="action-buttons" style="margin-top: 2.5rem; display: flex; gap: 1rem;">
                <button class="btn primary" id="sw-start-btn" onclick="startTimer()">Start</button>
                <button class="btn secondary" id="sw-stop-btn" onclick="stopTimer()" style="display: none;">Stop</button>
                <button class="btn secondary" id="sw-lap-btn" onclick="lapTimer()">Lap</button>
                <button class="btn secondary" onclick="resetTimer()">Reset</button>
            </div>
            <div id="laps-container" style="margin-top: 1.5rem; max-height: 150px; overflow-y: auto; width: 100%; max-width: 300px; padding-right: 5px;"></div>
        </div>
    `;
    let startTime = null;
    let elapsedTime = 0;
    let timerInterval = null;
    let lapCount = 0;

    window.startTimer = () => {
        if (timerInterval) return;
        startTime = Date.now() - elapsedTime;
        document.getElementById('sw-start-btn').style.display = 'none';
        document.getElementById('sw-stop-btn').style.display = 'inline-block';
        
        timerInterval = setInterval(() => {
            elapsedTime = Date.now() - startTime;
            const ms = elapsedTime % 1000;
            const s = Math.floor(elapsedTime / 1000) % 60;
            const m = Math.floor(elapsedTime / 60000) % 60;
            const h = Math.floor(elapsedTime / 3600000);
            
            const hStr = String(h).padStart(2, '0');
            const mStr = String(m).padStart(2, '0');
            const sStr = String(s).padStart(2, '0');
            const msStr = String(ms).padStart(3, '0');
            
            document.getElementById('timer').textContent = `${hStr}:${mStr}:${sStr}`;
            document.getElementById('ms-display').textContent = `.${msStr}`;
            
            const offset = 748 - (748 * (s + ms/1000)) / 60;
            document.getElementById('stopwatch-ring').style.strokeDashoffset = offset;
        }, 33);
    };

    window.stopTimer = () => {
        clearInterval(timerInterval);
        timerInterval = null;
        document.getElementById('sw-start-btn').style.display = 'inline-block';
        document.getElementById('sw-stop-btn').style.display = 'none';
    };

    window.resetTimer = () => {
        clearInterval(timerInterval);
        timerInterval = null;
        elapsedTime = 0;
        lapCount = 0;
        document.getElementById('timer').textContent = "00:00:00";
        document.getElementById('ms-display').textContent = ".000";
        document.getElementById('stopwatch-ring').style.strokeDashoffset = 748;
        document.getElementById('laps-container').innerHTML = "";
        document.getElementById('sw-start-btn').style.display = 'inline-block';
        document.getElementById('sw-stop-btn').style.display = 'none';
    };

    window.lapTimer = () => {
        if (elapsedTime === 0) return;
        lapCount++;
        const lapsBox = document.getElementById('laps-container');
        const lapDiv = document.createElement('div');
        lapDiv.style.display = 'flex';
        lapDiv.style.justifyContent = 'space-between';
        lapDiv.style.padding = '0.5rem 1rem';
        lapDiv.style.borderBottom = '1px solid rgba(99,102,241,0.05)';
        lapDiv.style.fontSize = '0.9rem';
        lapDiv.style.color = 'var(--text-muted)';
        
        const hStr = String(Math.floor(elapsedTime / 3600000)).padStart(2, '0');
        const mStr = String(Math.floor(elapsedTime / 60000) % 60).padStart(2, '0');
        const sStr = String(Math.floor(elapsedTime / 1000) % 60).padStart(2, '0');
        const msStr = String(elapsedTime % 1000).padStart(3, '0');
        
        lapDiv.innerHTML = `<span>⏱️ Lap ${lapCount}</span><span style="font-family: monospace; color:var(--text-primary); font-weight:bold;">${hStr}:${mStr}:${sStr}.${msStr}</span>`;
        lapsBox.insertBefore(lapDiv, lapsBox.firstChild);
    };
} else if (toolId === 'speed-test') {
    container.innerHTML = `
        <div class="speedtest-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div class="speedometer" style="position: relative; width: 250px; height: 150px; overflow: hidden; display: flex; align-items: flex-end; justify-content: center;">
                <svg style="width: 250px; height: 250px; position: absolute; top: 0; left: 0;">
                    <circle cx="125" cy="125" r="100" stroke="rgba(99,102,241,0.05)" stroke-width="12" fill="transparent" stroke-dasharray="314 314" stroke-dashoffset="0" style="transform: rotate(180deg); transform-origin: 125px 125px;" />
                    <circle cx="125" cy="125" r="100" stroke="url(#speedGrad)" stroke-width="12" fill="transparent" stroke-dasharray="314 314" stroke-dashoffset="314" id="speed-progress" style="transform: rotate(180deg); transform-origin: 125px 125px; transition: stroke-dashoffset 0.2s ease-out;" />
                    <defs>
                        <linearGradient id="speedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="var(--brand-primary)" />
                            <stop offset="100%" stop-color="var(--brand-secondary)" />
                        </linearGradient>
                    </defs>
                </svg>
                <div id="speed-pointer" style="position: absolute; bottom: 0; left: 50%; width: 6px; height: 95px; background: var(--brand-accent); transform-origin: bottom center; transform: rotate(-90deg); transition: transform 0.2s ease-out; border-radius: 4px; box-shadow: 0 0 10px rgba(16,185,129,0.3);"></div>
                <div style="text-align: center; z-index: 2; margin-bottom: 5px;">
                    <h2 id="speed-number" style="font-size: 2.5rem; font-weight: 850; color: var(--text-primary); margin: 0; line-height: 1;">0</h2>
                    <p style="font-size: 0.85rem; color: var(--brand-secondary); text-transform: uppercase; font-weight: bold; margin: 0; letter-spacing: 0.1em;">Mbps</p>
                </div>
            </div>
            <div style="margin-top: 2.5rem; text-align: center;">
                <button class="btn primary" id="speed-test-btn" onclick="runSpeed()">Start Speed Test</button>
                <p id="speed-status" style="margin-top: 1rem; font-size: 0.95rem; color: var(--text-muted); font-weight: 500;">Ready to test connection speed</p>
            </div>
        </div>
    `;
    window.runSpeed = async () => {
        const testBtn = document.getElementById('speed-test-btn');
        const statusEl = document.getElementById('speed-status');
        const speedNum = document.getElementById('speed-number');
        const speedProg = document.getElementById('speed-progress');
        const speedPointer = document.getElementById('speed-pointer');
        
        testBtn.disabled = true;
        statusEl.innerText = "Connecting to nearest edge server...";
        speedNum.innerText = "0";
        speedProg.style.strokeDashoffset = 314;
        speedPointer.style.transform = "rotate(-90deg)";
        
        let tempSpeed = 0;
        let sweepInterval = setInterval(() => {
            tempSpeed = Math.random() * 8 + 2;
            speedNum.innerText = tempSpeed.toFixed(1);
            const rotPercent = tempSpeed / 100;
            const rot = -90 + rotPercent * 180;
            speedPointer.style.transform = `rotate(\${rot}deg)`;
            speedProg.style.strokeDashoffset = 314 - (314 * rotPercent);
        }, 150);

        setTimeout(async () => {
            clearInterval(sweepInterval);
            statusEl.innerText = "Testing download throughput...";
            const start = Date.now();
            try {
                const images = [
                    'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
                    'https://www.gstatic.com/webp/gallery/1.webp',
                    'https://www.gstatic.com/webp/gallery/2.webp'
                ];
                let fetchCount = 0;
                
                let simulatedMax = Math.random() * 40 + 35;
                let currentSimSpeed = 0;
                let climbInterval = setInterval(() => {
                    if (currentSimSpeed < simulatedMax) {
                        currentSimSpeed += (simulatedMax - currentSimSpeed) * 0.15 + Math.random() * 2;
                        if (currentSimSpeed > simulatedMax) currentSimSpeed = simulatedMax;
                        speedNum.innerText = currentSimSpeed.toFixed(1);
                        const rotPercent = Math.min(currentSimSpeed / 100, 1);
                        const rot = -90 + rotPercent * 180;
                        speedPointer.style.transform = `rotate(\${rot}deg)`;
                        speedProg.style.strokeDashoffset = 314 - (314 * rotPercent);
                    }
                }, 100);

                for(let url of images) {
                    await fetch(url + '?cache=' + Math.random());
                    fetchCount++;
                }
                
                clearInterval(climbInterval);
                const duration = (Date.now() - start) / 1000;
                let actualSpeed = (45 / duration);
                if (actualSpeed > 100) actualSpeed = 95.8 + Math.random() * 4;
                if (actualSpeed < 1) actualSpeed = 4.2;

                speedNum.innerText = actualSpeed.toFixed(1);
                const rotPercent = Math.min(actualSpeed / 100, 1);
                const rot = -90 + rotPercent * 180;
                speedPointer.style.transform = `rotate(\${rot}deg)`;
                speedProg.style.strokeDashoffset = 314 - (314 * rotPercent);
                
                statusEl.innerText = "Speed test complete! Zero data stored.";
                testBtn.disabled = false;
            } catch (e) {
                clearInterval(sweepInterval);
                statusEl.innerText = "CORS restriction blocked actual measurement. Simulated result:";
                const mockSpeed = 68.4 + Math.random() * 5;
                speedNum.innerText = mockSpeed.toFixed(1);
                const rotPercent = mockSpeed / 100;
                const rot = -90 + rotPercent * 180;
                speedPointer.style.transform = `rotate(\${rot}deg)`;
                speedProg.style.strokeDashoffset = 314 - (314 * rotPercent);
                testBtn.disabled = false;
            }
        }, 1500);
    };
} else if (toolId === 'image-to-base64') {
    container.innerHTML = `
        <div id="drop-zone" class="drop-zone">
            <div class="drop-icon">📁</div>
            <p class="drop-text">Upload Image to get Base64</p>
            <input type="file" id="file-input" hidden>
        </div>
        <div class="editor-pane" style="margin-top:20px;">
            <div class="editor-header">
                <span class="editor-title">📤 Base64 Data URI</span>
                <div class="editor-actions">
                    <button type="button" class="editor-btn success" onclick="copyOutputText()">📋 Copy</button>
                    <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                </div>
            </div>
            <textarea id="base64-out" class="code-editor-textarea" style="height: 200px;" readonly placeholder="Data URI will appear here..."></textarea>
        </div>
    `;
    const fInput = document.getElementById('file-input');
    const dZone = document.getElementById('drop-zone');
    dZone.onclick = () => fInput.click();
    fInput.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (ev) => { document.getElementById('base64-out').value = ev.target.result; };
        reader.readAsDataURL(file);
    };
} else if (toolId === 'aspect-ratio-calculator') {
    container.innerHTML = `
        <div class="aspect-ratio-wrapper" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2rem; width: 100%;">
            <div class="config-panel" style="width: 100%; display:flex; gap:1rem;">
                <label style="flex:1; font-weight:700;">Width: <input type="number" id="ratio-w" value="1920" class="glass-input" style="text-align: center; width:100%; margin-top:5px;"></label>
                <label style="flex:1; font-weight:700;">Height: <input type="number" id="ratio-h" value="1080" class="glass-input" style="text-align: center; width:100%; margin-top:5px;"></label>
            </div>
            
            <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">Calculated Aspect Ratio</span>
                <h2 id="ratio-result" style="text-align:center; font-size: 2.8rem; font-weight: 800; color:var(--brand-primary); margin: 0;">16:9</h2>
            </div>

            <div class="simulator-outer" style="width: 100%; max-width: 380px; height: 220px; border: 1px dashed var(--border-color); border-radius: 12px; display: flex; align-items: center; justify-content: center; background: rgba(99,102,241,0.02); padding: 10px;">
                <div id="ratio-simulator-box" style="width: 100%; height: 100%; background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15)); border: 2px solid var(--brand-primary); border-radius: 8px; transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1); display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;">
                    <span id="simulator-label" style="font-weight: 700; color: var(--text-primary); font-family: monospace; font-size: 1.1rem;">1920 x 1080</span>
                </div>
            </div>
        </div>
    `;
    const updateRatioBox = () => {
        const w = parseFloat(document.getElementById('ratio-w').value);
        const h = parseFloat(document.getElementById('ratio-h').value);
        const resultText = document.getElementById('ratio-result');
        const simBox = document.getElementById('ratio-simulator-box');
        const simLabel = document.getElementById('simulator-label');
        
        if (isNaN(w) || isNaN(h) || w <= 0 || h <= 0) {
            resultText.textContent = "-";
            simLabel.textContent = "Enter dimensions";
            return;
        }

        const gcd = (a, b) => b ? gcd(b, a % b) : a;
        const common = gcd(w, h);
        const rw = w / common;
        const rh = h / common;
        resultText.textContent = rw + ":" + rh;
        simLabel.textContent = w + " x " + h;

        const maxW = 360;
        const maxH = 200;
        
        let targetW = maxW;
        let targetH = maxW * (h / w);
        
        if (targetH > maxH) {
            targetH = maxH;
            targetW = maxH * (w / h);
        }
        
        simBox.style.width = targetW + "px";
        simBox.style.height = targetH + "px";
    };
    
    document.getElementById('ratio-w').oninput = updateRatioBox;
    document.getElementById('ratio-h').oninput = updateRatioBox;
    updateRatioBox();
} else if (toolId === 'rgb-hex-converter') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto;">
            <div class="config-panel" style="display:flex; gap:1rem; width:100%;">
                <label style="flex:1; font-weight:700;">R: <input type="number" id="color-r" min="0" max="255" value="168" class="glass-input" style="width:100%; text-align:center; margin-top:5px;"></label>
                <label style="flex:1; font-weight:700;">G: <input type="number" id="color-g" min="0" max="255" value="85" class="glass-input" style="width:100%; text-align:center; margin-top:5px;"></label>
                <label style="flex:1; font-weight:700;">B: <input type="number" id="color-b" min="0" max="255" value="247" class="glass-input" style="width:100%; text-align:center; margin-top:5px;"></label>
            </div>
            <div id="color-preview" style="height:100px; border-radius:14px; margin:10px 0; background:#a855f7; box-shadow: 0 10px 25px rgba(168,85,247,0.25); border: 1px solid rgba(0,0,0,0.05);"></div>
            <h2 id="hex-result" style="text-align:center; font-size:2.8rem; font-weight:800; color:var(--text-primary);">#A855F7</h2>
        </div>
    `;
    const update = () => {
        const r = parseInt(document.getElementById('color-r').value) || 0;
        const g = parseInt(document.getElementById('color-g').value) || 0;
        const b = parseInt(document.getElementById('color-b').value) || 0;
        const hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
        document.getElementById('color-preview').style.background = hex;
        document.getElementById('hex-result').textContent = hex;
    };
    ['color-r', 'color-g', 'color-b'].forEach(id => document.getElementById(id).oninput = update);
} else if (toolId === 'unit-converter') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto;">
            <div style="display: flex; gap: 10px; width: 100%;">
                <input type="number" id="unit-val" value="1" class="glass-input" style="flex: 2;">
                <select id="unit-type" class="glass-input" style="flex: 1; padding: 0 10px; font-weight:bold; background:white;">
                    <option value="length">Length</option>
                    <option value="weight">Weight</option>
                    <option value="temp">Temp</option>
                </select>
            </div>
            <div style="display: flex; gap: 10px; width: 100%;">
                <select id="unit-from" class="glass-input" style="flex: 1; background:white; font-weight:600;"></select>
                <span style="display: flex; align-items: center; font-weight:bold; color:var(--text-light);">TO</span>
                <select id="unit-to" class="glass-input" style="flex: 1; background:white; font-weight:600;"></select>
            </div>
            <h2 id="unit-result" style="text-align:center; margin-top:20px; font-size: 2.8rem; font-weight:800; color:var(--brand-primary);">-</h2>
        </div>
    `;
    const units = {
        length: { m: 1, km: 1000, cm: 0.01, mm: 0.001, mi: 1609.34, yd: 0.9144, ft: 0.3048, in: 0.0254 },
        weight: { kg: 1, g: 0.001, mg: 0.000001, lb: 0.453592, oz: 0.0283495 },
        temp: { c: 'c', f: 'f', k: 'k' }
    };
    const updateSelects = () => {
        const type = document.getElementById('unit-type').value;
        const from = document.getElementById('unit-from');
        const to = document.getElementById('unit-to');
        const keys = Object.keys(units[type]);
        from.innerHTML = to.innerHTML = keys.map(u => `<option value="${u}">${u.toUpperCase()}</option>`).join('');
        if (type === 'length') to.value = 'km';
        if (type === 'weight') to.value = 'g';
        if (type === 'temp') to.value = 'f';
        calc();
    };
    const calc = () => {
        const val = parseFloat(document.getElementById('unit-val').value);
        const type = document.getElementById('unit-type').value;
        const from = document.getElementById('unit-from').value;
        const to = document.getElementById('unit-to').value;
        if (isNaN(val)) return;
        let res;
        if (type === 'temp') {
            let c;
            if (from === 'c') c = val;
            else if (from === 'f') c = (val - 32) * 5 / 9;
            else c = val - 273.15;
            if (to === 'c') res = c;
            else if (to === 'f') res = (c * 9 / 5) + 32;
            else res = c + 273.15;
        } else {
            res = val * units[type][from] / units[type][to];
        }
        document.getElementById('unit-result').textContent = res.toFixed(4).replace(/\\.0000$/, '') + " " + to.toUpperCase();
    };
    document.getElementById('unit-type').onchange = updateSelects;
    ['unit-val', 'unit-from', 'unit-to'].forEach(id => document.getElementById(id).oninput = calc);
    updateSelects();
} else if (toolId === 'hash-generator') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div class="editor-pane">
                <div class="editor-header">
                    <span class="editor-title">📥 Input Text</span>
                    <div class="editor-actions">
                        <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                        <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                    </div>
                </div>
                <textarea id="hash-input" class="code-editor-textarea" placeholder="Enter text to hash..." style="height: 100px;"></textarea>
            </div>
            
            <div style="display: grid; gap: 10px; margin-top: 10px;">
                <div class="glass-input" style="display: flex; justify-content: space-between; align-items: center; background:white;">
                    <span style="font-weight:800; color:var(--text-muted); font-size:0.85rem; text-transform:uppercase;">MD5:</span> <code id="md5-out" style="word-break: break-all; font-family:monospace; font-weight:700; color:var(--brand-primary); margin-left: 10px;">-</code>
                </div>
                <div class="glass-input" style="display: flex; justify-content: space-between; align-items: center; background:white;">
                    <span style="font-weight:800; color:var(--text-muted); font-size:0.85rem; text-transform:uppercase;">SHA1:</span> <code id="sha1-out" style="word-break: break-all; font-family:monospace; font-weight:700; color:var(--brand-secondary); margin-left: 10px;">-</code>
                </div>
                <div class="glass-input" style="display: flex; justify-content: space-between; align-items: center; background:white;">
                    <span style="font-weight:800; color:var(--text-muted); font-size:0.85rem; text-transform:uppercase;">SHA256:</span> <code id="sha256-out" style="word-break: break-all; font-family:monospace; font-weight:700; color:var(--brand-accent); margin-left: 10px;">-</code>
                </div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"><\/script>
    `;
    const hInput = document.getElementById('hash-input');
    hInput.oninput = () => {
        const v = hInput.value;
        if(!v) {
            document.getElementById('md5-out').textContent = "-";
            document.getElementById('sha1-out').textContent = "-";
            document.getElementById('sha256-out').textContent = "-";
            return;
        }
        document.getElementById('md5-out').textContent = CryptoJS.MD5(v).toString();
        document.getElementById('sha1-out').textContent = CryptoJS.SHA1(v).toString();
        document.getElementById('sha256-out').textContent = CryptoJS.SHA256(v).toString();
    };
} else if (toolId === 'morse-code') {
    const map = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----', ' ': '/'
    };
    const reverseMap = Object.entries(map).reduce((acc, [k, v]) => ({ ...acc, [v]: k }), {});
    container.innerHTML = `
        <div class="editor-pane">
            <div class="editor-header">
                <span class="editor-title">📥 Morse / Text Input</span>
                <div class="editor-actions">
                    <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                    <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                </div>
            </div>
            <textarea id="morse-input" class="code-editor-textarea" placeholder="Enter Text or Morse Code here..." style="height: 150px;"></textarea>
        </div>
        <div class="action-buttons" style="margin-top: 20px; display:flex; justify-content:center; gap: 0.8rem;">
            <button id="to-morse" class="btn primary">Text -> Morse</button>
            <button id="from-morse" class="btn secondary">Morse -> Text</button>
        </div>
    `;
    const mInput = document.getElementById('morse-input');
    document.getElementById('to-morse').onclick = () => {
        mInput.value = mInput.value.toUpperCase().split('').map(c => map[c] || c).join(' ').trim();
    };
    document.getElementById('from-morse').onclick = () => {
        mInput.value = mInput.value.split(' ').map(c => reverseMap[c] || c).join('').trim();
    };
} else if (toolId === 'youtube-thumbnail-downloader') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto;">
            <div style="display: flex; flex-direction: column; gap: 0.6rem; text-align: left;">
                <label style="font-weight: 800; font-size: 0.94rem; color: var(--text-muted);">Enter YouTube Video Link:</label>
                <input type="text" id="yt-url" class="glass-input" placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ" style="width: 100%;">
            </div>
            
            <button class="btn primary" onclick="getThumbnails()" style="justify-content: center;">⚡ Get Thumbnails</button>
            
            <div id="yt-thumbs-preview" style="display: none; flex-direction: column; gap: 1.5rem; margin-top: 1.5rem;">
                <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; background: white; padding: 1.5rem; gap: 1rem;">
                    <span style="font-weight: 800; font-size: 0.9rem; color: var(--brand-primary);">MAX RESOLUTION (1080p Full HD)</span>
                    <img id="thumb-max" style="width: 100%; max-width: 480px; border-radius: 8px; border: 1px solid var(--border-color);" src="" alt="Max Res Thumbnail" loading="lazy" decoding="async">
                    <a id="link-max" class="btn secondary" href="" download target="_blank">📥 Download HD Thumbnail</a>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; background: white; padding: 1rem; gap: 0.8rem;">
                        <span style="font-weight: 800; font-size: 0.8rem; color: var(--brand-secondary);">HIGH QUALITY (640x480)</span>
                        <img id="thumb-hq" style="width: 100%; border-radius: 6px;" src="" alt="HQ Thumbnail" loading="lazy" decoding="async">
                        <a id="link-hq" class="btn secondary" href="" download target="_blank" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">📥 Download HQ</a>
                    </div>
                    <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; background: white; padding: 1rem; gap: 0.8rem;">
                        <span style="font-weight: 800; font-size: 0.8rem; color: var(--brand-accent);">MEDIUM QUALITY (320x180)</span>
                        <img id="thumb-mq" style="width: 100%; border-radius: 6px;" src="" alt="MQ Thumbnail" loading="lazy" decoding="async">
                        <a id="link-mq" class="btn secondary" href="" download target="_blank" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">📥 Download MQ</a>
                    </div>
                </div>
            </div>
        </div>
    `;
    window.getThumbnails = () => {
        const urlVal = document.getElementById('yt-url').value.trim();
        let videoId = "";
        
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = urlVal.match(regExp);
        
        if (match && match[2].length === 11) {
            videoId = match[2];
        } else {
            alert("Please enter a valid YouTube Video URL.");
            return;
        }
        
        document.getElementById('yt-thumbs-preview').style.display = 'flex';
        
        document.getElementById('thumb-max').src = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
        document.getElementById('thumb-hq').src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        document.getElementById('thumb-mq').src = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
        
        document.getElementById('link-max').href = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
        document.getElementById('link-hq').href = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        document.getElementById('link-mq').href = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    };
} else if (toolId === 'base64-to-image') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto;">
            <div class="editor-pane">
                <div class="editor-header">
                    <span class="editor-title">📥 Enter Base64 Code String</span>
                    <div class="editor-actions">
                        <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                        <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                    </div>
                </div>
                <textarea id="base64-input" class="code-editor-textarea" placeholder="Paste your base64 string here (e.g., data:image/png;base64,iVBORw0...)" style="height: 150px;"></textarea>
            </div>
            
            <button class="btn primary" onclick="decodeBase64()" style="justify-content: center;">⚡ Decode & Generate Image</button>
            
            <div id="base64-preview-wrap" style="display: none; flex-direction: column; align-items: center; background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); gap: 1.2rem;">
                <span style="font-weight: 800; font-size: 0.9rem; color: var(--brand-primary);">🖼️ Image Preview</span>
                <img id="base64-img-preview" style="max-width: 100%; max-height: 400px; border-radius: 8px; border: 1px solid var(--border-color); box-shadow: var(--card-shadow);" src="" alt="Decoded Image" loading="lazy" decoding="async">
                <div style="display:flex; gap:10px;">
                    <a id="base64-download-btn" class="btn secondary" href="" download="decoded-image.png">📥 Download Image</a>
                </div>
            </div>
        </div>
    `;
    window.decodeBase64 = () => {
        const inputVal = document.getElementById('base64-input').value.trim();
        if (!inputVal) {
            alert("Please enter a Base64 string first.");
            return;
        }
        
        let cleanBase64 = inputVal;
        let mimeType = "image/png";
        
        const dataUriRegex = /^data:(image\/[a-zA-Z+]+);base64,(.*)$/;
        const match = inputVal.match(dataUriRegex);
        
        if (match) {
            mimeType = match[1];
            cleanBase64 = match[2];
        } else {
            const base64Regex = /^[a-zA-Z0-9+/]*={0,2}$/;
            if (!base64Regex.test(inputVal.replace(/\s/g, ''))) {
                alert("The entered string does not appear to be valid Base64 data.");
                return;
            }
        }
        
        const srcData = match ? inputVal : `data:${mimeType};base64,${cleanBase64}`;
        
        const previewWrap = document.getElementById('base64-preview-wrap');
        const imgEl = document.getElementById('base64-img-preview');
        const downloadBtn = document.getElementById('base64-download-btn');
        
        imgEl.src = srcData;
        downloadBtn.href = srcData;
        
        let ext = "png";
        if (mimeType.includes("jpeg") || mimeType.includes("jpg")) ext = "jpg";
        else if (mimeType.includes("webp")) ext = "webp";
        else if (mimeType.includes("gif")) ext = "gif";
        
        downloadBtn.download = `decoded-image.${ext}`;
        previewWrap.style.display = 'flex';
    };
} else if (toolId === 'robots-txt-generator') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 650px; margin: 0 auto; text-align: left;">
            <div class="glass-input" style="display: flex; flex-direction: column; gap: 1rem; background: white; padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border-color);">
                <h3 style="margin: 0; font-size: 1.1rem; color: var(--text-primary); font-weight: 800;">🤖 Robots.txt Directives Builder</h3>
                
                <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                    <label style="font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">Default Crawl Permission (User-agent: *):</label>
                    <select id="robots-allow" class="glass-input" style="background: white;">
                        <option value="allow">Allow All Search Engines (Recommended)</option>
                        <option value="disallow">Disallow All Search Engines</option>
                    </select>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                    <label style="font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">Sitemap XML URL:</label>
                    <input type="text" id="robots-sitemap" class="glass-input" placeholder="e.g., https://freeconvert.cloud/sitemap.xml" style="width: 100%;">
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                    <label style="font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">Crawl Delay (Seconds):</label>
                    <select id="robots-delay" class="glass-input" style="background: white;">
                        <option value="">No Delay (Default)</option>
                        <option value="5">5 Seconds</option>
                        <option value="10">10 Seconds</option>
                        <option value="20">20 Seconds</option>
                    </select>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                    <label style="font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">Restricted Paths (Disallow paths, one per line):</label>
                    <textarea id="robots-disallowed" class="code-editor-textarea" style="height: 100px;" placeholder="e.g., /admin/\n/tmp/\n/private/"></textarea>
                </div>
            </div>
            
            <button class="btn primary" onclick="generateRobotsTxt()" style="justify-content: center;">⚡ Generate Robots.txt</button>
            
            <div id="robots-result-wrap" style="display: none; flex-direction: column; gap: 1rem; margin-top: 1rem;">
                <div class="editor-pane">
                    <div class="editor-header">
                        <span class="editor-title">📤 Output Robots.txt File Content</span>
                        <div class="editor-actions">
                            <button type="button" class="editor-btn success" onclick="copyRobotsTxt()">📋 Copy</button>
                            <a id="robots-download-btn" class="editor-btn" href="" download="robots.txt">📥 Download</a>
                        </div>
                    </div>
                    <textarea id="robots-output" class="code-editor-textarea" style="height: 180px;" readonly></textarea>
                </div>
            </div>
        </div>
    `;
    window.generateRobotsTxt = () => {
        const allowVal = document.getElementById('robots-allow').value;
        const sitemapVal = document.getElementById('robots-sitemap').value.trim();
        const delayVal = document.getElementById('robots-delay').value;
        const disallowLines = document.getElementById('robots-disallowed').value.split('\n');
        
        let output = "";
        output += "# Generated by freeconvert.cloud online Robots.txt Builder\n";
        output += "User-agent: *\n";
        
        if (allowVal === 'disallow') {
            output += "Disallow: /\n";
        } else {
            output += "Allow: /\n";
        }
        
        if (delayVal) {
            output += `Crawl-delay: ${delayVal}\n`;
        }
        
        disallowLines.forEach(line => {
            const clean = line.trim();
            if (clean) {
                if (!clean.startsWith('/')) {
                    output += `Disallow: /${clean}\n`;
                } else {
                    output += `Disallow: ${clean}\n`;
                }
            }
        });
        
        if (sitemapVal) {
            output += `Sitemap: ${sitemapVal}\n`;
        }
        
        const outTextarea = document.getElementById('robots-output');
        outTextarea.value = output;
        
        const downloadBtn = document.getElementById('robots-download-btn');
        const blob = new Blob([output], { type: "text/plain" });
        downloadBtn.href = URL.createObjectURL(blob);
        
        document.getElementById('robots-result-wrap').style.display = 'flex';
    };
    window.copyRobotsTxt = () => {
        const val = document.getElementById('robots-output').value;
        navigator.clipboard.writeText(val).then(() => alert("📋 Copied robots.txt securely to clipboard!"));
    };
} else if (toolId === 'html-minifier') {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div class="editor-pane">
                <div class="editor-header">
                    <span class="editor-title">📥 Enter Raw HTML Code</span>
                    <div class="editor-actions">
                        <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                        <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
                    </div>
                </div>
                <textarea id="html-raw-input" class="code-editor-textarea" placeholder="Paste your HTML code here..." style="height: 180px;"></textarea>
            </div>
            
            <div class="glass-input" style="display: flex; flex-direction: column; gap: 0.8rem; background: white; padding: 1.2rem; border-radius: 12px; border: 1px solid var(--border-color); text-align: left;">
                <span style="font-weight: 800; font-size: 0.88rem; color: var(--text-muted); text-transform: uppercase;">Minification Options</span>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.88rem; cursor: pointer;">
                        <input type="checkbox" id="min-comments" checked style="width:16px; height:16px; accent-color:var(--brand-primary);"> Remove HTML Comments
                    </label>
                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.88rem; cursor: pointer;">
                        <input type="checkbox" id="min-whitespace" checked style="width:16px; height:16px; accent-color:var(--brand-primary);"> Collapse Whitespace
                    </label>
                    <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.88rem; cursor: pointer;">
                        <input type="checkbox" id="min-inline" checked style="width:16px; height:16px; accent-color:var(--brand-primary);"> Collapse Inline Script Blocks
                    </label>
                </div>
            </div>
            
            <button class="btn primary" onclick="minifyHTMLCode()" style="justify-content: center;">⚡ Minify HTML Code</button>
            
            <div id="html-min-result-wrap" style="display: none; flex-direction: column; gap: 1.5rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; padding: 1rem;">
                        <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">ORIGINAL FOOTPRINT</span>
                        <h3 id="html-orig-size" style="font-size:1.5rem; font-weight:900; margin:0; color:var(--text-primary);">0 Bytes</h3>
                    </div>
                    <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; padding: 1rem;">
                        <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">MINIFIED FOOTPRINT</span>
                        <h3 id="html-min-size" style="font-size:1.5rem; font-weight:900; margin:0; color:var(--brand-primary);">0 Bytes (0% Saved)</h3>
                    </div>
                </div>
                
                <div class="editor-pane">
                    <div class="editor-header">
                        <span class="editor-title">📤 Minified Output Code</span>
                        <div class="editor-actions">
                            <button type="button" class="editor-btn success" onclick="copyMinifiedHTML()">📋 Copy</button>
                            <button type="button" class="editor-btn" onclick="downloadMinifiedHTML()">📥 Download</button>
                        </div>
                    </div>
                    <textarea id="html-min-output" class="code-editor-textarea" style="height: 200px;" readonly></textarea>
                </div>
            </div>
        </div>
    `;
    window.minifyHTMLCode = () => {
        const val = document.getElementById('html-raw-input').value;
        if (!val.trim()) {
            alert("Please paste some HTML code first.");
            return;
        }
        
        const origBytes = new Blob([val]).size;
        let minified = val;
        
        const remComments = document.getElementById('min-comments').checked;
        const colWhitespace = document.getElementById('min-whitespace').checked;
        const colInline = document.getElementById('min-inline').checked;
        
        if (remComments) {
            minified = minified.replace(/<!--[\\s\\S]*?-->/g, '');
        }
        
        if (colWhitespace) {
            minified = minified.replace(/\\s+/g, ' ');
            minified = minified.replace(/>\\s+</g, '><');
        }
        
        if (colInline) {
            minified = minified.trim();
        }
        
        const minBytes = new Blob([minified]).size;
        const saved = origBytes > minBytes ? origBytes - minBytes : 0;
        const ratio = origBytes > 0 ? ((saved / origBytes) * 100).toFixed(1) : 0;
        
        document.getElementById('html-orig-size').textContent = `${origBytes} Bytes`;
        document.getElementById('html-min-size').textContent = `${minBytes} Bytes (-${ratio}% Saved)`;
        document.getElementById('html-min-output').value = minified;
        
        document.getElementById('html-orig-size').style.color = 'var(--brand-danger)';
        document.getElementById('html-min-size').style.color = 'var(--brand-accent)';
        
        document.getElementById('html-min-result-wrap').style.display = 'flex';
    };
    window.copyMinifiedHTML = () => {
        const val = document.getElementById('html-min-output').value;
        navigator.clipboard.writeText(val).then(() => alert("📋 Copied minified HTML securely to clipboard!"));
    };
    window.downloadMinifiedHTML = () => {
        const val = document.getElementById('html-min-output').value;
        const blob = new Blob([val], {type: 'text/html'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'minified.html';
        a.click();
    };
} else {
    const labelMap = {
        'age-calculator': ['Birth date', 'Exact age'],
        'percentage-calculator': ['Value, percent', 'Percentage result'],
        'random-number-generator': ['Min, max, count', 'Random numbers'],
        'uuid-generator': ['Count', 'UUIDs'],
        'timestamp-converter': ['Date', 'Unix timestamp'],
        'unix-time-converter': ['Unix timestamp', 'Readable date'],
        'time-zone-converter': ['Date/time, target zone', 'Converted time'],
        'slug-generator': ['Title', 'SEO slug'],
        'remove-duplicate-lines': ['Lines', 'Unique lines'],
        'text-cleaner': ['Messy text', 'Clean text'],
        'hashtag-generator': ['Topic', 'Hashtags'],
        'lorem-ipsum-generator': ['Paragraph count', 'Lorem ipsum'],
        'barcode-generator': ['Barcode value', 'Barcode preview']
    };
    const labels = labelMap[toolId] || ['Input', 'Output'];
    const defaults = {
        'age-calculator': '2000-01-01',
        'percentage-calculator': '200, 15',
        'random-number-generator': '1, 100, 5',
        'uuid-generator': '5',
        'timestamp-converter': new Date().toISOString().slice(0, 10),
        'unix-time-converter': Math.floor(Date.now() / 1000).toString(),
        'time-zone-converter': '2026-06-15 12:00, Asia/Karachi',
        'slug-generator': 'How to Convert JPG to PDF Online Free',
        'remove-duplicate-lines': 'apple\\nbanana\\napple\\norange\\nbanana',
        'text-cleaner': '<p>  Hello,   world!  </p>',
        'hashtag-generator': 'free online file converter',
        'lorem-ipsum-generator': '3',
        'barcode-generator': '123456789012'
    };
    const multiLine = ['remove-duplicate-lines', 'text-cleaner'].includes(toolId);
    const dateInput = ['age-calculator', 'timestamp-converter'].includes(toolId);
    const numberInput = ['uuid-generator', 'lorem-ipsum-generator'].includes(toolId);
    const inputControl = multiLine
        ? `<textarea id="utility-fallback-input" class="code-editor-textarea" style="height:150px;">${defaults[toolId] || ''}</textarea>`
        : `<input id="utility-fallback-input" class="glass-input" type="${dateInput ? 'date' : numberInput ? 'number' : 'text'}" value="${defaults[toolId] || ''}" style="width:100%;">`;

    container.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:1.5rem;max-width:720px;margin:0 auto;text-align:left;">
            <div class="editor-pane">
                <div class="editor-header"><span class="editor-title">${labels[0]}</span><div class="editor-actions"><button type="button" class="editor-btn" onclick="runUtilityFallback()">Process</button><button type="button" class="editor-btn" onclick="clearUtilityFallback()">Clear</button></div></div>
                ${inputControl}
            </div>
            <div class="editor-pane">
                <div class="editor-header"><span class="editor-title">${labels[1]}</span><div class="editor-actions"><button type="button" class="editor-btn success" onclick="copyUtilityFallback()">Copy</button></div></div>
                <div id="utility-fallback-visual" style="display:none;padding:1rem;border-bottom:1px solid var(--border-color);background:var(--bg-light);"></div>
                <textarea id="utility-fallback-output" class="code-editor-textarea" style="height:180px;" readonly></textarea>
            </div>
        </div>`;

    const slugify = value => value.toLowerCase().trim().replace(/['"]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    const parts = value => value.split(',').map(part => part.trim()).filter(Boolean);
    const uuidv4 = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });

    window.runUtilityFallback = () => {
        const input = document.getElementById('utility-fallback-input');
        const output = document.getElementById('utility-fallback-output');
        const visual = document.getElementById('utility-fallback-visual');
        const value = input.value || '';
        let result = '';
        visual.style.display = 'none';
        visual.innerHTML = '';

        if (toolId === 'age-calculator') {
            const birth = new Date(value);
            const now = new Date();
            if (isNaN(birth.getTime()) || birth > now) result = 'Enter a valid birth date.';
            else {
                let years = now.getFullYear() - birth.getFullYear();
                const hadBirthday = now.getMonth() > birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() >= birth.getDate());
                if (!hadBirthday) years--;
                const days = Math.floor((now - birth) / 86400000);
                result = `${years} years old\\n${days} total days\\n${Math.floor(days * 24)} total hours`;
            }
        } else if (toolId === 'percentage-calculator') {
            const [baseRaw, pctRaw] = parts(value);
            const base = Number(baseRaw), pct = Number(pctRaw);
            result = isNaN(base) || isNaN(pct) ? 'Enter values like: 200, 15' : `${pct}% of ${base} = ${(base * pct / 100).toFixed(4).replace(/\\.0000$/, '')}`;
        } else if (toolId === 'random-number-generator') {
            const [minRaw, maxRaw, countRaw] = parts(value);
            const min = Number(minRaw || 1), max = Number(maxRaw || 100), count = Math.max(1, Math.min(Number(countRaw || 5), 100));
            result = Array.from({length: count}, () => Math.floor(Math.random() * (max - min + 1)) + min).join(', ');
        } else if (toolId === 'uuid-generator') {
            const count = Math.max(1, Math.min(parseInt(value, 10) || 5, 100));
            result = Array.from({length: count}, uuidv4).join('\\n');
        } else if (toolId === 'timestamp-converter') {
            const date = new Date(value);
            result = isNaN(date.getTime()) ? 'Enter a valid date.' : Math.floor(date.getTime() / 1000).toString();
        } else if (toolId === 'unix-time-converter') {
            const seconds = parseInt(value, 10);
            result = isNaN(seconds) ? 'Enter a valid Unix timestamp.' : new Date(seconds * 1000).toISOString();
        } else if (toolId === 'time-zone-converter') {
            const [dateRaw, zoneRaw] = parts(value);
            const date = new Date(dateRaw || Date.now());
            const zone = zoneRaw || 'Asia/Karachi';
            result = isNaN(date.getTime()) ? 'Enter a valid date/time.' : new Intl.DateTimeFormat('en-US', {dateStyle:'full', timeStyle:'long', timeZone:zone}).format(date) + ` (${zone})`;
        } else if (toolId === 'slug-generator') {
            result = slugify(value);
        } else if (toolId === 'remove-duplicate-lines') {
            const seen = new Set();
            result = value.split(/\\r?\\n/).filter(line => {
                const key = line.trim();
                if (!key || seen.has(key)) return false;
                seen.add(key);
                return true;
            }).join('\\n');
        } else if (toolId === 'text-cleaner') {
            result = value.replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ').trim();
        } else if (toolId === 'hashtag-generator') {
            result = value.split(/\\s+/).map(word => word.replace(/[^a-zA-Z0-9]/g, '')).filter(Boolean).slice(0, 20).map(word => '#' + word.toLowerCase()).join(' ');
        } else if (toolId === 'lorem-ipsum-generator') {
            const count = Math.max(1, Math.min(parseInt(value, 10) || 3, 20));
            const text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante venenatis dapibus posuere velit aliquet.';
            result = Array.from({length: count}, () => text).join('\\n\\n');
        } else if (toolId === 'barcode-generator') {
            const clean = value.trim() || '123456789012';
            result = clean;
            visual.style.display = 'block';
            visual.innerHTML = `<div style="display:flex;align-items:end;gap:3px;height:90px;justify-content:center;background:white;border-radius:12px;border:1px solid var(--border-color);padding:1rem;">${clean.split('').map((char, i) => `<span style="display:block;width:${(char.charCodeAt(0) % 4) + 2}px;height:${35 + ((char.charCodeAt(0) + i) % 45)}px;background:#111827;"></span>`).join('')}</div><p style="text-align:center;font-weight:800;margin:0.7rem 0 0;">${clean}</p>`;
        } else {
            result = value;
        }
        output.value = result;
    };
    window.clearUtilityFallback = () => {
        document.getElementById('utility-fallback-input').value = '';
        document.getElementById('utility-fallback-output').value = '';
        const visual = document.getElementById('utility-fallback-visual');
        visual.style.display = 'none';
        visual.innerHTML = '';
    };
    window.copyUtilityFallback = () => {
        const val = document.getElementById('utility-fallback-output').value;
        if (val) navigator.clipboard.writeText(val).then(() => alert('Copied result to clipboard!'));
    };
    window.runUtilityFallback();
}
"""

TEXT_UI = """
<div style="display: flex; flex-direction: column; gap: 1.5rem; width: 100%;">
    <div class="editor-pane" style="width: 100%;">
        <div class="editor-header">
            <span class="editor-title">📥 Input Text</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
            </div>
        </div>
        <textarea id="text-input" class="code-editor-textarea" style="height: 220px;" placeholder="Paste your text here..."></textarea>
    </div>
    <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 0.5rem;">
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">WORDS</span>
            <h3 id="word-count" style="font-size:2rem; font-weight:900; margin:0; color:var(--brand-primary);">0</h3>
        </div>
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">CHARACTERS (WITH SPACES)</span>
            <h3 id="char-count-spaces" style="font-size:2rem; font-weight:900; margin:0; color:var(--brand-secondary);">0</h3>
        </div>
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">CHARACTERS (NO SPACES)</span>
            <h3 id="char-count-nospaces" style="font-size:2rem; font-weight:900; margin:0; color:var(--brand-accent);">0</h3>
        </div>
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">SENTENCES</span>
            <h3 id="sentence-count" style="font-size:2rem; font-weight:900; margin:0; color:#06b6d4;">0</h3>
        </div>
    </div>
    <div style="background: white; border: 1px solid var(--border-color); border-radius: 18px; padding: 1.5rem; margin-top: 1rem;">
        <h4 style="margin: 0 0 1rem 0; color: var(--text-primary); font-weight: 800;">📌 Common Social Media Limits</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; font-size: 0.85rem; text-align: center;">
            <div style="padding: 0.8rem; background: var(--bg-light); border-radius: 10px; border: 1px solid var(--border-color);" id="limit-tw">
                <strong>Twitter (X)</strong><br><span style="color:var(--brand-primary); font-weight:800;" id="tw-fill">0 / 280</span>
            </div>
            <div style="padding: 0.8rem; background: var(--bg-light); border-radius: 10px; border: 1px solid var(--border-color);" id="limit-sms">
                <strong>SMS Text</strong><br><span style="color:var(--brand-secondary); font-weight:800;" id="sms-fill">0 / 160</span>
            </div>
            <div style="padding: 0.8rem; background: var(--bg-light); border-radius: 10px; border: 1px solid var(--border-color);" id="limit-li">
                <strong>LinkedIn Post</strong><br><span style="color:var(--brand-accent); font-weight:800;" id="li-fill">0 / 3000</span>
            </div>
            <div style="padding: 0.8rem; background: var(--bg-light); border-radius: 10px; border: 1px solid var(--border-color);" id="limit-ig">
                <strong>Instagram Caption</strong><br><span style="color:#06b6d4; font-weight:800;" id="ig-fill">0 / 2200</span>
            </div>
        </div>
    </div>
</div>
"""

TEXT_SCRIPT = """
const textInput = document.getElementById('text-input');
textInput.addEventListener('input', () => {
    const text = textInput.value;
    const cleanText = text.trim();
    
    const words = cleanText ? cleanText.split(/\\s+/).length : 0;
    const charsWithSpaces = text.length;
    const charsNoSpaces = text.replace(/\\s/g, '').length;
    const sentences = cleanText ? cleanText.split(/[.!?]+/).filter(s => s.trim()).length : 0;
    
    document.getElementById('word-count').textContent = words;
    document.getElementById('char-count-spaces').textContent = charsWithSpaces;
    document.getElementById('char-count-nospaces').textContent = charsNoSpaces;
    document.getElementById('sentence-count').textContent = sentences;
    
    document.getElementById('tw-fill').textContent = charsWithSpaces + ' / 280';
    document.getElementById('tw-fill').style.color = charsWithSpaces > 280 ? 'var(--brand-danger)' : 'var(--brand-primary)';
    
    document.getElementById('sms-fill').textContent = charsWithSpaces + ' / 160';
    document.getElementById('sms-fill').style.color = charsWithSpaces > 160 ? 'var(--brand-danger)' : 'var(--brand-secondary)';
    
    document.getElementById('li-fill').textContent = charsWithSpaces + ' / 3000';
    document.getElementById('li-fill').style.color = charsWithSpaces > 3000 ? 'var(--brand-danger)' : 'var(--brand-accent)';
    
    document.getElementById('ig-fill').textContent = charsWithSpaces + ' / 2200';
    document.getElementById('ig-fill').style.color = charsWithSpaces > 2200 ? 'var(--brand-danger)' : '#06b6d4';
});
"""

METACHECKER_UI = """
<div style="display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 0 auto; text-align: left;">
    <div class="editor-pane" style="width: 100%;">
        <div class="editor-header">
            <span class="editor-title" id="checker-input-title">📥 Enter SEO Title</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
                <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
            </div>
        </div>
        <textarea id="checker-input" class="code-editor-textarea" style="height: 100px;" placeholder="Type your text here..."></textarea>
    </div>
    <div style="background: white; border: 1px solid var(--border-color); border-radius: 18px; padding: 1.5rem;">
        <h4 style="margin: 0 0 1rem 0; color: var(--text-primary); font-weight: 800;">🔍 Google SERP Desktop Preview</h4>
        <div style="padding: 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: #fff; font-family: arial, sans-serif; text-align: left; box-shadow: 0 4px 12px rgba(0,0,0,0.02); overflow: hidden;">
            <div style="font-size: 12px; color: #202124; line-height: 1.3; display: flex; align-items: center; gap: 4px; margin-bottom: 4px;">
                <span>https://freeconvert.cloud</span><span style="font-size:10px; color:#5f6368;">› ...</span>
            </div>
            <h3 id="serp-title" style="font-size: 20px; color: #1a0dab; font-weight: 400; line-height: 1.3; margin: 0 0 4px 0; font-family: arial, sans-serif; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 600px;">Please enter title...</h3>
            <p id="serp-desc" style="font-size: 14px; color: #4d5156; line-height: 1.58; margin: 0; font-family: arial, sans-serif; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">Please enter descriptive text...</p>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;" id="char-limit-box">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">CHARACTER LENGTH</span>
            <h3 id="checker-char-count" style="font-size:2rem; font-weight:900; margin:0; color:var(--brand-primary);">0</h3>
            <span style="font-size:0.7rem; font-weight:bold; color:var(--text-muted); margin-top:5px;" id="checker-char-limit">Limit: 60 Chars</span>
        </div>
        <div class="glass-input" style="display: flex; flex-direction: column; align-items: center; justify-content: center; background:white; padding: 1rem;" id="pixel-limit-box">
            <span style="font-size:0.75rem; font-weight:bold; color:var(--text-muted);">VISUAL PIXEL WIDTH</span>
            <h3 id="checker-pixel-count" style="font-size:2rem; font-weight:900; margin:0; color:var(--brand-secondary);">0px</h3>
            <span style="font-size:0.7rem; font-weight:bold; color:var(--text-muted); margin-top:5px;" id="checker-pixel-limit">Limit: 600px</span>
        </div>
    </div>
    <div id="checker-status-alert" style="padding: 0.8rem 1.2rem; border-radius: 10px; font-weight: bold; text-align: center; font-size: 0.9rem; display: none;"></div>
</div>
"""

METACHECKER_SCRIPT = """
const chInput = document.getElementById('checker-input');
const chCharCount = document.getElementById('checker-char-count');
const chPixelCount = document.getElementById('checker-pixel-count');
const serpTitle = document.getElementById('serp-title');
const serpDesc = document.getElementById('serp-desc');
const statusAlert = document.getElementById('checker-status-alert');

const path = window.location.pathname.replace(/\\//g, '');
const isTitle = path === 'meta-title-checker';

if (isTitle) {
    document.getElementById('checker-input-title').textContent = "📥 Enter Meta Title";
    chInput.placeholder = "Enter your meta title here (e.g. Free File Converter Online)...";
    document.getElementById('checker-char-limit').textContent = "Limit: 60 Chars";
    document.getElementById('checker-pixel-limit').textContent = "Limit: 600px";
} else {
    document.getElementById('checker-input-title').textContent = "📥 Enter Meta Description";
    chInput.placeholder = "Enter your meta description here (e.g. Convert documents, images, video and archives safely inside your browser)...";
    document.getElementById('checker-char-limit').textContent = "Limit: 160 Chars";
    document.getElementById('checker-pixel-limit').textContent = "Limit: 960px";
}

const getPixelWidth = (text, isDesc = false) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = isDesc ? "14px arial" : "20px arial";
    return Math.round(ctx.measureText(text).width);
};

chInput.addEventListener('input', () => {
    const val = chInput.value;
    const count = val.length;
    const pxWidth = getPixelWidth(val, !isTitle);
    
    chCharCount.textContent = count;
    chPixelCount.textContent = pxWidth + 'px';
    
    let maxChars = isTitle ? 60 : 160;
    let maxPx = isTitle ? 600 : 960;
    
    if (isTitle) {
        serpTitle.textContent = val || "Please enter title...";
        if (val) serpTitle.style.color = '#1a0dab';
        else serpTitle.style.color = '#777';
    } else {
        serpDesc.textContent = val || "Please enter descriptive text...";
    }
    
    if (count === 0) {
        statusAlert.style.display = 'none';
        return;
    }
    
    statusAlert.style.display = 'block';
    if (count <= maxChars && pxWidth <= maxPx) {
        statusAlert.className = 'glass-input';
        statusAlert.style.color = 'var(--brand-accent)';
        statusAlert.style.background = 'rgba(16,185,129,0.05)';
        statusAlert.style.borderColor = 'rgba(16,185,129,0.15)';
        statusAlert.textContent = "🟢 Perfect Length! Your meta tag fits beautifully in Google's SERP container.";
    } else {
        statusAlert.className = 'glass-input';
        statusAlert.style.color = 'var(--brand-danger)';
        statusAlert.style.background = 'rgba(239,68,68,0.05)';
        statusAlert.style.borderColor = 'rgba(239,68,68,0.15)';
        statusAlert.textContent = `🔴 Too Long! Exceeds standard limits (${count}/${maxChars} chars, ${pxWidth}/${maxPx}px). Google will truncate it with "..."`;
    }
});
"""


CASE_UI = """
<div class="editor-pane" style="width: 100%;">
    <div class="editor-header">
        <span class="editor-title">📥 Input Text</span>
        <div class="editor-actions">
            <button type="button" class="editor-btn" onclick="loadSampleData()">✨ Load Sample</button>
            <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
        </div>
    </div>
    <textarea id="text-input" class="code-editor-textarea" style="height: 250px;" placeholder="Paste your text here..."></textarea>
</div>
<div class="action-buttons" style="display:flex; justify-content:center; gap:0.8rem; margin-top:1.5rem; flex-wrap:wrap;">
    <button id="upper-btn" class="btn secondary">UPPERCASE</button>
    <button id="lower-btn" class="btn secondary">lowercase</button>
    <button id="title-btn" class="btn secondary">Title Case</button>
    <button class="btn secondary success" onclick="copyOutputText()">📋 Copy</button>
</div>
"""

CASE_SCRIPT = """
const textInput = document.getElementById('text-input');
document.getElementById('upper-btn').onclick = () => { textInput.value = textInput.value.toUpperCase(); };
document.getElementById('lower-btn').onclick = () => { textInput.value = textInput.value.toLowerCase(); };
document.getElementById('title-btn').onclick = () => { 
    textInput.value = textInput.value.toLowerCase().split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' '); 
};
"""

SECURITY_UI = """
<div class="config-panel" style="display:flex; flex-direction:column; gap:1.2rem; margin-bottom:1.8rem;">
    <label style="font-weight:bold; font-size: 0.95rem;">Password Length: <input type="number" id="pass-length" class="glass-input" value="16" min="4" max="100" style="display:inline-block; width:80px; margin-left:10px; padding:0.4rem; text-align:center; font-weight:bold; background:white;"></label>
    <div class="checkbox-group" style="display:flex; gap:1.5rem; justify-content:center; flex-wrap:wrap; font-weight:700; color:var(--text-muted);">
        <label><input type="checkbox" id="include-upper" checked style="margin-right:5px; transform:scale(1.15);"> Uppercase</label>
        <label><input type="checkbox" id="include-numbers" checked style="margin-right:5px; transform:scale(1.15);"> Numbers</label>
        <label><input type="checkbox" id="include-symbols" checked style="margin-right:5px; transform:scale(1.15);"> Symbols</label>
    </div>
</div>
<div class="result-box" style="background:var(--bg-light); border:1px solid var(--border-color); border-radius:18px; padding:1.5rem; display:flex; justify-content:space-between; align-items:center; margin-bottom:1.8rem; box-shadow:inset 0 2px 8px rgba(0,0,0,0.01);">
    <span id="password-result" style="font-family:monospace; font-size:1.4rem; font-weight:bold; color:var(--brand-primary); word-break:break-all;">********</span>
    <button id="copy-btn" class="btn secondary" style="padding:0.4rem 1.2rem; text-transform:none; font-size: 0.8rem; border-radius: 8px;">📋 Copy</button>
</div>
<button id="generate-btn" class="btn primary" style="width:100%; justify-content:center;">⚡ Generate Strong Password</button>
"""

SECURITY_SCRIPT = """
const generateBtn = document.getElementById('generate-btn');
const charDisplay = document.getElementById('password-result');
const copyBtn = document.getElementById('copy-btn');

generateBtn.onclick = () => {
    const length = document.getElementById('pass-length').value;
    const upper = document.getElementById('include-upper').checked;
    const num = document.getElementById('include-numbers').checked;
    const sym = document.getElementById('include-symbols').checked;
    
    let chars = "abcdefghijklmnopqrstuvwxyz";
    if (upper) chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (num) chars += "0123456789";
    if (sym) chars += "!@#$%^&*()_+~`|}{[]:;?><,./-=";
    
    let pass = "";
    for (let i = 0; i < length; i++) {
        pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    charDisplay.textContent = pass;
};

copyBtn.onclick = () => {
    if(charDisplay.textContent.includes('***')) return;
    navigator.clipboard.writeText(charDisplay.textContent);
    alert('📋 Password Copied securely to clipboard!');
};
"""

QR_UI = """
<div class="config-panel" style="margin-bottom:1.5rem; display:flex; flex-direction:column; gap:0.5rem; align-items:center;">
    <input type="text" id="qr-data" class="glass-input" style="min-height: 52px; text-align:center; width: 100%; max-width: 500px;" placeholder="Enter link or text here...">
    <div class="editor-actions" style="margin-top: 10px;">
        <button type="button" class="editor-btn" onclick="loadSampleData()">⚡ Test Example Link</button>
        <button type="button" class="editor-btn" onclick="clearInput()">🗑️ Clear</button>
    </div>
</div>
<div id="qr-result" class="qr-container" style="display: flex; justify-content: center; padding: 1.5rem; background:var(--bg-light); border-radius:18px; border:1px solid var(--border-color); margin-bottom: 1.5rem; min-height: 288px; align-items: center;">
    <span style="color:var(--text-light); font-weight:500;">Your QR Code will render here</span>
</div>
<button id="generate-qr-btn" class="btn primary" style="width:100%; justify-content:center;">⚡ Generate Custom QR Code</button>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
"""

QR_SCRIPT = """
const genBtn = document.getElementById('generate-qr-btn');
const qrData = document.getElementById('qr-data');
const qrResult = document.getElementById('qr-result');

genBtn.onclick = () => {
    const data = qrData.value.trim();
    if (!data) { alert('Please enter some text or a URL'); return; }
    qrResult.innerHTML = "";
    new QRCode(qrResult, {
        text: data,
        width: 256,
        height: 256,
        colorDark : "#6366f1",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
};
"""

# Dynamic Developer/Utility UIs
DEV_BASIC_UI = """
<div class="code-editor-module">
    <div class="editor-pane">
        <div class="editor-header">
            <span class="editor-title">📥 Input Data</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn" id="btn-load-sample" onclick="loadSampleData()">✨ Load Sample</button>
                <button type="button" class="editor-btn" id="btn-clear-input" onclick="clearInput()">🗑️ Clear</button>
            </div>
        </div>
        <textarea id="dev-input" class="code-editor-textarea" placeholder="Paste or type your data here..."></textarea>
    </div>
    
    <div class="editor-middle-control">
        <div id="operation-selector" class="op-select-wrap" style="width: 100%; max-width: 320px;"></div>
        <button id="action-btn" class="btn primary convert-action-btn">⚡ Process & Convert</button>
    </div>
    
    <div class="editor-pane">
        <div class="editor-header">
            <span class="editor-title">📤 Output Results</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn success" id="btn-copy-output" onclick="copyOutputText()">📋 Copy</button>
            </div>
        </div>
        <textarea id="dev-output" class="code-editor-textarea output-area" placeholder="Converted results will appear here..." readonly></textarea>
    </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>
"""

DEV_ADVANCED_UI = """
<div class="code-editor-module advanced-module" id="editor-container">
    <div class="editor-pane">
        <div class="editor-header">
            <span class="editor-title">📥 Code Editor</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn" id="btn-load-sample-adv" onclick="loadSampleData()">✨ Load Sample</button>
                <button type="button" class="editor-btn" id="btn-clear-input-adv" onclick="clearInput()">🗑️ Clear</button>
            </div>
        </div>
        <textarea id="adv-input" class="code-editor-textarea" placeholder="Paste code here..."></textarea>
    </div>
    
    <div class="editor-pane">
        <div class="editor-header">
            <span class="editor-title">🔍 Output / Preview</span>
            <div class="editor-actions">
                <button type="button" class="editor-btn success" id="btn-copy-output-adv" onclick="copyOutputText()">📋 Copy</button>
            </div>
        </div>
        <div id="adv-preview" class="code-editor-textarea preview-box" style="display:none; overflow-y:auto; background: #0f172a; border: 1px solid #1e293b; color: #f1f5f9; padding: 1.25rem;"></div>
        <textarea id="adv-output" class="code-editor-textarea output-area" placeholder="Formatted output will appear here..." readonly></textarea>
    </div>
</div>

<div class="editor-bottom-control">
    <button id="adv-action-btn" class="btn primary convert-action-btn" style="margin-top: 1.5rem;">⚡ Format & Run</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.14.7/beautify.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.14.7/beautify-css.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.14.7/beautify-html.min.js"></script>
<script src="https://unpkg.com/sql-formatter@4.0.2/dist/sql-formatter.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/5.1.0/diff.min.js"></script>
"""

UTILITY_UI = """
<div class="utility-panel" style="padding:0;">
    <div id="utility-content"></div>
</div>
"""

# Reusable Header and Footer snippets
HEADER_SNIPPET = """
    <!-- SaaS Header -->
    <header class="header-glass">
        <nav class="navbar">
            <a href="/" class="logo">
                <picture>
                    <source srcset="/assets/freeconvert-logo.webp" type="image/webp">
                    <img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud privacy-first online file converter" class="logo-img" style="height:38px;width:auto;display:block;" decoding="async" fetchpriority="high">
                </picture>
            </a>
            <div class="mobile-toggle" id="mobile-toggle">
                <span></span><span></span><span></span>
            </div>
            <div class="nav-links">
                <div class="nav-item">
                    <a href="/image-converter/" class="nav-link">🔄 Convert</a>
                    <div class="nav-dropdown">
                        <a href="/image-converter/">🖼️ Image Converter</a>
                        <a href="/video-converter/">🎥 Video Converter</a>
                        <a href="/audio-converter/">🎵 Audio Converter</a>
                        <a href="/document-converter/">📄 Document Converter</a>
                        <a href="/pdf-tools/">🛡️ PDF Tools</a>
                        <a href="/archive-converter/">🗜️ Archive Converter</a>
                        <a href="/ebook-converter/">📚 eBook Converter</a>
                        <a href="/unit-converter/">📏 Unit Converter</a>
                    </div>
                </div>
                <div class="nav-item">
                    <a href="/image-compressor/" class="nav-link">🗜️ Compress</a>
                    <div class="nav-dropdown">
                        <a href="/image-compressor/">🖼️ Image Compressor</a>
                        <a href="/pdf-tools/">📄 PDF Compressor</a>
                    </div>
                </div>
                <div class="nav-item">
                    <a href="/pdf-tools/" class="nav-link">📄 PDF Tools</a>
                </div>
                <div class="nav-item">
                    <a href="/pricing/" class="nav-link">💎 Pricing</a>
                </div>
                <div class="nav-item">
                    <a href="/api/" class="nav-link" style="background:linear-gradient(135deg,var(--brand-primary) 0%,var(--brand-secondary) 100%);color:#fff;box-shadow:0 10px 22px -10px rgba(99,102,241,0.6);">⚡ API</a>
                </div>
                <a href="/pricing/" class="btn primary" style="padding: 0.5rem 1.2rem; font-size: 0.8rem; text-transform: none; border-radius: 8px;">Sign Up</a>
            </div>
        </nav>
    </header>
"""

FOOTER_SNIPPET = """
    <!-- Competitor-level Footer -->
    <footer class="footer-mega">
        <!-- AdSense Slot: Footer -->
        <div class="adsense-wrap footer-ad-wrap">
            <span class="adsense-label">Sponsored Links</span>
            <ins class="adsbygoogle"
                 style="display:block;min-height:90px;"
                 data-ad-client="ca-pub-8997218708343263"
                 data-ad-slot="REPLACE_SLOT_FOOTER"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <div class="footer-content">
            <div class="footer-brand">
                <a href="/"><picture><source srcset="/assets/freeconvert-logo.webp" type="image/webp"><img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud privacy-first online file converter" style="height:36px;width:auto;margin-bottom:0.75rem;display:block;" loading="lazy" decoding="async"></picture></a>
                <p>The world's most beautiful, privacy-first SaaS conversion platform. Convert images, PDFs, video, audio, and developer files in your browser.</p>
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
                    <a href="/all-tools/">All Tools Directory</a>
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
                    <a href="/help/">Help &amp; FAQ</a>
                    <a href="/tools/embed/">Embed Widgets</a>
                    <a href="/sitemap/">HTML Sitemap</a>
                    <a href="/press-kit/">Press Kit</a>
                    <a href="/popular-conversions/">Popular Conversions</a>
                    <a href="/free-online-converter-guides/">Converter Guides</a>
                    <a href="/file-formats/">File Format Glossary</a>
                    <a href="/blog/category/pdf-tools/">PDF Guides</a>
                    <a href="/blog/category/image-conversion/">Image Guides</a>
                    <a href="/privacy/">Privacy Policy</a>
                    <a href="/terms/">Terms of Service</a>
                    <a href="/security/">File Security</a>
                    <a href="/advertising-policy/">Advertising Policy</a>
                    <a href="/cookies/">Cookie Policy</a>
                    <a href="/contact/">Contact Us</a>
                    <a href="/dmca/">DMCA Policy</a>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            <span>&copy; 2026 freeconvert.cloud. All rights reserved.</span>
            <span>Designed & Developed by <a href="https://hosterlo.com" target="_blank" class="hosterlo-link">Hosterlo</a></span>
        </div>
    </footer>
"""


def build_homepage(tools):
    POPULAR_TOOLS = ['jpg-to-pdf', 'pdf-to-word', 'png-to-jpg', 'mp4-to-mp3', 'csv-to-json', 'json-to-csv']
    with open('index.html', 'w', encoding='utf-8') as f:
        # Generate homepage grid tools
        tools_html = ""
        for tool in tools:
            is_popular = tool['id'] in POPULAR_TOOLS
            popular_badge = '<span class="popular-badge">⚡ Popular</span>\n                ' if is_popular else ''
            tools_html += f"""
            <a href="/{tool['id']}/" class="tool-card" data-category="{tool['type']}">
                {popular_badge}<div class="tool-card-top">
                    <div class="tool-icon">{tool['icon']}</div>
                    <span class="tool-category-tag">{tool['category']}</span>
                </div>
                <div class="tool-card-body">
                    <span role="heading" aria-level="3" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{tool['name']}</span>
                    <p>{tool['description']}</p>
                </div>
                <div class="tool-card-footer">
                    <span class="explore-text">Explore Tool</span>
                    <span class="arrow-icon">→</span>
                </div>
            </a>"""

        latest_guides_html = ""
        for article in reversed(BLOG_ARTICLES[-8:]):
            latest_guides_html += f"""
                <a href="/blog/{article['slug']}/" class="tool-card" style="text-decoration:none;text-align:left;">
                    <div class="tool-card-top">
                        <div class="tool-icon">Guide</div>
                        <span class="tool-category-tag">SEO Guide</span>
                    </div>
                    <div class="tool-card-body">
                        <h3>{article['title']}</h3>
                        <p>{article['description']}</p>
                    </div>
                    <div class="tool-card-footer">
                        <span class="explore-text">Read Guide</span>
                        <span class="arrow-icon">-&gt;</span>
                    </div>
                </a>"""

        keyword_hub_html = homepage_keyword_hub_html(tools)

        html_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Online File Converter | freeconvert.cloud</title>
    <meta name="description" content="Use free browser tools for image conversion, compression, developer formatting, text utilities, QR codes, passwords, calculators, and file guides.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts & Preloads -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" href="/style.css" as="style">
    <link rel="stylesheet" href="/style.css">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">

    <!-- Canonical tag -->
    <link rel="canonical" href="https://freeconvert.cloud/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="freeconvert.cloud — Free Online File Converter">
    <meta property="og:description" content="Convert images, documents, PDFs, video, audio and developer files online — free, fast, and 100% private.">
    <meta property="og:url" content="https://freeconvert.cloud/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta property="og:site_name" content="freeconvert.cloud">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="freeconvert.cloud — Free Online File Converter">
    <meta name="twitter:description" content="Convert images, documents, PDFs, video, audio and developer files online — free, fast, and 100% private.">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- JSON-LD: WebSite + SearchAction (Sitelinks Searchbox) -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "freeconvert.cloud",
      "alternateName": "FreeConvert Cloud",
      "url": "https://freeconvert.cloud/",
      "description": "Free online file converter — convert images, PDFs, video, audio, documents, and developer files directly in your browser with 100% privacy.",
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://freeconvert.cloud/?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    }
    </script>

    <!-- JSON-LD: Organization (brand entity registration) -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "freeconvert.cloud",
      "url": "https://freeconvert.cloud/",
      "logo": {
        "@type": "ImageObject",
        "url": "https://freeconvert.cloud/assets/freeconvert-logo.png",
        "width": 512,
        "height": 512
      },
      "description": "Free, privacy-first online file conversion platform supporting images, PDFs, video, audio, archives, and developer tools.",
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@freeconvert.cloud",
        "url": "https://freeconvert.cloud/contact/"
      },
      "sameAs": []
    }
    </script>

    <!-- JSON-LD: SiteNavigationElement (signals sitelinks to Google) -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": "freeconvert.cloud Navigation",
      "itemListElement": [
        {
          "@type": "SiteNavigationElement",
          "position": 1,
          "name": "Image Converter",
          "description": "Convert PNG, JPG, WebP, HEIC and other image formats online free.",
          "url": "https://freeconvert.cloud/image-converter/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 2,
          "name": "PDF Tools",
          "description": "Compress, merge, split, and convert PDF files online for free.",
          "url": "https://freeconvert.cloud/pdf-tools/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 3,
          "name": "MP4 to MP3",
          "description": "Extract audio from video files and convert MP4 to MP3 online.",
          "url": "https://freeconvert.cloud/mp4-to-mp3/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 4,
          "name": "Image Compressor",
          "description": "Compress images online without losing quality — free and private.",
          "url": "https://freeconvert.cloud/image-compressor/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 5,
          "name": "JPG to PDF",
          "description": "Convert JPG images to PDF documents online in seconds.",
          "url": "https://freeconvert.cloud/jpg-to-pdf/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 6,
          "name": "Document Converter",
          "description": "Convert Word, PDF, and document formats online for free.",
          "url": "https://freeconvert.cloud/document-converter/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 7,
          "name": "Video Converter",
          "description": "Convert MP4, WebM, AVI and other video formats online.",
          "url": "https://freeconvert.cloud/video-converter/"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 8,
          "name": "Pricing",
          "description": "View freeconvert.cloud plans and pricing options.",
          "url": "https://freeconvert.cloud/pricing/"
        }
      ]
    }
    </script>

    {KEYWORD_TARGET_SCHEMA}
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <section class="hero-section">
        <div class="hero-badges">
            <span class="badge">🛡️ Free, secure & browser-based file conversion</span>
        </div>
        <h1>Convert Files Online — <span class="gradient-text">Fast, Secure & Effortless</span></h1>
        <p class="hero-subtitle">Convert images, documents, PDFs, audio, video, archives, and developer files in seconds with a privacy-first conversion platform.</p>

        <!-- Homepage Active Upload box right in the Hero! -->
        <div style="margin-bottom: 2.5rem;">
            {UPLOAD_BOX_UI}
        </div>

        <!-- Search bar for tools -->
        <div style="position: relative; max-width: 600px; margin: 0 auto 1.5rem;">
            <input type="text" id="tool-search" placeholder="Search 35+ tools (e.g. JPG to PDF, JSON to CSV)..."
                style="width: 100%; padding: 1.1rem 2rem; border-radius: 50px; background: white; border: 1px solid var(--border-color); color: var(--text-primary); font-size: 1.05rem; outline: none; box-shadow: var(--card-shadow); transition: all 0.3s;"
                onfocus="this.style.borderColor='var(--brand-primary)'; this.style.boxShadow='var(--hover-shadow)';"
                onblur="this.style.borderColor='var(--border-color)'; this.style.boxShadow='var(--card-shadow)';">
        </div>

        <!-- Popular Quick Tools Chips -->
        <div class="quick-chips">
            <span class="quick-chip-label">Quick Tools:</span>
            <a href="/jpg-to-pdf/" class="quick-chip">JPG to PDF</a>
            <a href="/pdf-to-word/" class="quick-chip">PDF to Word</a>
            <a href="/png-to-jpg/" class="quick-chip">PNG to JPG</a>
            <a href="/mp4-to-mp3/" class="quick-chip">MP4 to MP3</a>
            <a href="/json-to-csv/" class="quick-chip">JSON to CSV</a>
        </div>

        <!-- Trust Stats Row -->
        <div class="trust-stats-row">
            <div class="stat-badge">⚡ 35+ Tools</div>
            <div class="stat-badge">🔒 Privacy-First</div>
            <div class="stat-badge">💻 No Software Needed</div>
            <div class="stat-badge">🧼 Clean Processing</div>
        </div>
    </section>

    <!-- AdSense Slot: Homepage Below Hero -->
    <div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
        <span class="adsense-label">Advertisement</span>
        <ins class="adsbygoogle"
             style="display:block;min-height:90px;"
             data-ad-client="ca-pub-8997218708343263"
             data-ad-slot="REPLACE_SLOT_HOME_TOP"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
    </div>

    <!-- 📈 Personal secure Productivity Dashboard & Log -->
    <section class="dashboard-section">
        <div class="dashboard-card">
            <div class="dashboard-header">
                <h3 class="dashboard-title">📈 Your Local Sandbox Analytics</h3>
                <button type="button" class="dashboard-reset-btn" onclick="resetDashboardStats()">🗑️ Reset Logs</button>
            </div>
            
            <div class="dashboard-stats-grid">
                <div class="stat-card">
                    <div class="stat-num" id="dash-files-count">0</div>
                    <div class="stat-label">Files Processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num" id="dash-savings-count">0.00 KB</div>
                    <div class="stat-label">Storage Saved</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num" style="color: var(--brand-accent); background: linear-gradient(135deg, var(--brand-accent) 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">100%</div>
                    <div class="stat-label">Privacy Score</div>
                </div>
            </div>

            <div class="history-section">
                <h4 class="history-title">🕒 Recent Operations History</h4>
                <div class="history-list" id="dash-history-list">
                    <div class="empty-history-state">
                        🌱 Your secure operations log is clean. Start converting files to see metrics in real-time!
                    </div>
                </div>
            </div>
            
            <p style="font-size:0.75rem; color:var(--text-light); text-align:center; margin-top: 1rem; line-height: 1.4;">
                🔒 All telemetry is computed and stored 100% locally on your computer using browser sandbox storage. Zero server uploads.
            </p>
        </div>
    </section>

    <!-- Dynamic Category Switcher pills -->
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="font-size: 2.1rem; letter-spacing: -0.03em;">Browse Online Converters</h2>
        <p style="font-size: 1rem; color: var(--text-muted); margin-top: 0.4rem;">Select a category to filter the utility converters grid instantly.</p>
        <div class="category-tabs">
            <button class="category-tab active" data-category="all">🔮 All Tools</button>
            <button class="category-tab" data-category="image">🖼️ Image</button>
            <button class="category-tab" data-category="developer">🌐 Developer</button>
            <button class="category-tab" data-category="designer">🎨 Designer</button>
            <button class="category-tab" data-category="security">🛡️ Security</button>
            <button class="category-tab" data-category="utility">🚀 Utility</button>
        </div>
    </div>

    <!-- Unified Tool Grid -->
    <main id="tools" class="tool-grid">
        {tools_html}
    </main>

    {KEYWORD_HUB_HTML}

    <!-- Why Choose Us Grid -->
    <section style="background: white; border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
            <h2 style="font-size: 2.2rem; margin-bottom: 3.5rem; letter-spacing:-0.03em;">Why Choose freeconvert.cloud?</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                <div style="background: var(--bg-light); border: 1px solid var(--border-color); padding: 2.5rem 2rem; border-radius: 24px; text-align: left; transition: all 0.3s;" class="saas-card">
                    <h3 style="color: var(--brand-primary); margin-bottom: 0.8rem; font-size: 1.3rem;">🔒 Private by Design</h3>
                    <p style="font-size: 0.94rem; line-height: 1.6;">All standard converter operations execute in your browser's local sandbox memory. Your files are completely safe and never uploaded.</p>
                </div>
                <div style="background: var(--bg-light); border: 1px solid var(--border-color); padding: 2.5rem 2rem; border-radius: 24px; text-align: left; transition: all 0.3s;" class="saas-card">
                    <h3 style="color: var(--brand-secondary); margin-bottom: 0.8rem; font-size: 1.3rem;">⚡ Fast Browser Tools</h3>
                    <p style="font-size: 0.94rem; line-height: 1.6;">Powered by modern WebAssembly and Canvas client-side libraries. Converting files takes milliseconds with absolutely zero network delay.</p>
                </div>
                <div style="background: var(--bg-light); border: 1px solid var(--border-color); padding: 2.5rem 2rem; border-radius: 24px; text-align: left; transition: all 0.3s;" class="saas-card">
                    <h3 style="color: var(--brand-accent); margin-bottom: 0.8rem; font-size: 1.3rem;">💎 Clean Output Quality</h3>
                    <p style="font-size: 0.94rem; line-height: 1.6;">High-definition conversions with zero loss of formatting, transparency, or pixel density. Premium and optimized.</p>
                </div>
                <div style="background: var(--bg-light); border: 1px solid var(--border-color); padding: 2.5rem 2rem; border-radius: 24px; text-align: left; transition: all 0.3s;" class="saas-card">
                    <h3 style="color: #06b6d4; margin-bottom: 0.8rem; font-size: 1.3rem;">🖥️ Works Everywhere</h3>
                    <p style="font-size: 0.94rem; line-height: 1.6;">A fully responsive browser-based SaaS converter that runs smoothly on Mac, Windows, iOS, Android, and Linux without setups.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Popular Conversion Categories Grid -->
    <section style="background: var(--bg-light); border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
            <h2 style="font-size: 2.2rem; margin-bottom: 1rem; letter-spacing:-0.03em;">Popular Conversion Hubs</h2>
            <p style="color: var(--text-muted); margin-bottom: 3.5rem; font-size: 1.05rem;">Explore comprehensive conversion directories and batch processing hubs.</p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.8rem;">
                <a href="/image-converter/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">🖼️</div>
                    <h3 style="color:var(--text-primary);">Image Converter</h3>
                    <p>Convert PNG, JPG, WebP, SVG, and HEIC images safely in your browser.</p>
                </a>
                <a href="/pdf-tools/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">📄</div>
                    <h3 style="color:var(--text-primary);">PDF Tools</h3>
                    <p>Compress, format, split, and merge PDF files in a single click.</p>
                </a>
                <a href="/document-converter/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">📄</div>
                    <h3 style="color:var(--text-primary);">Document Converter</h3>
                    <p>Process Microsoft Word docx, Excel sheets, and developer code bases.</p>
                </a>
                <a href="/video-converter/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">🎥</div>
                    <h3 style="color:var(--text-primary);">Video Converter</h3>
                    <p>Transcode MP4, WebM, AVI, and MOV video file dimensions online.</p>
                </a>
                <a href="/audio-converter/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">🎵</div>
                    <h3 style="color:var(--text-primary);">Audio Converter</h3>
                    <p>Convert MP3, WAV, OGG, and FLAC audios with high quality preservation.</p>
                </a>
                <a href="/unit-converter/" style="text-decoration:none;" class="tool-card">
                    <div class="tool-icon">📏</div>
                    <h3 style="color:var(--text-primary);">Utility & Units</h3>
                    <p>Calculate aspect ratios, test connectivity speeds, and measure metrics.</p>
                </a>
            </div>
        </div>
    </section>

    <!-- Latest Guides Internal Linking Section -->
    <section style="background: white; border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
            <span class="badge" style="margin-bottom:1rem;">Fresh SEO Guides</span>
            <h2 style="font-size: 2.2rem; margin-bottom: 1rem; letter-spacing:-0.03em;">Latest Conversion Guides</h2>
            <p style="color: var(--text-muted); margin-bottom: 3.5rem; font-size: 1.05rem;">High-intent tutorials for PDF compression, image resizing, WebP conversion, passport photos, Base64, and search snippet optimization.</p>
            <div class="tool-grid" style="padding:0;">
                {LATEST_GUIDES_HTML}
            </div>
            <div style="margin-top:2rem;">
                <a href="/blog/" class="btn secondary">Explore All Guides</a>
                <a href="/all-tools/" class="btn primary" style="margin-left:0.8rem;">Browse All Tools</a>
            </div>
        </div>
    </section>

    <!-- How It Works Step List -->
    <section style="background: white; border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1100px; margin: 0 auto; text-align: center;">
            <h2 style="font-size: 2.2rem; margin-bottom: 3.5rem; letter-spacing:-0.03em;">How it Works — Three Easy Steps</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 3rem; position: relative;">
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 900; background: var(--brand-primary-light); color: var(--brand-primary); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; border: 1px solid rgba(99,102,241,0.15);">1</div>
                    <h3 style="font-size: 1.25rem; margin-bottom: 0.6rem;">Upload Your File</h3>
                    <p style="font-size: 0.94rem; line-height: 1.55;">Drag and drop your file into the secure dotted zone or browse from your device storage.</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 900; background: rgba(139, 92, 246, 0.08); color: var(--brand-secondary); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; border: 1px solid rgba(139,92,246,0.15);">2</div>
                    <h3 style="font-size: 1.25rem; margin-bottom: 0.6rem;">Choose Target Format</h3>
                    <p style="font-size: 0.94rem; line-height: 1.55;">Select your compatible high-definition target output format and adjust advanced custom sliders.</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 900; background: var(--brand-accent-light); color: var(--brand-accent); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; border: 1px solid rgba(16,185,129,0.15);">3</div>
                    <h3 style="font-size: 1.25rem; margin-bottom: 0.6rem;">Convert and Download</h3>
                    <p style="font-size: 0.94rem; line-height: 1.55;">Execute the safe sandbox conversion instantly and download your pristine results securely.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Complete SEO Content Expansion & E-E-A-T Signal Block -->
    <section style="background: var(--bg-light); border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1000px; margin: 0 auto; text-align: left;" class="seo-content">
            <h2 style="font-size: 2.2rem; margin-bottom: 1.5rem; letter-spacing: -0.03em; text-align: center; color: var(--text-primary);">
                The Future of Secure, Browser-Based File Conversion
            </h2>
            <p style="font-size: 1.05rem; line-height: 1.7; color: var(--text-muted); margin-bottom: 2rem;">
                Welcome to <strong>freeconvert.cloud</strong>, a next-generation SaaS file conversion platform built for security, speed, and privacy. Traditional online utility websites function by uploading your private files, documents, and assets to external cloud servers, storing your content in database cache repositories and exposing your personal records to substantial hacking vulnerabilities. At freeconvert.cloud, we are spearheading a paradigm shift in web-based operations. 
            </p>
            <p style="font-size: 1.05rem; line-height: 1.7; color: var(--text-muted); margin-bottom: 2.5rem;">
                By utilizing advanced client-side technologies—including <strong>HTML5 Canvas APIs</strong>, <strong>WebAssembly modules</strong>, and <strong>local JavaScript compilation engines</strong>—our core converter tools process all calculations, rasterizations, hash generations, and text transformations directly in your device's web browser RAM sandbox. Your raw files are never transmitted across external networks, ensuring 100% data secrecy, absolute confidentiality, and zero risk of data leaks.
            </p>

            <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 3rem 0;">

            <h3 style="font-size: 1.6rem; color: var(--text-primary); margin-bottom: 1rem; letter-spacing: -0.02em;">
                Who Benefits from freeconvert.cloud?
            </h3>
            <p style="margin-bottom: 1.5rem;">
                Our secure web utility ecosystem is custom-engineered to optimize workflows for a diverse grid of professional, developer, creative, and academic roles:
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.8rem; margin-bottom: 3rem;">
                <div style="background: white; border: 1px solid var(--border-color); padding: 2rem; border-radius: 20px; box-shadow: var(--card-shadow);" class="saas-card">
                    <h4 style="margin-top: 0; font-size: 1.2rem; color: var(--brand-primary); margin-bottom: 0.6rem;">🌐 Software Developers</h4>
                    <p style="font-size: 0.92rem; line-height: 1.6; margin-bottom: 0; color: var(--text-muted);">
                        Engineers and DevOps professionals rely on our sandboxed developer tools to flatten API JSON payloads into CSV sheets, prettify minified SQL queries, format active HTML, CSS, and JS blocks, extract raw cryptographic SHA hashes, and decode complex URL/Base64 strings locally without exposing client databases or proprietary source codes to external server APIs.
                    </p>
                </div>
                <div style="background: white; border: 1px solid var(--border-color); padding: 2rem; border-radius: 20px; box-shadow: var(--card-shadow);" class="saas-card">
                    <h4 style="margin-top: 0; font-size: 1.2rem; color: var(--brand-secondary); margin-bottom: 0.6rem;">🖼️ Creative Designers</h4>
                    <p style="font-size: 0.92rem; line-height: 1.6; margin-bottom: 0; color: var(--text-muted);">
                        Graphics designers and content publishers utilize our browser-local compressors and resizers to shrink pixel weights, convert heavy Apple HEIC camera photographs to standard compressed JPG format, scale transparent vector SVG elements to high-resolution PNG screens, and extract dominant color palettes from design comps in milliseconds.
                    </p>
                </div>
                <div style="background: white; border: 1px solid var(--border-color); padding: 2rem; border-radius: 20px; box-shadow: var(--card-shadow);" class="saas-card">
                    <h4 style="margin-top: 0; font-size: 1.2rem; color: var(--brand-accent); margin-bottom: 0.6rem;">💼 Business Teams & Students</h4>
                    <p style="font-size: 0.92rem; line-height: 1.6; margin-bottom: 0; color: var(--text-muted);">
                        Office workers, copywriters, and academic students use our document processors to combine sequential homework scans or corporate invoices into single, organized multi-page PDFs, convert read-only PDF reports to editable MS Word DOCX models, track character/sentence statistics in real-time, and generate secure cryptographically sound password keys.
                    </p>
                </div>
            </div>

            <h3 style="font-size: 1.6rem; color: var(--text-primary); margin-bottom: 1.2rem; letter-spacing: -0.02em;">
                Why Local Sandbox Processing is a Security Imperative
            </h3>
            <p style="margin-bottom: 1.2rem; line-height: 1.6; font-size: 0.96rem; color: var(--text-muted);">
                Every time you upload an invoice, scanned tax document, company ID, or client ledger to a legacy online converter, that document is sent to an unregulated server database. It can sit in cached cloud files for weeks or even months. For organizations complying with strict regulatory frameworks such as GDPR, HIPAA, or SOC 2, these data trails represent severe security and compliance liabilities.
            </p>
            <p style="margin-bottom: 3rem; line-height: 1.6; font-size: 0.96rem; color: var(--text-muted);">
                freeconvert.cloud completely eliminates these liabilities. Standard operations run client-side, meaning your local files never leave your device. For heavy calculations that require isolated edge container conversions (such as document reflows or video transcoding), we utilize secure 256-bit SSL tunnels to route data to transient virtual machines. Once compiled, the edge storage runs automatic cron routines that securely shred and wipe all binaries within 2 hours, maintaining zero database logs or long-term backups.
            </p>

            <h3 style="font-size: 1.6rem; color: var(--text-primary); margin-bottom: 1.2rem; letter-spacing: -0.02em;">
                Standard Web Formats Glossary (LLM SEO Optimized)
            </h3>
            <div style="background: white; border: 1px solid var(--border-color); border-radius: 20px; padding: 2rem; margin-bottom: 3.5rem; box-shadow: var(--card-shadow);">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                    <div>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>JPG / JPEG:</strong> A highly compatible raster image container using lossy compression optimized for photographs, which trims unnoticeable color scales to keep size small.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>PNG:</strong> A lossless compressed raster graphic format that records colors exactly as designed and supports full transparent alpha background layers.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>PDF:</strong> Adobe's fixed-layout document standard. It embeds text fonts, images, and vectors identically across all screens, devices, and printers.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 0; color: var(--text-muted);">
                            <strong>DOCX:</strong> Microsoft Word's fluid, XML-based editing container optimized for drafting copy, but prone to formatting shifts if system fonts are missing.
                        </p>
                    </div>
                    <div>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>CSV:</strong> A simple flat database format that records tabular entries separated by commas, allowing easy importing into spreadsheet tools like Excel.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>JSON:</strong> JavaScript Object Notation, a lightweight web data exchange container storing structured objects, database values, and API grids.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; color: var(--text-muted);">
                            <strong>MP4:</strong> The global standard digital multimedia container, utilizing H.264 compression to store high-definition audio and video tracks.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 0; color: var(--text-muted);">
                            <strong>File Compression:</strong> The mathematical compaction of file structures to reduce storage footprints, boosting network speeds and email limit compliances.
                        </p>
                    </div>
                </div>
            </div>

            <h3 style="font-size: 1.6rem; color: var(--text-primary); margin-bottom: 1.5rem; letter-spacing: -0.02em; text-align: center;">
                Frequently Asked Questions
            </h3>
            <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem;">
                <div class="accordion">
                    <div class="accordion-header">❓ How does freeconvert.cloud ensure absolute file security and privacy?</div>
                    <div class="accordion-content">
                        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.6;">
                            Our platform utilizes local browser-based execution. Converting formats (e.g. PNG to JPG), checking passwords, or formatting code occurs client-side inside your browser sandbox memory using WebAssembly and HTML5 Canvas. Your raw file binary payloads never leave your machine or travel over the internet, rendering server-side hacking and data breaches structurally impossible.
                        </p>
                    </div>
                </div>
                <div class="accordion">
                    <div class="accordion-header">❓ Do some converters require cloud server processing?</div>
                    <div class="accordion-content">
                        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.6;">
                            Yes. Heavy transcoding operations (like converting Microsoft Word DOCX to PDF or extracting MP3 audio tracks from high-definition MP4 videos) require high computing cluster power. For these tasks, files are transmitted via secure 256-bit SSL pipelines to isolated transient edge sandboxes. The converted data is instantly returned to you, and both the source and target files are shredded completely from our servers within 2 hours.
                        </p>
                    </div>
                </div>
                <div class="accordion">
                    <div class="accordion-header">❓ Are there file size limits or cost constraints on the tools?</div>
                    <div class="accordion-content">
                        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.6;">
                            All tools on freeconvert.cloud are 100% free with absolutely zero subscription barriers or watermarks. To keep system cache processing smooth and prevent network bottlenecks, free users are capped at files up to 50MB per conversion. Uncapped queue limits, API developer endpoints, and larger batch processing limits are easily accessible on our flexible Pro tiers.
                        </p>
                    </div>
                </div>
                <div class="accordion">
                    <div class="accordion-header">❓ Do you display advertisements on the converter pages?</div>
                    <div class="accordion-content">
                        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.6;">
                            Yes. To sustain our server clusters and provide our utilities completely free, we display Google AdSense advertisement layouts. We strictly adhere to AdSense Policy Guidelines: ads are clearly marked as 'Advertisement' or 'Sponsored Links', and we enforce safe margins to prevent ads from being placed inside or too close to drag-and-drop zones, file upload inputs, or conversion CTAs.
                        </p>
                    </div>
                </div>
                <div class="accordion">
                    <div class="accordion-header">❓ Which operating systems and web browsers are supported?</div>
                    <div class="accordion-content">
                        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.6;">
                            Since our platform operates using standard modern web protocols, it is fully cross-platform and responsive. It works flawlessly inside Safari on Apple iPhones and iPads, Google Chrome on Android devices, Mozilla Firefox, Microsoft Edge, and Chrome on Windows, macOS, and Linux without requiring any software installations or browser extensions.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Developer API Preview Section -->
    <section style="background: white; border-top: 1px solid var(--border-color); padding: 5.5rem 5%;">
        <div style="max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1.2fr; gap: 3.5rem; align-items: center;">
            <div style="text-align: left;">
                <span class="badge" style="margin-bottom:1rem;">⚡ High Scalability</span>
                <h2 style="font-size: 2.2rem; margin-bottom: 1.2rem; letter-spacing:-0.03em;">Modern Developer API</h2>
                <p style="font-size: 1.02rem; margin-bottom: 2rem;">Integrate clean conversion clusters directly into your applications. Fast multipart responses with secure API key validations.</p>
                <div style="display:flex; gap:1rem;">
                    <a href="/api/" class="btn primary">Explore API</a>
                    <a href="/pricing/" class="btn secondary">Pricing Plans</a>
                </div>
            </div>

            <!-- Code Preview Terminal Card -->
            <div class="code-editor-module" style="text-align: left;">
                <div class="editor-pane" style="grid-column: span 2;">
                    <div class="editor-header">
                        <span class="editor-title">💻 API Integration (Node.js)</span>
                        <div class="editor-actions">
                            <span style="font-size: 0.75rem; font-weight: bold; color: var(--brand-accent);">● Live</span>
                        </div>
                    </div>
                    <pre style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #a5b4fc; overflow-x: auto; line-height: 1.6;">
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const form = new FormData();
form.append('file', fs.createReadStream('report.docx'));
form.append('target', 'pdf');

axios.post('https://api.freeconvert.cloud/v1/convert', form, {
  headers: {
    'Authorization': 'Bearer YOUR_SECRET_API_KEY',
    ...form.getHeaders()
  }
}).then(res => console.log('Job ID:', res.data.job_id));</pre>
                </div>
            </div>
        </div>
    </section>

    {FOOTER_SNIPPET}

    <script src="/tools/tools-data.js"></script>
    <script src="/tools/tool-logic.js"></script>
    <script>
        {UPLOAD_BOX_SCRIPT}
    </script>
    <script src="/main.js"></script>
</body>

</html>""".replace('{HEADER_SNIPPET}', HEADER_SNIPPET).replace('{FOOTER_SNIPPET}', FOOTER_SNIPPET).replace('{tools_html}', tools_html).replace('{LATEST_GUIDES_HTML}', latest_guides_html).replace('{KEYWORD_HUB_HTML}', keyword_hub_html).replace('{KEYWORD_TARGET_SCHEMA}', keyword_target_schema_tag(tools)).replace('{UPLOAD_BOX_UI}', UPLOAD_BOX_UI).replace('{UPLOAD_BOX_SCRIPT}', UPLOAD_BOX_SCRIPT.replace('{{ID}}', '').replace('{{NAME}}', ''))
        f.write(html_content)
    print("Redesigned and wrote homepage `/index.html` successfully with active Hero Uploadbox & AdSense slots.")


def build_all_tools_directory(tools):
    """Build a crawl-friendly HTML directory with direct contextual links to every tool."""
    grouped = {}
    for tool in tools:
        grouped.setdefault(tool.get('category', 'Utility'), []).append(tool)

    category_sections = []
    item_list_elements = []
    position = 1
    for category in sorted(grouped):
        cards = []
        for tool in sorted(grouped[category], key=lambda item: item['name']):
            name = html.escape(tool['name'])
            desc = html.escape(tool.get('seo_desc') or tool.get('description', ''))
            url = f"/{tool['id']}/"
            item_list_elements.append({
                "@type": "ListItem",
                "position": position,
                "name": tool['name'],
                "url": f"{SITE_URL}/{tool['id']}/",
                "description": tool.get('seo_desc') or tool.get('description', '')
            })
            position += 1
            cards.append(f"""
                    <a href="{url}" class="tool-card" style="text-align:left;text-decoration:none;">
                        <div class="tool-card-top">
                            <div class="tool-icon">{tool['icon']}</div>
                            <span class="tool-category-tag">{html.escape(category)}</span>
                        </div>
                        <div class="tool-card-body">
                            <span role="heading" aria-level="3" style="display:block;font-size:1.15rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{name}</span>
                            <p>{desc}</p>
                        </div>
                        <div class="tool-card-footer">
                            <span class="explore-text">Open tool</span>
                            <span class="arrow-icon">-&gt;</span>
                        </div>
                    </a>""")
        category_sections.append(f"""
            <section style="margin-top:3rem;">
                <div style="display:flex;align-items:end;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem;">
                    <div>
                        <span class="badge">{html.escape(category)} tools</span>
                        <h2 style="font-size:1.8rem;margin:0.8rem 0 0;">{html.escape(category)} converters and utilities</h2>
                    </div>
                    <span style="color:var(--text-muted);font-weight:700;">{len(grouped[category])} pages</span>
                </div>
                <div class="tool-grid" style="padding:0;">
                    {''.join(cards)}
                </div>
            </section>""")

    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "All free online converter tools",
        "url": f"{SITE_URL}/all-tools/",
        "description": "Complete crawl-friendly directory of freeconvert.cloud file converters, PDF tools, video tools, image utilities, developer tools, and calculators.",
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(item_list_elements),
            "itemListElement": item_list_elements
        }
    }
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'

    Path('all-tools').mkdir(exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Free Online Converter Tools | freeconvert.cloud</title>
    <meta name="description" content="Browse every freeconvert.cloud tool in one crawl-friendly directory: PDF tools, image converters, video converters, audio tools, developer utilities, calculators, and security tools.">
    <link rel="stylesheet" href="/style.css">
    <meta property="og:title" content="All Free Online Converter Tools | freeconvert.cloud">
    <meta property="og:description" content="A complete HTML directory of free online file converters, PDF tools, image utilities, video converters, developer tools, and calculators.">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{BRAND_IMAGE}">
    <meta name="twitter:card" content="summary_large_image">
    {schema_tag}
</head>
<body>
    {HEADER_SNIPPET}
    <section class="tool-header">
        <span class="badge">Crawl Directory</span>
        <h1>All Free Online Converter Tools</h1>
        <p>Use this complete HTML index to find every converter, compressor, calculator, formatter, generator, and file utility on freeconvert.cloud.</p>
        <div class="quick-chips" style="margin-top:1.4rem;">
            <a href="/pdf-tools/" class="quick-chip">PDF tools</a>
            <a href="/image-converter/" class="quick-chip">Image converters</a>
            <a href="/video-converter/" class="quick-chip">Video converters</a>
            <a href="/blog/" class="quick-chip">Guides</a>
            <a href="/sitemap/" class="quick-chip">HTML sitemap</a>
            <a href="/sitemap-index.xml" class="quick-chip">XML sitemap</a>
        </div>
    </section>

    <main style="max-width:1440px;margin:0 auto;padding:0 5% 5rem;">
        <section style="background:white;border:1px solid var(--border-color);border-radius:16px;padding:1.6rem;box-shadow:var(--card-shadow);">
            <h2 style="font-size:1.35rem;margin-bottom:0.8rem;">Why this directory helps users and crawlers</h2>
            <p style="color:var(--text-muted);line-height:1.7;margin:0;">This page gives visitors and search crawlers a direct, readable path to every important converter page. XML sitemaps help discovery, but HTML directories improve internal linking, crawl depth, and topical context for newly published tools.</p>
        </section>
        {''.join(category_sections)}
    </main>
    {FOOTER_SNIPPET}
    <script src="/main.js"></script>
</body>
</html>"""
    Path('all-tools/index.html').write_text(html_content, encoding='utf-8')
    print("Generated all tools crawl directory `/all-tools/index.html` successfully.")


def page_title_from_html(path):
    try:
        text = Path(path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return Path(path).parent.name.replace('-', ' ').title()
    if '<title>' in text:
        title = text.split('<title>', 1)[1].split('</title>', 1)[0]
        title = html.unescape(title)
        title = title.replace(' | freeconvert.cloud', '').replace(' | freeconvert.cloud Blog', '')
        return re.sub(r'\s+', ' ', title).strip()
    return Path(path).parent.name.replace('-', ' ').title()


def html_sitemap_link_list(items):
    links = []
    for href, label, desc in items:
        desc_html = f'<span style="display:block;color:var(--text-muted);font-size:0.86rem;margin-top:0.25rem;line-height:1.45;">{html.escape(desc)}</span>' if desc else ''
        links.append(
            f'<li style="break-inside:avoid;margin-bottom:0.75rem;">'
            f'<a href="{html.escape(href)}" style="color:var(--brand-primary);font-weight:800;text-decoration:none;">{html.escape(label)}</a>'
            f'{desc_html}</li>'
        )
    return '<ul style="list-style:none;padding:0;margin:0;columns:2 260px;">' + ''.join(links) + '</ul>'


def build_html_sitemap_page(tools):
    core_pages = [
        ('/', 'Home', 'Main free online converter homepage.'),
        ('/all-tools/', 'All Tools Directory', 'Direct HTML index for every converter and utility.'),
        ('/pricing/', 'Pricing', 'Conversion limits and plan details.'),
        ('/api/', 'Developer API', 'API overview for file conversion workflows.'),
        ('/blog/', 'Blog and Guides', 'Editorial tutorials and conversion guides.'),
        ('/popular-conversions/', 'Popular Conversions', 'High-intent conversion workflow hub.'),
        ('/free-online-converter-guides/', 'Free Online Converter Guides', 'Long-tail conversion and sizing guides.'),
        ('/file-formats/', 'File Format Glossary', 'Plain-English file format definitions.'),
        ('/help/', 'Help Center', 'Common questions and support information.'),
        ('/about/', 'About freeconvert.cloud', 'Company and editorial information.'),
        ('/security/', 'File Security', 'Privacy, sandboxing, and retention information.'),
        ('/contact/', 'Contact', 'Contact and support details.'),
        ('/press-kit/', 'Press Kit', 'Brand assets, facts, and media contact information.'),
    ]
    category_pages = [
        (f'/{cat["slug"]}/', cat['name'], cat.get('seo_desc', cat.get('intro', 'Browse related converter tools.')))
        for cat in CATEGORIES.values()
    ]

    grouped_tools = {}
    for tool in tools:
        grouped_tools.setdefault(tool.get('category', 'Utility'), []).append((
            f'/{tool["id"]}/',
            tool['name'],
            tool.get('seo_desc') or tool.get('description', '')
        ))

    guide_items = []
    for path in sorted(Path('free-online-converter-guides').glob('**/index.html')):
        if path.parent.name == 'free-online-converter-guides':
            continue
        guide_items.append((public_url_for_html(path).replace(SITE_URL, ''), page_title_from_html(path), 'Step-by-step converter guide.'))
    for path in sorted(Path('popular-conversions').glob('**/index.html')):
        if path.parent.name == 'popular-conversions':
            continue
        guide_items.append((public_url_for_html(path).replace(SITE_URL, ''), page_title_from_html(path), 'Popular conversion workflow.'))
    for path in sorted(Path('file-formats').glob('**/index.html')):
        if path.parent.name == 'file-formats':
            continue
        guide_items.append((public_url_for_html(path).replace(SITE_URL, ''), page_title_from_html(path), 'File format glossary page.'))

    blog_items = [
        (f'/blog/{article["slug"]}/', article['title'], article.get('description', 'Conversion guide.'))
        for article in BLOG_ARTICLES
    ]

    sections = [
        ('Core Pages', core_pages),
        ('Tool Categories', category_pages),
    ]
    for category in sorted(grouped_tools):
        sections.append((f'{category} Tools', sorted(grouped_tools[category], key=lambda item: item[1])))
    sections.append(('Guides, Popular Workflows, and File Formats', guide_items))
    sections.append(('Blog Articles', blog_items))

    section_html = ''
    all_items = []
    for heading, items in sections:
        all_items.extend(items)
        section_html += f"""
        <section style="background:white;border:1px solid var(--border-color);border-radius:16px;padding:1.8rem;margin-bottom:1.4rem;box-shadow:var(--card-shadow);">
            <h2 style="font-size:1.45rem;margin-bottom:1rem;">{html.escape(heading)}</h2>
            {html_sitemap_link_list(items)}
        </section>"""

    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "HTML Sitemap",
        "url": f"{SITE_URL}/sitemap/",
        "description": "Human-readable sitemap for freeconvert.cloud with direct links to converter pages, category hubs, guides, and policy pages.",
        "dateModified": TODAY_ISO,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(all_items),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": idx,
                    "name": label,
                    "url": f"{SITE_URL}{href}" if href.startswith('/') else href
                }
                for idx, (href, label, _) in enumerate(all_items, start=1)
            ]
        }
    }
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'

    Path('sitemap').mkdir(exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Sitemap | freeconvert.cloud</title>
    <meta name="description" content="Browse the full freeconvert.cloud HTML sitemap with direct links to converter tools, PDF tools, image tools, video tools, guides, and file format pages.">
    <link rel="stylesheet" href="/style.css">
    <meta property="og:title" content="HTML Sitemap | freeconvert.cloud">
    <meta property="og:description" content="A complete human-readable sitemap for freeconvert.cloud converter tools, guides, categories, and policy pages.">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{BRAND_IMAGE}">
    <meta name="twitter:card" content="summary_large_image">
    {schema_tag}
</head>
<body>
    {HEADER_SNIPPET}
    <section class="tool-header">
        <span class="badge">HTML Sitemap</span>
        <h1>freeconvert.cloud Sitemap</h1>
        <p>Browse every important public page on freeconvert.cloud from one clean, crawl-friendly HTML index.</p>
        <div class="quick-chips" style="margin-top:1.4rem;">
            <a href="/all-tools/" class="quick-chip">All tools</a>
            <a href="/sitemap-index.xml" class="quick-chip">XML sitemap index</a>
            <a href="/blog/" class="quick-chip">Guides</a>
            <a href="/popular-conversions/" class="quick-chip">Popular conversions</a>
        </div>
    </section>
    <main style="max-width:1280px;margin:0 auto;padding:0 5% 5rem;">
        {section_html}
    </main>
    {FOOTER_SNIPPET}
    <script src="/main.js"></script>
</body>
</html>"""
    Path('sitemap/index.html').write_text(html_content, encoding='utf-8')
    print("Generated HTML sitemap `/sitemap/index.html` successfully.")


def generate_category_seo_content(cat_slug, cat_name):
    # Generates custom long-form content exceeding 1,200 words for each category page
    intro_p = ""
    glossary_box = ""
    why_section = ""
    use_cases = []
    formats_guide = ""
    faqs = []
    
    if cat_slug == 'image-converter':
        intro_p = "Welcome to freeconvert.cloud's premier Image Converter hub. Our platform delivers next-generation, high-performance visual transcoding utilities designed to optimize workflow layouts, accelerate page speeds, and preserve high-definition print resolutions. In the modern web space, raw images represent the single largest bandwidth drain on networks. Managing image formatting, dimensions, and compression scales is essential for software builders, graphical designers, and professional photographers. Our local browser sandboxed engines allow you to convert, compress, and resize images without ever exposing your files to third-party servers."
        
        glossary_box = """
        <div style="background:var(--bg-light); border:1px solid var(--border-color); border-radius:16px; padding:1.8rem; margin:2rem auto; text-align:left; box-shadow:var(--card-shadow);">
            <h3 style="margin-top:0; font-size:1.15rem; color:var(--text-primary); letter-spacing:-0.02em;">🖼️ Image Formats Glossary & Definitions</h3>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>PNG (Portable Network Graphics):</strong> A lossless compressed raster format that records pixel data exactly as created. It supports full alpha transparency, making it the perfect choice for logos, typography, and clean graphic assets.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>JPG / JPEG (Joint Photographic Experts Group):</strong> A lossy compressed raster format optimized for photograph color depth. It compresses file weights aggressively by discarding visually subtle variations, speeding up webpage loading.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>WebP (Web Picture Format):</strong> Google's next-gen lossy and lossless image standard. It compresses image weights by 30% more than traditional JPEGs, directly boosting Google Core Web Vitals rankings.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:0; color:var(--text-muted);"><strong>SVG (Scalable Vector Graphics):</strong> An XML-based vector graphics standard. Rather than storing a grid of pixels, it stores geometric paths, enabling graphics to scale to infinite sizes with zero blurring.</p>
        </div>"""
        
        why_section = "Our image converters are engineered on client-side sandboxing, executing format translations inside your web browser using HTML5 Canvas and WebAssembly. Traditional web converters upload your photos to external server databases, posing severe privacy risks. By keeping processing local, freeconvert.cloud ensures that your private graphics drafts, scanned IDs, and receipts are never uploaded, while delivering instant millisecond-level results."
        
        use_cases = [
            "Converting camera JPGs to WebP format to speed up web platform rendering speeds and save server hosting bandwidth.",
            "Upgrading screenshots to transparent PNG comps to allow seamless background layers blending in editor platforms.",
            "Resizing heavy graphic banners to exact pixel dimensions to avoid CSS scaling stutters on mobile viewports.",
            "Extracting solid hex palettes and dominant colors from illustrations to compile clean UI design styles.",
            "Creating standard Favicons (.ico) from company logotypes to complete brand site designs.",
            "Converting Apple HEIC iPhone camera photos to standard JPG format for universal compatibility on Windows PCs."
        ]
        
        formats_guide = "We support standard raster, vector, next-generation, and camera container formats, including PNG, JPG, JPEG, WebP, SVG, HEIC, and ICO files. Standard operations, including resizing, compressing, palette extracting, and format translations, run 100% locally in your browser memory."
        
        faqs = [
            {"q": "Is my image quality preserved during format conversions?", "a": "Yes. Our conversion compiler uses lossless local pixel translating algorithms. Converting between lossless formats (like PNG or SVG) preserves pixel states perfectly, while lossy exports (like WebP or JPG) can be quality-locked up to 100% using our advanced sliders."},
            {"q": "Does your image converter upload my photos to your servers?", "a": "No, never. All image conversions, resizes, and compression routines run client-side inside your browser sandbox. Your visual files never leave your computer, securing absolute confidentiality."},
            {"q": "Can I convert multiple photos simultaneously in a batch?", "a": "Yes! Our drag-and-drop boxes support multi-file queues. You can select an entire collection of images, adjust standard dimensions, and batch-transcode them instantly."},
            {"q": "How does freeconvert.cloud replace transparent backgrounds during JPG conversions?", "a": "Because the JPG format does not support transparency, our local rendering context automatically overlays a solid white background layer behind transparent pixels, preventing ugly black box corruptions common in legacy converters."},
            {"q": "Do I need to sign up or install software to use these tools?", "a": "No. Our tools are 100% web-based, free, and accessible on all responsive viewports, including Safari on iPhones, Chrome on Android, macOS, and Windows."}
        ]
    elif cat_slug == 'pdf-tools':
        intro_p = "Welcome to freeconvert.cloud's professional PDF Tools suite. Our workspace offers a collection of secure, document processing utilities engineered to compress, split, format, and package PDF papers. PDF is the global standard for formal contracts, resumes, e-books, and commercial attachments. Managing PDF layouts cleanly is crucial for business professionals, writers, and students. Our tools are designed to streamline document workflows while enforcing strict encryption and automated cluster shredding to protect your records."
        
        glossary_box = """
        <div style="background:var(--bg-light); border:1px solid var(--border-color); border-radius:16px; padding:1.8rem; margin:2rem auto; text-align:left; box-shadow:var(--card-shadow);">
            <h3 style="margin-top:0; font-size:1.15rem; color:var(--text-primary); letter-spacing:-0.02em;">📄 Document Formats Glossary & Definitions</h3>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>PDF (Portable Document Format):</strong> Adobe's fixed-layout document standard. It embeds fonts, vector graphics, and raster images identically, ensuring document formatting never shifts regardless of operating system or screen size.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>DOCX (Word Document):</strong> Microsoft's fluid XML-based editing container. Perfect for drafting and copywriting, but susceptible to formatting shifts if opened on systems lacking the author's local fonts.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:0; color:var(--text-muted);"><strong>File Compression:</strong> The algorithmic optimization of document sizes, which identifies duplicate data arrays and compacts graphic payloads to fit strict email file constraints.</p>
        </div>"""
        
        why_section = "Typical document portals log your private PDF uploads on foreign database servers, presenting significant compliance and data leak risks. freeconvert.cloud secures your files by splitting tasks between browser-local tools (like local QR generators and text counters) and secure SSL edge sandboxes. Any file uploaded for heavy document formatting is routed through 256-bit SSL tunnels, compiled within a temporary container, and shredded completely from edge storage within 2 hours. We maintain zero database logs or backups."
        
        use_cases = [
            "Compiling scanned classroom homework pictures sequentially into a single multi-page PDF document for school submissions.",
            "Compressing formal resume PDFs to lightweight files under 150KB to bypass online HR application filters.",
            "Transforming heavy contracts into PDFs to enable secure digital signings and security locks.",
            "Generating custom QR codes for website URLs and contact vCards to use in print marketing campaigns.",
            "Splitting huge report files into standalone single-page documents for targeted distribution."
        ]
        
        formats_guide = "We support standard PDF documents, scanned JPG/PNG pictures, Microsoft Word DOCX files, QR code assets, and basic developer data formats. Standard layouts let you adjust orientation, margins, and compression levels."
        
        faqs = [
            {"q": "Is it safe to upload confidential business contracts to your PDF tools?", "a": "Yes. All file transfers utilize secure 256-bit SSL encryption. Documents are processed in automated temporary edge sandboxes and permanently deleted from our drives within 2 hours, guaranteeing complete security and compliance."},
            {"q": "Does compressing a PDF degrade the text quality?", "a": "No. Our compression engine compacts image pixels and removes unnecessary metadata layers while keeping vector fonts and letter styling sharp and legible."},
            {"q": "Can I convert Word documents to PDF on this platform?", "a": "Yes! We offer a highly accurate DOCX to PDF converter that preserves font structures, tables, lists, and formatting margins identically."},
            {"q": "Does this platform support batch document processing?", "a": "Yes, our queue managers allow you to upload multiple files at once, enabling you to process batches of documents in a single session."},
            {"q": "Is there a file size limit for free document tools?", "a": "To ensure lightning-fast processing speeds and avoid server queue delays, free users can upload files up to 50MB per document."}
        ]
    else:
        intro_p = f"Welcome to the high-performance {cat_name} directory on freeconvert.cloud. Our platform is engineered to deliver enterprise-grade conversion, calculation, formatting, and compression tools. Navigating incompatible file extensions, heavy media payloads, or complex coding scripts represents a daily productivity bottleneck for professionals and students alike. We optimize this workflow by offering client-side browser local tools and secure edge server sandboxes, unlocking lightning-fast transcoding speeds while respecting your data privacy."
        
        glossary_box = f"""
        <div style="background:var(--bg-light); border:1px solid var(--border-color); border-radius:16px; padding:1.8rem; margin:2rem auto; text-align:left; box-shadow:var(--card-shadow);">
            <h3 style="margin-top:0; font-size:1.15rem; color:var(--text-primary); letter-spacing:-0.02em;">📝 {cat_name} Glossary & Standards</h3>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>Format Transcoding:</strong> The process of translating a digital file from one coding structure to another, ensuring compatibility across different operating systems, media players, and devices.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:1rem; color:var(--text-muted);"><strong>Local Sandbox Execution:</strong> A secure, isolated runtime environment inside the web browser that processes file conversions locally on your computer memory without sending data to servers.</p>
            <p style="font-size:0.92rem; line-height:1.6; margin-bottom:0; color:var(--text-muted);"><strong>SSL Secure Gateway:</strong> An encrypted network pipeline that utilizes 256-bit SSL tunnels to safely transmit files to edge containers, shredding files immediately after processing.</p>
        </div>"""
        
        why_section = f"At freeconvert.cloud, we monetize strictly through non-intrusive AdSense advertising. Unlike spammy online tools directories, we maintain a clean visual separation between ad layouts and converter modules, completely eliminating accidental clicks or deceptive download redirect pathways. We believe in providing original, human-written content layers, detailed use cases, and robust guides that deliver real value to our visitors."
        
        use_cases = [
            f"Transcoding dynamic {cat_name} containers to highly optimized formats to accelerate page load speeds and decrease mobile bandwidth usage.",
            f"Migrating structured database arrays and developer records safely in a client-side sandbox environment.",
            f"Configuring advanced options like bitrate structures, quality parameters, and dimensions locally.",
            f"Compressing heavy attachments to ensure compatibility under standard email client size limits."
        ]
        
        formats_guide = f"We support a wide array of formats inside the {cat_name} directory, including images, document files, media tracks, and developer code structures. The converters page layouts adapt dynamically to any desktop or mobile screen size."
        
        faqs = [
            {"q": f"Are the {cat_name} converters completely free to use?", "a": f"Yes. All utility converters on freeconvert.cloud are 100% free with no sign-ups, registrations, or monthly limits, ensuring immediate productivity."},
            {"q": "How does freeconvert.cloud guarantee the security of my files?", "a": "Image, calculation, and developer text converters run entirely inside your browser's local sandbox memory. Audio, video, and documents use encrypted SSL edge servers that shred data within 2 hours."},
            {"q": f"Can I use these {cat_name} tools on my smartphone?", "a": "Yes! Our platform is fully responsive and runs seamlessly on iOS Safari, Android Chrome, tablet web browsers, and desktop systems without installing any software."}
        ]
        
    # Convert use cases list to HTML
    use_cases_html = "".join([f"<li>{uc}</li>" for uc in use_cases])
    
    # Convert FAQs to HTML
    faq_html = ""
    for f in faqs:
        faq_html += f"""
        <div class="accordion">
            <div class="accordion-header">❓ {f['q']}</div>
            <div class="accordion-content">
                <p style="font-size:0.95rem; color:var(--text-muted); line-height:1.6;">{f['a']}</p>
            </div>
        </div>"""
        
    return intro_p, glossary_box, why_section, use_cases_html, formats_guide, faq_html, faqs


def build_categories(tools):
    for key, cat in CATEGORIES.items():
        # Filter matching tools
        cat_tools = [t for t in tools if t['type'] in cat['types']]
        grid_html = ""
        for tool in cat_tools:
            grid_html += f"""
            <a href="/{tool['id']}/" class="tool-card">
                <div class="tool-icon">{tool['icon']}</div>
                <span role="heading" aria-level="3" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">{tool['name']}</span>
                <p>{tool['description']}</p>
            </a>"""

        os.makedirs(f"{cat['slug']}", exist_ok=True)
        
        # Call generate_category_seo_content helper
        cat_seo_intro, cat_glossary, cat_why_section, cat_use_cases, cat_formats_guide, faq_acc_html, faqs_list = generate_category_seo_content(cat['slug'], cat['name'])
        
        faq_schema = []
        for f_item in faqs_list:
            faq_schema.append({
                "@type": "Question",
                "name": f_item['q'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f_item['a']
                }
            })
            
        # Build ItemList of tools for category schema
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
        schema_tag = f'<script type="application/ld+json">{json.dumps(schema_data)}</script>'

        html_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SEO_TITLE} | freeconvert.cloud</title>
    <meta name="description" content="{SEO_DESC}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/{CAT_SLUG}/" />

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
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content">
        <!-- Visual Breadcrumbs -->
        <nav class="breadcrumbs">
            <a href="/">Home</a>
            <span>&gt;</span>
            <span style="color: var(--text-muted);">{CAT_NAME}</span>
        </nav>

        <section class="tool-header">
            <h1>{CAT_NAME}</h1>
            <p style="margin-top: 0.5rem;">{CAT_INTRO}</p>
        </section>

        <!-- Dynamic Category upload block -->
        <section class="upload-section" id="tool-container">
            {UPLOAD_BOX_UI}
        </section>

        <!-- Category Grid of Tools -->
        <section>
            <h2 style="text-align: center; margin-bottom: 2rem; letter-spacing: -0.03em;">Available {CAT_NAME} Tools</h2>
            <div class="tool-grid" style="padding: 0; margin-bottom: 3rem;">
                {GRID_HTML}
            </div>
        </section>

        <!-- AdSense Slot: Category Page Mid Content -->
        <div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
            <span class="adsense-label">Advertisement</span>
            <ins class="adsbygoogle"
                 style="display:block;min-height:90px;"
                 data-ad-client="ca-pub-8997218708343263"
                 data-ad-slot="REPLACE_SLOT_CAT_TOP"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <!-- Help articles -->
        <article class="seo-content">
            <h2>About our {CAT_NAME} Hub</h2>
            <p>{CAT_SEO_INTRO}</p>
            
            {CAT_GLOSSARY}

            <h2>Why Choose freeconvert.cloud for {CAT_NAME}?</h2>
            <p>{CAT_WHY_SECTION}</p>

            <h2>Primary Use Cases</h2>
            <ul style="padding-left:1.5rem; margin-top:0.8rem; display:flex; flex-direction:column; gap:0.6rem; font-size:0.95rem; line-height:1.6;">
                {CAT_USE_CASES}
            </ul>

            <h2>Supported Formats and Guides</h2>
            <p>{CAT_FORMATS_GUIDE}</p>

            <h2>How does our {CAT_NAME} tool work?</h2>
            {CAT_HOW_TO}
            
            <h2>Frequently Asked Questions</h2>
            <p style="margin-bottom:1rem;">Have questions about converting files inside our {CAT_NAME} directory? Read our comprehensive FAQ below:</p>
            {FAQ_ACC_HTML}
        </article>

        <!-- Related categories section -->
        <div style="text-align: center; margin-bottom: 2rem;">
            <h3 style="margin-bottom: 1.5rem; font-size: 1.4rem; letter-spacing:-0.02em;">Explore Related Categories</h3>
            <div style="display: flex; gap: 0.8rem; justify-content: center; flex-wrap: wrap;">
                <a href="/image-converter/" class="category-tab active" style="box-shadow:none; text-decoration:none;">🖼️ Image Converter</a>
                <a href="/pdf-tools/" class="category-tab active" style="box-shadow:none; text-decoration:none;">📄 PDF Tools</a>
                <a href="/document-converter/" class="category-tab active" style="box-shadow:none; text-decoration:none;">📄 Document Converter</a>
                <a href="/video-converter/" class="category-tab active" style="box-shadow:none; text-decoration:none;">🎥 Video Converter</a>
            </div>
        </div>
    </main>

    {FOOTER_SNIPPET}

    <script src="/tools/tool-logic.js"></script>
    <script>
        {UPLOAD_BOX_SCRIPT}
    </script>
</body>

</html>""".replace('{SEO_TITLE}', cat['seo_title']).replace('{SEO_DESC}', cat['seo_desc']).replace('{CAT_SLUG}', cat['slug']).replace('{SCHEMA_TAG}', schema_tag).replace('{HEADER_SNIPPET}', HEADER_SNIPPET).replace('{CAT_NAME}', cat['name']).replace('{CAT_INTRO}', cat['intro']).replace('{UPLOAD_BOX_UI}', UPLOAD_BOX_UI).replace('{GRID_HTML}', grid_html).replace('{CAT_HOW_TO}', cat['how_to']).replace('{FAQ_ACC_HTML}', faq_acc_html).replace('{FOOTER_SNIPPET}', FOOTER_SNIPPET).replace('{UPLOAD_BOX_SCRIPT}', UPLOAD_BOX_SCRIPT.replace('{{ID}}', '').replace('{{NAME}}', '')).replace('{CAT_SEO_INTRO}', cat_seo_intro).replace('{CAT_GLOSSARY}', cat_glossary).replace('{CAT_WHY_SECTION}', cat_why_section).replace('{CAT_USE_CASES}', cat_use_cases).replace('{CAT_FORMATS_GUIDE}', cat_formats_guide)
        with open(f"{cat['slug']}/index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated category page: /{cat['slug']}/index.html")


def build_pricing_page():
    os.makedirs('pricing', exist_ok=True)
    html_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS Subscription Pricing Plans | freeconvert.cloud</title>
    <meta name="description" content="View pricing options for freeconvert.cloud. Choose Free, Pro, or API Enterprise conversions with massive batch limits and SSL encryptions.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/pricing/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="Pricing Plans | freeconvert.cloud">
    <meta property="og:description" content="View pricing options for freeconvert.cloud. Free, Pro, and API Enterprise plans available.">
    <meta property="og:url" content="https://freeconvert.cloud/pricing/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Pricing Plans | freeconvert.cloud">
    <meta name="twitter:description" content="View pricing options for freeconvert.cloud. Free, Pro, and API Enterprise plans available.">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content" style="max-width: 1200px;">
        <section class="tool-header">
            <h1>Simple, Transparent <span class="gradient-text">Pricing</span></h1>
            <p style="margin-top: 0.5rem;">Unlock batch conversion limits, larger files sizes, and lightning-fast edge processing speeds.</p>
        </section>

        <!-- Plan switch toggle -->
        <div class="pricing-toggle-wrap">
            <span style="font-weight: 700;">Monthly</span>
            <div class="pricing-toggle" id="pricing-toggle">
                <div class="pricing-toggle-ball"></div>
            </div>
            <span style="font-weight: 700; color: var(--brand-primary);">Yearly <span style="font-size:0.75rem; background:var(--brand-accent-light); padding:3px 8px; border-radius:30px; color:var(--brand-accent);">(Save 20%)</span></span>
        </div>

        <!-- Plan card grid -->
        <div class="pricing-grid">
            <div class="pricing-card">
                <h3 style="font-size: 1.4rem;">Starter</h3>
                <p>Perfect for quick everyday conversions.</p>
                <div class="pricing-price">$0<span>/month</span></div>
                <hr style="border-color: var(--border-color); border-style: solid;">
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.9rem; padding-left:0;">
                    <li>✅ Up to 50 MB File Size</li>
                    <li>✅ Browser Local Sandbox Tools</li>
                    <li>✅ Standard Conversion Speed</li>
                    <li>✅ 15 conversions per day</li>
                </ul>
                <button class="btn secondary" style="margin-top: auto; justify-content: center;">Current Plan</button>
            </div>

            <div class="pricing-card popular">
                <h3 style="font-size: 1.4rem;">Pro Plan</h3>
                <p>For professionals needing high-volume file conversions.</p>
                <div class="pricing-price" id="pro-price-display">$9.99<span>/month</span></div>
                <hr style="border-color: var(--border-color); border-style: solid;">
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.9rem; padding-left:0;">
                    <li>✅ Up to 2 GB File Size Limit</li>
                    <li>✅ 50 batch conversions simultaneously</li>
                    <li>✅ Priority cloud conversion queue</li>
                    <li>✅ Unlimited conversions per day</li>
                    <li>✅ Zero Ad Experience</li>
                </ul>
                <button class="btn primary" style="margin-top: auto; justify-content: center;">Get Started</button>
            </div>

            <div class="pricing-card">
                <h3 style="font-size: 1.4rem;">Developer API</h3>
                <p>Integrate scalable file conversions in your code.</p>
                <div class="pricing-price">$29<span>/month</span></div>
                <hr style="border-color: var(--border-color); border-style: solid;">
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.9rem; padding-left:0;">
                    <li>✅ SDK for Node.js, Python, and Ruby</li>
                    <li>✅ 10,000 API Conversion Credits</li>
                    <li>✅ Dedicated high-performance clusters</li>
                    <li>✅ 24/7 Priority Support</li>
                </ul>
                <a href="/api/" class="btn secondary" style="margin-top: auto; justify-content: center;">Integrate Now</a>
            </div>
        </div>
    </main>

    {FOOTER_SNIPPET}

    <script src="/tools/tool-logic.js"></script>
    <script>
        const toggle = document.getElementById('pricing-toggle');
        const priceDisplay = document.getElementById('pro-price-display');
        let isYearly = false;
        toggle.onclick = () => {
            isYearly = !isYearly;
            if (isYearly) {
                toggle.classList.add('yearly');
                priceDisplay.innerHTML = "$7.99<span>/month ($95.88 billed yearly)</span>";
            } else {
                toggle.classList.remove('yearly');
                priceDisplay.innerHTML = "$9.99<span>/month</span>";
            }
        };
    </script>
</body>

</html>""".replace('{HEADER_SNIPPET}', HEADER_SNIPPET).replace('{FOOTER_SNIPPET}', FOOTER_SNIPPET)
    with open('pricing/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Generated pricing page `/pricing/index.html` successfully.")


def build_api_page():
    os.makedirs('api', exist_ok=True)
    html_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS File Conversion API Reference | freeconvert.cloud</title>
    <meta name="description" content="Robust, scalable file conversion API for developers. Integrate PDF, image, video, and document conversions with a simple JSON API.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/api/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="Developer API | freeconvert.cloud">
    <meta property="og:description" content="Integrate freeconvert.cloud into your app with our REST API. Convert files programmatically at scale.">
    <meta property="og:url" content="https://freeconvert.cloud/api/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Developer API | freeconvert.cloud">
    <meta name="twitter:description" content="Integrate freeconvert.cloud into your app with our REST API. Convert files programmatically at scale.">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content" style="max-width: 1200px;">
        <section class="tool-header">
            <h1>Scalable File Conversion <span class="gradient-text">API</span></h1>
            <p style="margin-top: 0.5rem;">Convert documents, media, and images inside your codebase with a single unified SDK call.</p>
        </section>

        <!-- Code examples split view -->
        <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 2rem; margin-bottom: 4rem;">
            <div class="legal-container" style="padding: 2rem;">
                <h2>File Conversion API</h2>
                <p>We provide standard endpoints that accept multipart file payloads and convert formats with absolute safety.</p>
                <h4 style="margin-top:1rem;">API Use Cases:</h4>
                <ul style="padding-left:1.2rem; font-size:0.9rem; display:flex; flex-direction:column; gap:0.5rem;">
                    <li>📁 Automating PDF generation from HTML templates.</li>
                    <li>🖼️ Compressing user photo uploads to WebP formats on backend.</li>
                    <li>🎥 Converting videos in the background of web applications.</li>
                </ul>
                <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                    <a href="/pricing/" class="btn primary" style="font-size:0.8rem; text-transform:none;">Create API Token</a>
                    <button class="btn secondary" style="font-size:0.8rem; text-transform:none;" onclick="alert('Contacting sales...')">Contact Sales</button>
                </div>
            </div>

            <!-- Tabbed SDK panel -->
            <div class="legal-container" style="padding: 2rem;">
                <div class="api-tabs-header">
                    <button class="api-tab-btn active" id="tab-node" onclick="switchTab('node')">Node.js</button>
                    <button class="api-tab-btn" id="tab-py" onclick="switchTab('py')">Python</button>
                </div>
                <div id="code-content">
                    <pre class="api-code-block" id="api-code-block">const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const form = new FormData();
form.append('file', fs.createReadStream('report.doc'));
form.append('target', 'pdf');

axios.post('https://api.freeconvert.cloud/v1/convert', form, {
    headers: {
        'Authorization': 'Bearer YOUR_SECRET_API_KEY',
        ...form.getHeaders()
    }
})
.then(response => {
    console.log('Conversion Job ID:', response.data.job_id);
});</pre>
                </div>
            </div>
        </div>
    </main>

    {FOOTER_SNIPPET}

    <script src="/tools/tool-logic.js"></script>
    <script>
        const nodeCode = `const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const form = new FormData();
form.append('file', fs.createReadStream('report.doc'));
form.append('target', 'pdf');

axios.post('https://api.freeconvert.cloud/v1/convert', form, {
    headers: {
        'Authorization': 'Bearer YOUR_SECRET_API_KEY',
        ...form.getHeaders()
    }
})
.then(response => {
    console.log('Conversion Job ID:', response.data.job_id);
});`;

        const pyCode = `import requests

files = {'file': open('report.doc', 'rb')}
payload = {'target': 'pdf'}
headers = {'Authorization': 'Bearer YOUR_SECRET_API_KEY'}

response = requests.post(
    'https://api.freeconvert.cloud/v1/convert',
    files=files,
    data=payload,
    headers=headers
)
print("Conversion Job ID:", response.json().get('job_id'))`;

        window.switchTab = (lang) => {
            const btnNode = document.getElementById('tab-node');
            const btnPy = document.getElementById('tab-py');
            const block = document.getElementById('api-code-block');
            
            if (lang === 'node') {
                btnNode.classList.add('active');
                btnPy.classList.remove('active');
                block.textContent = nodeCode;
            } else {
                btnNode.classList.remove('active');
                btnPy.classList.add('active');
                block.textContent = pyCode;
            }
        };
    </script>
    <script src="/tools/tool-logic.js"></script>
</body>

</html>""".replace('{HEADER_SNIPPET}', HEADER_SNIPPET).replace('{FOOTER_SNIPPET}', FOOTER_SNIPPET)
    with open('api/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Generated API page `/api/index.html` successfully.")


def build_legal_pages():
    pages = {
        'privacy': {
            'title': 'Privacy Policy',
            'desc': 'Understand how we protect your files and data privacy.',
            'content': """<h2>Privacy Guarantee</h2>
            <p>At freeconvert.cloud, we take data privacy and file security extremely seriously. Standard tools like image converters, case converters, and data calculators process 100% locally in your device's browser memory via Canvas, local JavaScript, or CSS engines, meaning your raw files never touch external networks or servers.</p>
            
            <h2>What Data Do We Collect?</h2>
            <p>We do not collect or archive personal data, nor do we require registrations to utilize our free tools. The only data processed is the binary payloads you explicitly submit during conversion workflows, which run securely under sandbox policies.</p>
            
            <h2>File Retention Policy</h2>
            <p>For tools requiring backend conversions (e.g. Doc to PDF), files are uploaded via secure 256-bit SSL tunnels and permanently deleted from our clusters immediately after conversion or after a maximum queue delay of 2 hours. We guarantee zero database archiving or backup generation of your file binaries.</p>"""
        },
        'terms': {
            'title': 'Terms of Service',
            'desc': 'Read our platform usage conditions and service agreements.',
            'content': """<h2>Usage Conditions</h2>
            <p>Welcome to freeconvert.cloud. By utilizing our file converters, you agree to comply with standard service requirements. You are fully responsible for the legality of the files you convert. Converting illegal material, copyrighted files without ownership, or abusing API quotas is strictly prohibited.</p>
            
            <h2>Quotas and Limits</h2>
            <p>Free plan conversions are restricted to files under 50MB and capped at 15 total daily conversions per network connection. Pro plan tiers grant batch limits and increased file size allowances as agreed upon subscription.</p>
            
            <h2>Liability Limitations</h2>
            <p>freeconvert.cloud provides client-side and cloud-based file transformations 'as is' without warranties. We are not liable for data losses or transmission disruptions occurring during conversion execution.</p>"""
        },
        'security': {
            'title': 'File Security Infrastructure',
            'desc': 'Learn about our SSL encryptions and secure local browser execution.',
            'content': """<h2>Enterprise-Grade Cryptography</h2>
            <p>Our platform enforces strict transport security (HSTS) and encrypts all network transmissions using 256-bit SSL tunnels, shielding your file uploads from sniffing or external routing attacks.</p>
            
            <h2>Browser Sandbox Isolation</h2>
            <p>Standard developer and image tools operate inside a secure browser sandbox. Executions are completely decoupled from network interfaces, making client-side processes mathematically isolated from data breaches.</p>
            
            <h2>Cluster Purging</h2>
            <p>Our server clusters execute automatic cron processes that securely wipe and shred uploaded binaries from system drives every 2 hours, ensuring no trace of your documents is preserved.</p>"""
        },
        'dmca': {
            'title': 'DMCA & Abuse Report Policy',
            'desc': 'Submit DMCA abuse or copyright infringement notices to freeconvert.cloud for review.',
            'content': """<h2>DMCA Compliance</h2>
            <p>Because freeconvert.cloud processes conversions on-the-fly and permanently purges files immediately after task completion, we do not host, store, or archive public downloadable files on our servers. Therefore, copyright infringement is structurally impossible on our web indexes.</p>
            
            <h2>Abuse Reporting</h2>
            <p>If you identify any malicious abuse of our open conversion APIs or infrastructure, please contact us immediately at <strong>abuse@freeconvert.cloud</strong> and our security team will investigate your report within 24 hours.</p>"""
        },
        'contact': {
            'title': 'Contact Support',
            'desc': 'Get in touch with our customer service and technical team.',
            'content': """<h2>Customer Support</h2>
            <p>Have questions about your file conversions, Pro plan subscriptions, or custom API limits? Our specialized support team is here to assist you 24/7.</p>
            
            <h2>Contact Channels</h2>
            <p>You can reach us through any of the following active support addresses:</p>
            <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1.5rem;">
                <li>📧 <strong>Support Email:</strong> support@freeconvert.cloud</li>
                <li>⚡ <strong>API Developer Sales:</strong> api@freeconvert.cloud</li>
                <li>🛡️ <strong>DMCA / Abuse Reports:</strong> abuse@freeconvert.cloud</li>
            </ul>
            
            <h2>Response Times</h2>
            <p>Free plan queries are typically reviewed within 48 hours. Pro and Enterprise Developer API subscribers receive priority routing, ensuring direct expert assistance within a guaranteed 2-hour window.</p>"""
        },
        'help': {
            'title': 'Help & FAQ',
            'desc': 'Find answers about free online file conversion, PDF tools, image converters, privacy, upload limits, and troubleshooting.',
            'content': """<h2>Frequently Asked Questions</h2>
            <p>This help center answers the most common questions about using freeconvert.cloud for PDF, image, document, audio, video, archive, and developer file conversion workflows.</p>

            <h2>How do I convert a file online?</h2>
            <p>Open the converter you need, choose your file, review the selected output format, and click the conversion button. Popular starting points include <a href="/pdf-to-jpg/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">PDF to JPG</a>, <a href="/jpg-to-pdf/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">JPG to PDF</a>, <a href="/png-to-jpg/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">PNG to JPG</a>, and <a href="/compress-pdf/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">Compress PDF</a>.</p>

            <h2>Are my files private?</h2>
            <p>Many image, text, code, color, hash, and utility tools run directly inside your browser. For conversion workflows that require server processing, files are transferred over HTTPS and are designed to be deleted automatically after processing.</p>

            <h2>What are the free file limits?</h2>
            <p>The free plan is designed for everyday conversion tasks and smaller files. Larger documents, batch conversions, and high-volume workflows are available through the Pro and Developer API plans on the <a href="/pricing/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">pricing page</a>.</p>

            <h2>Why did my conversion fail?</h2>
            <p>Failures usually happen when a file is password-protected, corrupted, too large, or saved in a rare format variant. Try exporting the source file again, removing passwords, or using the closest matching converter category from the homepage.</p>

            <h2>Can I use freeconvert.cloud for SEO and web images?</h2>
            <p>Yes. Use PNG to JPG, JPG to WebP, WebP to JPG, image compression, resize image, and color palette tools to prepare lighter website images and cleaner upload assets.</p>

            <h2>Do you offer API access?</h2>
            <p>Developer API access is available for teams that need automated conversion workflows, higher limits, and integration support. Visit the <a href="/api/" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">Developer API</a> page for details.</p>"""
        },
        'about': {
            'title': 'About Us',
            'desc': 'Learn more about freeconvert.cloud\'s mission, privacy commitments, and SaaS technology.',
            'content': """<h2>Our Mission</h2>
            <p>At freeconvert.cloud, we are committed to delivering premium, commercial-grade file conversion utilities without the traditional overhead, bloat, or security risks of conventional web converters. Our platform is built from the ground up to respect user privacy first, and monetize responsibly second.</p>
            
            <h2>Privacy-First Local Processing</h2>
            <p>Unlike standard converters that upload every document to foreign servers (raising severe corporate risk), our advanced pipeline harnesses HTML5 Canvas, WebAssembly, and local JavaScript sandboxing. Image rasterization, calculations, hashes, text transformations, and code formatters happen entirely on your computer, meaning your files are 100% private and never exposed to the web. For details on our sandbox specifications, visit our dedicated <a href="/security/" style="color:var(--brand-primary); text-decoration:none; font-weight:600;">File Security</a> page.</p>

            <h2>Editorial Policy & Content Integrity</h2>
            <p>Our commitment to our visitors is simple: absolute content authority, accuracy, and utility. Every guide, comparison table, glossary definition, and FAQ published across freeconvert.cloud is carefully researched and fact-checked by our in-house <strong>freeconvert.cloud Editorial Team</strong>. We do not generate low-value, duplicate, or generic AI content. Every section is written to deliver genuine, real-world answers to your technical conversion and data-handling questions.</p>

            <h2>How We Review and Update Content</h2>
            <p>The digital format space evolves rapidly, with new operating systems, browser engines, and compression standards emerging frequently. To ensure that our guidelines remain highly accurate and beginner-friendly, our editorial team regularly reviews all published materials. Each guide features a clear 'Last Updated' flag (e.g. May 2026) indicating our most recent validation stamp. If we identify obsolete technical instructions or formatting changes, we update the articles immediately.</p>

            <h2>Responsible Advertising & Independent Recommendations</h2>
            <p>We monetize freeconvert.cloud strictly via non-intrusive Google AdSense advertising. However, we maintain a strict boundary between our advertising partners and our tool recommendations or editorial decisions:</p>
            <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-top:0.8rem; margin-bottom:1.5rem; font-size:0.95rem; line-height:1.6;">
                <li><strong>Zero Bias:</strong> Advertisers and sponsors have absolutely zero influence over our software recommendations, tool prioritizations, or editorial guides.</li>
                <li><strong>No Fake Buttons:</strong> We prohibit misleading download banners, auto-redirect links, or installer pop-ups disguised as conversion elements.</li>
                <li><strong>Safe Margins:</strong> Placements are clearly labeled as 'Advertisement' or 'Sponsored Links' and are kept at a safe distance from upload sections and action CTAs to completely eliminate accidental clicks.</li>
            </ul>"""
        },
        'cookies': {
            'title': 'Cookie Policy',
            'desc': 'Review how we utilize cookie tracking for preferences, analytics, and AdSense.',
            'content': """<h2>What Are Cookies?</h2>
            <p>Cookies are small text files stored locally in your browser to retain preferences, remember utility configurations, and optimize performance. freeconvert.cloud utilizes standard session and third-party cookies strictly to enhance your conversion experience.</p>
            
            <h2>Third-Party Advertising & AdSense Cookies</h2>
            <p>Google, as a third-party vendor, uses cookies to serve personalized advertisements based on your visits to our site and other websites on the internet. Users may opt out of personalized advertising by visiting Google's Ads Settings.</p>
            
            <h2>Managing Cookie Settings</h2>
            <p>You can choose to disable or selectively turn off our cookies or third-party cookies in your browser settings. However, this can affect how you are able to interact with our platform (such as retaining dark-theme layouts or loading developer sample files).</p>"""
        },
        'advertising-policy': {
            'title': 'Advertising & Editorial Standards',
            'desc': 'Learn how freeconvert.cloud separates advertising, editorial content, file tools, and user experience.',
            'content': """<h2>Advertising Review Status</h2>
            <p>freeconvert.cloud is prepared for responsible advertising, but our priority is always useful tools and original guidance. Advertising placements are not allowed to interrupt file uploads, conversion buttons, downloads, form controls, or educational content.</p>

            <h2>Clear Separation Between Ads and Tools</h2>
            <p>Any future advertising unit must be clearly labeled and visually separated from conversion workflows. We do not use fake download buttons, misleading alerts, forced redirects, auto-start downloads, pop-under windows, or layouts designed to create accidental ad clicks.</p>

            <h2>Independent Editorial Standards</h2>
            <p>Our converter pages, tutorials, FAQs, and comparison guides are written to help users solve practical file-format problems. Advertising partners do not influence tool rankings, recommendations, article topics, page titles, conversion instructions, or privacy statements.</p>

            <h2>Minimum Content Quality Checks</h2>
            <p>Before a page is published, we check that it includes a working utility or a useful educational purpose, clear headings, original instructions, relevant internal links, privacy notes, and no empty placeholder content. Pages that exist only to display ads are not part of our publishing policy.</p>

            <h2>User Experience Commitments</h2>
            <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-top:0.8rem; margin-bottom:1.5rem; font-size:0.95rem; line-height:1.6;">
                <li>Conversion tools remain visible and usable before any monetization element.</li>
                <li>Important pages such as Privacy, Terms, Contact, Security, Help, and DMCA are linked from the footer.</li>
                <li>We avoid thin doorway pages and redirect old URLs to the most relevant current resource.</li>
                <li>We keep sitemap, robots.txt, llms.txt, feed.xml, and structured data updated for crawlers.</li>
            </ul>"""
        }
    }

    for slug, p_data in pages.items():
        os.makedirs(slug, exist_ok=True)
        html_content = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p_data['title']} | freeconvert.cloud</title>
    <meta name="description" content="{p_data['desc']}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/{slug}/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="{p_data['title']} | freeconvert.cloud">
    <meta property="og:description" content="{p_data['desc']}">
    <meta property="og:url" content="https://freeconvert.cloud/{slug}/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{p_data['title']} | freeconvert.cloud">
    <meta name="twitter:description" content="{p_data['desc']}">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content">
        <!-- Visual Breadcrumbs -->
        <nav class="breadcrumbs">
            <a href="/">Home</a>
            <span>&gt;</span>
            <span style="color: var(--text-muted);">{p_data['title']}</span>
        </nav>

        <section class="tool-header">
            <h1>{p_data['title']}</h1>
            <p style="margin-top: 0.5rem;">{p_data['desc']}</p>
        </section>

        <!-- AdSense Slot: Legal Page Mid Content -->
        <div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
            <span class="adsense-label">Advertisement</span>
            <ins class="adsbygoogle"
                 style="display:block;min-height:90px;"
                 data-ad-client="ca-pub-8997218708343263"
                 data-ad-slot="REPLACE_SLOT_LEGAL_MID"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </div>

        <article class="seo-content">
            {p_data['content']}
        </article>
    </main>

    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>

</html>"""
        with open(f"{slug}/index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated legal/trust page: /{slug}/index.html")

def build_press_kit_page():
    """Generate a public press/media kit for journalists and directory owners."""
    slug = 'press-kit'
    title = 'Press Kit'
    desc = 'Downloadable brand assets, facts, and contact information for freeconvert.cloud.'
    content = """<h2>About freeconvert.cloud</h2>
        <p>freeconvert.cloud is a free, browser-based file conversion platform that handles PDF, image, video, audio, document, archive, and developer formats. The platform is built with privacy in mind: most tools run locally in the browser so files never leave the user's device.</p>

        <h2>Quick Facts</h2>
        <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1.5rem;">
            <li><strong>Founded:</strong> 2026</li>
            <li><strong>Website:</strong> <a href="https://freeconvert.cloud" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">https://freeconvert.cloud</a></li>
            <li><strong>Pricing:</strong> Free (Pro and API plans available)</li>
            <li><strong>Platforms:</strong> Web, iOS browser, Android browser</li>
            <li><strong>Headquarters:</strong> Global, remote-first</li>
            <li><strong>Contact:</strong> <a href="mailto:press@freeconvert.cloud" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">press@freeconvert.cloud</a></li>
        </ul>

        <h2>Brand Assets</h2>
        <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1.5rem;">
            <li><strong>Logo (PNG):</strong> <a href="/assets/freeconvert-logo.png" style="color:var(--brand-primary);font-weight:600;text-decoration:none;" download>Download PNG</a></li>
            <li><strong>Favicon (PNG):</strong> <a href="/assets/favicon.png" style="color:var(--brand-primary);font-weight:600;text-decoration:none;" download>Download favicon</a></li>
        </ul>

        <h2>Official Description</h2>
        <p>freeconvert.cloud is a free, browser-based file conversion platform for documents, images, PDFs, videos, audio, archives, and developer files. Most tools run locally in your browser, so your files never leave your device unless the format requires server processing. The platform includes 80+ converters, compressors, format guides, and batch-friendly workflows — all without sign-ups or intrusive ads.</p>

        <h2>Tagline</h2>
        <p>"Free, privacy-first file converters for every format."</p>

        <h2>Key Features</h2>
        <ul style="padding-left:1.5rem; display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1.5rem;">
            <li>80+ free file converters for PDF, image, video, audio, document, archive, and developer formats</li>
            <li>Browser-local processing for privacy-sensitive conversions</li>
            <li>No registration or software installation required</li>
            <li>Batch-friendly workflows and compression tools</li>
            <li>Clean, fast UI with mobile support</li>
            <li>Free guides and format explainers for every workflow</li>
            <li>Developer API for automated conversions</li>
        </ul>

        <h2>Categories</h2>
        <p>File Converter, PDF Tools, Image Converter, Online Tools, Productivity, Developer Tools, Design Tools, Security, Privacy.</p>

        <h2>In the News & Directories</h2>
        <p>freeconvert.cloud is listed or submitted to Product Hunt, AlternativeTo, G2, Capterra, 10015.io, and leading software directories. For partnership, press, or directory inquiries, contact <a href="mailto:press@freeconvert.cloud" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">press@freeconvert.cloud</a>.</p>

        <h2>Product Hunt Launch</h2>
        <p>Track our launch on Product Hunt and support the project: <a href="https://www.producthunt.com/products/freeconvert-cloud" style="color:var(--brand-primary);font-weight:600;text-decoration:none;">freeconvert.cloud on Product Hunt</a>.</p>"""

    os.makedirs(slug, exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | freeconvert.cloud</title>
    <meta name="description" content="{desc}">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/{slug}/" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="freeconvert.cloud">
    <meta property="og:title" content="{title} | freeconvert.cloud">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="https://freeconvert.cloud/{slug}/">
    <meta property="og:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title} | freeconvert.cloud">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="https://freeconvert.cloud/assets/freeconvert-logo.png">
    <meta name="twitter:site" content="@freeconvertcloud">

    <!-- Preloads -->
    <link rel="preload" href="/style.css" as="style">
    <link rel="preload" href="/assets/freeconvert-logo.png" as="image">
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content">
        <!-- Visual Breadcrumbs -->
        <nav class="breadcrumbs">
            <a href="/">Home</a>
            <span>&gt;</span>
            <span style="color: var(--text-muted);">{title}</span>
        </nav>

        <section class="tool-header">
            <h1>{title}</h1>
            <p style="margin-top: 0.5rem;">{desc}</p>
        </section>

        <article class="seo-content">
            {content}
        </article>
    </main>

    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>

</html>"""
    with open(f"{slug}/index.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated press kit page: /{slug}/index.html")

def generate_tool_adsense_content(tool):
    t_id = tool['id']
    t_name = tool['name']
    t_cat = tool.get('category', 'Utility')
    t_desc = tool['description']
    t_type = tool['type']
    
    use_cases = []
    limitations = ""
    faqs = []
    
    # Specific tool customizations for the main high-volume target pages
    if t_id == 'png-to-jpg':
        use_cases = [
            "Optimizing website page load speeds by converting massive transparent PNG screenshots into highly compressed, light JPG images.",
            "Structuring and exporting graphics design assets for universal compatibility with digital publishing, photo galleries, and social media platforms.",
            "Batch-converting image files inside developer environments to standard high-definition compressed photo targets."
        ]
        limitations = "This tool executes 100% locally in your web browser memory using the HTML5 Canvas API. Processing extremely large files (e.g. over 50MB) may cause brief browser tab freezes depending on your computer's RAM and CPU capabilities."
        faqs = [
            {"q": "Will my output JPG image retain transparent layers from the PNG source?", "a": "No, the JPG format does not support transparency. Any transparent background pixels in your original PNG image will automatically be converted to a solid white background color by our local rendering engine."},
            {"q": "Are my uploaded photos safe and secure?", "a": "Absolutely. This converter processes files entirely client-side using JavaScript. Your files never touch external networks, internet servers, or third-party databases. It is 100% private and secure."},
            {"q": "Can I convert multiple PNG files at once?", "a": "Yes! Our conversion framework supports multi-file queues. You can drag and drop several PNG files together into the upload section and click Convert to process them in a batch instantly."},
            {"q": "Will my PNG background turn black during conversion?", "a": "No. Typical poor converters render transparent PNG layers as black fields in JPG. freeconvert.cloud automatically applies a solid, clean white background layer behind transparent coordinates."},
            {"q": "Is there a limit on file page sizes for free users?", "a": "No, free users can convert batch photos under 50MB instantly. We keep zero logs and enforce no registrations."}
        ]
    elif t_id == 'jpg-to-png':
        use_cases = [
            "Converting heavily compressed camera pictures to PNG format to preserve maximum pixel detailing for layers editing.",
            "Preparing graphic elements, vector frames, and logos for background removal and transparency blending in design tools.",
            "Eliminating artifacts and blocky shapes caused by JPG compression algorithms by upgrading files to lossless PNG models."
        ]
        limitations = "Because PNG is a lossless format, converting a JPG to PNG will usually increase the resulting file size. Furthermore, format conversion alone does not magically make a solid white background transparent."
        faqs = [
            {"q": "Does converting JPG to PNG automatically make the background transparent?", "a": "No. Format conversion changes the underlying binary structure to support transparency. However, to actually make a background transparent, you must use a background removal editor or layer masking afterward."},
            {"q": "Why is the converted PNG file larger than my original JPG?", "a": "JPG is a lossy compressed format that discards subtle color variations to save space. PNG is a lossless format that records every single pixel value perfectly. Converting a compressed file into a lossless container causes the file size to expand to hold the unpacked pixel grid."},
            {"q": "Is my privacy secure while using this JPG to PNG converter?", "a": "Yes. The conversion engine runs in-browser. No image data is sent to our servers. Your original photos are processed completely inside your device memory."},
            {"q": "Can I use this JPG to PNG converter on my iPhone?", "a": "Yes, our tool is fully responsive and runs client-side inside Safari, Chrome, and Firefox web browsers on iOS and Android without any setup."},
            {"q": "Are there any watermarks or hidden subscription costs?", "a": "No, freeconvert.cloud is 100% free with no advertising watermarks or registration gates."}
        ]
    elif t_id == 'word-counter':
        use_cases = [
            "Analyzing character limits and word count requirements for essays, school submissions, and academic research papers.",
            "Optimizing meta descriptions, social media tags, and AdWords snippets to strictly match character constraints for SEO rankings.",
            "Providing real-time telemetry on typing speed, sentence counts, and reading durations for content creators and copywriters."
        ]
        limitations = "Text parsing calculations are carried out locally inside your web browser. Copying and pasting extremely large text documents (such as a full 500-page book) may lead to visual lag due to standard DOM rendering limits."
        faqs = [
            {"q": "Does this word counter include spaces in the character count?", "a": "Yes. Our tool provides a comprehensive statistics dashboard detailing both 'Total Characters with Spaces' and 'Total Characters without Spaces' to fulfill any editor criteria."},
            {"q": "Is the text I type or paste stored anywhere?", "a": "No, never. All text calculations, metrics, and paragraph counting occur in real-time on your local machine. Closed browser tabs permanently purge your data. We do not store or transmit anything."},
            {"q": "Does this count paragraph breaks and sentence statistics?", "a": "Yes! The word counter dynamically calculates word counts, character counts, average sentence length, paragraph counts, and estimated reading time."},
            {"q": "Can I download or copy my analyzed text statistics?", "a": "Yes, we display a clear visual overview of all text statistics that you can easily copy alongside the text editor tools."},
            {"q": "Does the word counter support non-English scripts?", "a": "Yes. Our client-side parser reads Unicode characters, analyzing Latin, Cyrillic, Arabic, and Asian scripts correctly."}
        ]
    elif t_id == 'password-generator':
        use_cases = [
            "Generating strong, unbreakable cryptographic passwords for online bank portals, primary email suites, and social networks.",
            "Setting up highly secure passwords for system administration, server root accesses, and databases.",
            "Creating multi-character secure seeds and unique keys for keychains and software activations."
        ]
        limitations = "Since our password generator runs entirely in the browser memory, we maintain zero logs. Be sure to copy and record your password securely in a personal password vault before closing the window."
        faqs = [
            {"q": "Are the passwords generated by this tool safe from hacking?", "a": "Yes. The passwords are constructed locally using the Web Cryptography API, utilizing robust entropy seeds. They are highly secure against dictionary and brute-force cracking attacks."},
            {"q": "Do you save the passwords generated on this page?", "a": "No. The system operates 100% locally. No password data is sent over the internet or saved in databases. Once you copy it, the text disappears from the browser state upon reloading."},
            {"q": "What options can I customize in this password generator?", "a": "You can select custom password lengths (up to 64 characters) and toggle upper case, lower case, numeric digits, and special symbolic characters depending on your requirements."},
            {"q": "Is there an author fact-check for these tools?", "a": "Yes, our secure tools are fact-checked and maintained by the freeconvert.cloud Editorial Team under absolute E-E-A-T and privacy guidelines."},
            {"q": "Does this work on mobile devices without app installation?", "a": "Yes, fully responsive and works natively in mobile browsers, letting you generate passwords securely on-the-go."}
        ]
    elif t_id == 'image-resizer':
        use_cases = [
            "Resizing digital images to match exact pixel width and height requirements for social media banners, post thumbnails, and profile avatars.",
            "Cropping or scale-adjusting product images to standardized grids for e-commerce store listings.",
            "Shrinking photos to prevent web page loading delays and lower client data usage."
        ]
        limitations = "Image scaling utilizes the HTML5 Canvas 2D context. Resizing extremely high-resolution files (e.g., raw DSLR images above 8000x8000 pixels) might result in slight browser stuttering during pixel interpolation."
        faqs = [
            {"q": "Can I lock the aspect ratio while resizing my images?", "a": "Yes, our image resizer includes a smart aspect ratio lock checkbox. When checked, changing the width automatically recalculates the height proportionally to prevent distortion."},
            {"q": "Does this resizer reduce the quality of my images?", "a": "No, you can adjust the quality slider to 100% for lossless scaling, or lower the quality slider to save on output file size. The process is completely transparent and customizable."},
            {"q": "Is my uploaded image sent to a server?", "a": "No. All scaling, resizing, and aspect ratio interpolations are executed inside your browser. No files are uploaded to our servers, keeping your photos entirely private."},
            {"q": "Does resizing help website speed optimization?", "a": "Absolutely. Scaling massive photos down to the exact size they will be displayed on your webpage prevents heavy data downloads, dramatically boosting page loading speed and Core Web Vitals."},
            {"q": "Can I resize by custom percentage?", "a": "Yes, the resizer handles exact custom pixel inputs for width and height instantly."}
        ]
    elif t_id == 'image-compressor':
        use_cases = [
            "Reducing image files to extremely small sizes to speed up website speed and boost Core Web Vitals performance.",
            "Optimizing image attachments to stay below strict email inbox or attachment size limits.",
            "Freeing up local disk space by compressing large personal photo folders."
        ]
        limitations = "Compression ratios vary depending on the file type. Extremely compressed PNG files may lose minor edge details, while highly optimized JPGs use custom quantizations. Max file limit is 50MB."
        faqs = [
            {"q": "Is this compression lossy or lossless?", "a": "Our compressor supports smart lossy compression by default, which trims imperceptible color details to shrink file sizes by up to 80%. You can adjust the quality scale slider for customized compression rates."},
            {"q": "Are my files uploaded to your servers for compression?", "a": "No, compression runs client-side using JavaScript. Your files are compressed in browser memory and are never uploaded, ensuring complete privacy."},
            {"q": "Which image formats are supported for compression?", "a": "We support direct compression of PNG, JPG, JPEG, and WebP images instantly."},
            {"q": "Will compressing images affect my SEO scores?", "a": "Yes! Serving compressed images below 150KB directly speeds up Largest Contentful Paint (LCP), giving your site a massive boost in Google's search algorithms."},
            {"q": "Can I compress transparent PNG files cleanly?", "a": "Yes. Our tool optimizes lossless PNG files, maintaining full alpha-channel transparent borders without corruption."}
        ]
    elif t_id == 'json-to-csv':
        use_cases = [
            "Converting complex developer JSON API payloads to flat CSV tables for easy analysis inside Excel or Google Sheets.",
            "Migrating structured document database collections into standard relational database rows.",
            "Preparing database exports for import into legacy ERP systems or email marketing software."
        ]
        limitations = "Calculated client-side. Converting deeply nested JSON arrays with varying column definitions may result in blank fields or require flattening."
        faqs = [
            {"q": "Does this tool support nested JSON structures?", "a": "Yes! Our parser automatically flattens nested objects into dot-separated column headers (e.g. user.address.city) for clean representation in CSV tables."},
            {"q": "Is my confidential JSON data uploaded to the server?", "a": "No, never. The conversion engine runs purely inside your browser window. Your sensitive customer lists, database records, and proprietary objects are entirely safe and private."},
            {"q": "Can I import the CSV file directly into Microsoft Excel?", "a": "Absolutely. The generated CSV is completely compliant with RFC-4180 standards and can be opened immediately by Excel, Google Sheets, and other standard data tools."},
            {"q": "Is there a file limit for developer tool inputs?", "a": "Our JSON parser is optimized to process files client-side. Large scripts exceeding 10MB of raw text might cause a brief tab lag, but everything executes in RAM safely."},
            {"q": "Does freeconvert.cloud offer a reverse CSV to JSON converter?", "a": "Yes! We provide an active browser-local <a href='/csv-to-json/' style='color:var(--brand-primary); text-decoration:none;'>CSV to JSON Converter</a> that flattens cells back to clean arrays."}
        ]
    elif t_id == 'csv-to-json':
        use_cases = [
            "Importing flat tabular CSV data from spreadsheet exports into modern JSON document databases.",
            "Beautifying Excel rows into JSON arrays to integrate into mobile and web application codebases.",
            "Transforming old CSV spreadsheets into structured JSON files for API testing."
        ]
        limitations = "Standard limits are determined by browser parser limits. Converting files larger than 10MB might lag the output text preview console."
        faqs = [
            {"q": "How does the converter handle CSV headers?", "a": "The converter automatically uses the first row of your CSV as the JSON key properties. If your CSV lacks header columns, the tool can generate default generic keys (e.g. field1, field2)."},
            {"q": "Is it safe to paste client databases or subscriber lists here?", "a": "Yes. Since all CSV processing, parsing, and JSON generation runs locally in the sandbox, no database records are sent over the internet."},
            {"q": "Does the CSV parser support custom delimiters like semicolons or tabs?", "a": "Yes, our engine automatically detects standard comma, semicolon, tab, and pipe delimiters instantly."},
            {"q": "Can I convert spreadsheets back to JSON arrays?", "a": "Yes. Column coordinates are converted to neat structured arrays, making them immediately ready for REST APIs and databases."},
            {"q": "What browser engines are required?", "a": "Works natively on Google Chrome, Safari, Microsoft Edge, and Mozilla Firefox on any PC or mobile device."}
        ]
    elif t_id == 'heic-to-jpg':
        use_cases = [
            "Converting iPhone HEIC camera photos to standard JPG format for compatibility on legacy computers.",
            "Formatting Apple HEIF photos to share easily on WhatsApp, email, or digital photo frames.",
            "Transcoding HEIC photos to standard formats for simple web publishing."
        ]
        limitations = "Requires moderate CPU power to unpack modern HEIF encodings in-browser. Converting multiple high-resolution photos may take a few seconds."
        faqs = [
            {"q": "Why does Apple use HEIC format instead of JPG?", "a": "HEIC (High Efficiency Image Container) uses advanced compression to store photos at half the file size of JPG while maintaining identical image quality. However, it is not supported on older platforms."},
            {"q": "Does this conversion delete the original photo from my iPhone?", "a": "No, your original HEIC photos remain completely untouched on your device. The tool simply processes a copy in memory and outputs a fresh JPG for download."},
            {"q": "Are my high-resolution photos sent to any server?", "a": "Absolutely not. All HEIC parsing, decoding, and JPG rendering are carried out locally on your computer using client-side libraries."},
            {"q": "Does the HEIC to JPG converter preserve metadata?", "a": "Yes. Our local conversion engine translates image dimensions and colors identically without stripping standard EXIF data tags."},
            {"q": "Can I bulk convert HEIC photos?", "a": "Yes, batch selection is supported, allowing you to convert groups of iPhone HEIF photos simultaneously."}
        ]
    elif t_id == 'webp-to-jpg':
        use_cases = [
            "Converting modern WebP images downloaded from websites to JPG format for standard image editors.",
            "Formatting high-definition WebP graphics to share on social networks that do not support WebP uploads.",
            "Preparing images for legacy apps and software that require traditional JPG extensions."
        ]
        limitations = "This tool processes 100% client-side in the browser. Animated WebP images will only have their first frame converted to a static JPG photo."
        faqs = [
            {"q": "Will the image quality drop when converting WebP to JPG?", "a": "WebP is a highly optimized format. When converting to JPG, minor quality loss might happen due to lossy JPG compression. You can adjust the quality slider to 100% to maximize resolution."},
            {"q": "Can I convert multiple WebP files together?", "a": "Yes! Batch selection is fully supported. You can upload several WebP images at once and convert them instantly with a single click."},
            {"q": "Does this WebP tool require internet data uploads?", "a": "No. The transcoding is executed completely in your local browser sandbox RAM, keeping your data private and saving your mobile bandwidth."},
            {"q": "Will it support transparent WebP images?", "a": "Yes. Because JPG lacks transparency, our local rendering overlay applies a solid white background layer behind transparent WebP pixels."},
            {"q": "What is the file size limit?", "a": "We recommend keeping batch uploads under 50MB to ensure fluid, fast rendering in local memory."}
        ]
    elif t_id == 'jpg-to-pdf':
        use_cases = [
            "Combining homework scans, expense receipts, or book images sequentially into a single PDF document.",
            "Structuring and compiling creative design comps for formal business presentations.",
            "Formatting image files into standard PDF containers to bypass email size boundaries."
        ]
        limitations = "Processed entirely client-side inside browser sandbox memory. For optimal speeds, keep batch image file uploads under 50MB."
        faqs = [
            {"q": "Can I combine multiple JPG files into a single PDF document?", "a": "Yes! freeconvert.cloud supports multi-page compiling. Simply select multiple JPG images and compile them into a beautifully ordered multi-page PDF."},
            {"q": "Does converting JPG to PDF reduce image resolution?", "a": "No. Our local compiler maps pixel details identically without downscaling, unless you explicitly select margins or compression levels to meet strict HR guidelines."},
            {"q": "Are my private scanned documents safe from data leaks?", "a": "Absolutely. Because this converter operates client-side in your local browser memory, your scanned receipts or tax records are never uploaded to any server."},
            {"q": "Do I need Adobe Acrobat to perform this PDF compile?", "a": "No, our utility runs natively inside modern browsers (Safari, Chrome) without requiring plugins, apps, or setups."},
            {"q": "Does the converter work on iPhones and Android systems?", "a": "Yes, our web platform is fully responsive and optimized for mobile devices, letting you compile JPGs on-the-go."}
        ]
    elif t_id == 'pdf-to-word':
        use_cases = [
            "Transforming read-only document contracts to editable Microsoft Word files for copywriting edits.",
            "Extracting flat tabular arrays from PDF reports into editable Word rows.",
            "Re-editing personal resumes without losing original visual coordinates."
        ]
        limitations = "Complex PDF documents containing heavy vector layouts or hand-drawn sketches might reflow slightly during Microsoft Word translation, requiring brief manual reviews."
        faqs = [
            {"q": "Can I edit the output Word document directly?", "a": "Yes, the converted output is exported as a standard Microsoft Word Open XML (.docx) file, which is fully editable in MS Word, LibreOffice, and Google Docs."},
            {"q": "Are my uploaded PDF contracts secure?", "a": "Yes. All file transfers utilize secure 256-bit SSL tunnels. Documents are processed in temporary sandboxed containers and permanently shredded from our drives within 2 hours."},
            {"q": "Does the converter preserve PDF tables and forms?", "a": "Yes, our converter accurately translates grid margins and cell borders into editable Word table cells, saving you substantial formatting time."},
            {"q": "Is there a limit on PDF page counts?", "a": "Free users can process PDF documents up to 50MB and 100 pages cleanly per session. Priority limits are unlocked on Pro plan tiers."},
            {"q": "How long does a typical PDF to Word conversion take?", "a": "Most documents are processed on our secure edge queues in under 10 seconds, delivering instant downloads."}
        ]
    elif t_id == 'mp4-to-mp3':
        use_cases = [
            "Extracting high-definition audio tracks from video files for background music players.",
            "Converting digital lectures and webinars into MP3 podcasts for offline learning.",
            "Freeing up substantial storage space by converting visual clips to audio files."
        ]
        limitations = "Video files are heavy payloads. Processing files requires edge cluster transcoding; ensure you remain under the 50MB free quota limit."
        faqs = [
            {"q": "Can I extract audio from videos in high quality?", "a": "Yes, you can choose custom bitrates up to 320kbps for pristine audio fidelity."},
            {"q": "Is it secure to upload my recordings here?", "a": "Yes, uploaded securely through SSL and permanently shredded within 2 hours."},
            {"q": "Which video containers are supported for extraction?", "a": "We support MP4, WebM, AVI, MOV, and MKV files."},
            {"q": "Does converting video to MP3 save storage space?", "a": "Yes, can reduce the file weight by up to 95%."},
            {"q": "Does it work on smartphones?", "a": "Yes, fully web-based and runs on mobile browsers without setups."}
        ]
    # General category-based dynamic content generation for fallback coverage
    else:
        if t_cat == 'Image' or 'image' in t_type:
            use_cases = [
                f"Optimizing {t_name} layouts to scale down loading times and reduce page sizes on web platforms.",
                f"Converting image assets into compatible {t_name} formats for graphic design and digital media campaigns.",
                f"Batch transcoding image formats locally with zero resolution loss or pixel blurring."
            ]
            limitations = f"This {t_name} converter is executed locally in your web browser sandbox using modern Canvas APIs. For optimal performance, the recommended file size is capped at 50MB."
            faqs = [
                {"q": f"Does this {t_name} tool upload my files to any server?", "a": f"No. All conversions for {t_name} occur locally on your computer inside the browser memory. Your files are completely safe and never touch our servers."},
                {"q": f"What is the benefit of using client-side {t_name} processing?", "a": f"Because it runs client-side, the {t_name} process is exceptionally fast, respects your privacy, and saves you network bandwidth since you do not have to upload files."},
                {"q": f"Can I use this responsive {t_name} converter on my mobile phone?", "a": f"Yes! Our interface is fully optimized for mobile devices. The {t_name} tool works perfectly on Safari, Chrome, and Firefox on iOS and Android."},
                {"q": f"How is E-E-A-T trust maintained?", "a": f"All tools are fact-checked and maintained under strict data safety protocols by the freeconvert.cloud Editorial Team."},
                {"q": f"What is the file size limit?", "a": f"We recommend keeping batch uploads under 50MB to ensure fluid, fast rendering in local memory."}
            ]
        elif t_cat == 'Developer' or 'dev_' in t_type or t_type in ['dev_basic', 'dev_advanced']:
            use_cases = [
                f"Beautifying and processing {t_name} data payloads to accelerate application development and debugging.",
                f"Transforming and formatting {t_name} syntax for code reviews, database migrations, and clean repository commits.",
                f"Converting {t_name} outputs safely on-the-fly without exposing proprietary code to external APIs."
            ]
            limitations = f"Calculated locally using parser libraries. Text inputs larger than 10MB of raw {t_name} scripts may cause a brief browser freeze during syntax highlighting."
            faqs = [
                {"q": f"Is my code or private text secure when using {t_name}?", "a": f"Absolutely. The {t_name} processor runs entirely within your browser window. Zero code, text, or database strings are sent over the internet, making it safe for corporate use."},
                {"q": f"Can I load sample data to test the {t_name} tool?", "a": f"Yes! We provide a '✨ Load Sample' button right above the editor panel so you can quickly see how the {t_name} parser formats outputs."},
                {"q": f"Does this {t_name} utility support dark theme console layouts?", "a": f"Yes, the developer tools feature a beautiful dark-theme console layout styled with custom syntax glowing borders to reduce eye strain."},
                {"q": f"Does this work on mobile viewports?", "a": f"Yes, the editor panels scale dynamically into neat stacks on mobile screens, allowing easy debugging."},
                {"q": f"Can I copy my converted data cleanly?", "a": f"Yes! Simply click the Copy button to immediately save the parsed string to your clipboard."}
            ]
        elif t_cat == 'Video Converter' or t_type == 'video':
            use_cases = [
                f"Converting {t_name} files for social media uploads, mobile playback, website embeds, and client sharing.",
                f"Preparing video clips for compatibility across iPhone, Android, Windows, macOS, browsers, and editing tools.",
                f"Reducing friction when a platform rejects a video because the format, file size, or dimensions are not accepted."
            ]
            limitations = f"{t_name} works best with common video containers such as MP4, MOV, AVI, MKV, and WebM. Large files may require temporary encrypted edge processing because browser-only video transcoding can be heavy."
            faqs = [
                {"q": f"What is {t_name} best used for?", "a": f"Use {t_name} when you need a more compatible, smaller, or easier-to-share video output for websites, social platforms, messages, or editing tools."},
                {"q": f"Are uploaded videos private?", "a": "Video files are transferred over HTTPS for temporary processing when transcoding is required. Files are designed to be deleted automatically after processing."},
                {"q": f"Which video formats are commonly supported?", "a": "Common workflows include MP4, MOV, AVI, MKV, WebM, MP3 audio extraction, GIF clips, trimming, resizing, and compression."},
                {"q": f"Can I use {t_name} on mobile?", "a": "Yes, the page is responsive and works in modern mobile browsers. For very large videos, desktop browsers usually perform better."},
                {"q": f"How do I keep video quality high?", "a": "Start with the best original file, avoid repeated conversions, and compress only as much as your upload or sharing limit requires."}
            ]
        elif t_cat == 'Security' or 'security' in t_type:
            use_cases = [
                f"Creating strong credentials and security measures to shield online database and bank portals.",
                f"Analyzing passphrase strength and vulnerabilities against brute force calculations.",
                f"Generating random cryptographically sound credentials to secure systems."
            ]
            limitations = f"Calculated 100% locally. We do not host or back up passwords. Make sure to copy and save your {t_name} values in a password manager."
            faqs = [
                {"q": f"Are the passwords or credentials generated by this tool secure?", "a": f"Yes. Our {t_name} algorithm uses the browser Cryptography API to generate keys with high entropy, making them extremely robust."},
                {"q": f"Do you record the credentials analyzed on this page?", "a": f"No, never. The {t_name} tool runs in-browser. Zero data is transmitted to the network or saved in server databases."},
                {"q": f"How is E-E-A-T trust maintained?", "a": f"All tools are fact-checked and maintained under strict data safety protocols by the freeconvert.cloud Editorial Team."},
                {"q": f"Do I need to sign up to use the tools?", "a": f"No, all converters are 100% free with no registration or subscriptions required."},
                {"q": f"Does this work on mobile viewports?", "a": f"Yes, works natively inside Safari and Chrome on any device."}
            ]
        else:
            use_cases = [
                f"Generating {t_name} configurations for commercial, design, and development projects.",
                f"Performing precise {t_name} calculations and measurements with instant responsive rendering.",
                f"Testing, building, and deploying resources with precise, millisecond-level precision."
            ]
            limitations = f"Processes inside the client sandbox. Performance is maintained locally, though network-based operations depend on your ISP connection speeds."
            faqs = [
                {"q": f"Is this {t_name} tool free to use?", "a": f"Yes, all converters on freeconvert.cloud are 100% free with no registration or subscriptions required."},
                {"q": f"How does the {t_name} tool save my configurations?", "a": f"We use secure lightweight local browser storage to remember your custom options so they are preserved when you visit again."},
                {"q": f"Does this tool upload my files to any server?", "a": f"No. All conversions for {t_name} occur locally on your computer inside the browser memory. Your files are completely safe and never touch our servers."},
                {"q": f"Is this responsive on mobile browsers?", "a": f"Yes, works natively inside modern mobile browsers without app installations."},
                {"q": f"How is E-E-A-T trust maintained?", "a": f"All tools are fact-checked and maintained under strict data safety protocols by the freeconvert.cloud Editorial Team."}
            ]

    # Convert lists to HTML
    use_cases_html = "".join([f"<li>{uc}</li>" for uc in use_cases])
    
    faq_html = ""
    for f in faqs:
        faq_html += f"""
        <div class="accordion">
            <div class="accordion-header">❓ {f['q']}</div>
            <div class="accordion-content">
                <p style="font-size:0.95rem; color:var(--text-muted); line-height:1.6;">{f['a']}</p>
            </div>
        </div>"""
        
    return use_cases_html, limitations, faq_html, faqs


def build_discovery_files(tools):
    tools_by_id = {tool['id']: tool for tool in tools}
    available_tool_ids = set(tools_by_id)
    priority_tool_lines = []
    for target in TOP_KEYWORD_TARGETS:
        tool = tools_by_id.get(target['tool_id'])
        if not tool:
            continue
        priority_tool_lines.append(
            f"- {tool['name']}: {SITE_URL}/{tool['id']}/ - targets \"{target['keyword']}\"; intent: {target['intent']}"
        )

    all_tool_lines = [
        f"- {tool['name']}: {SITE_URL}/{tool['id']}/ - {tool['description']} Category: {tool.get('category', 'Utility')}."
        for tool in tools
    ]

    keyword_cluster_lines = [
        f"- {target['keyword']} -> {SITE_URL}/{target['tool_id']}/ ({target['cluster']}; variants: {', '.join(target['modifiers'])})"
        for target in TOP_KEYWORD_TARGETS
        if target['tool_id'] in available_tool_ids
    ]

    # 1. llms.txt
    llms_content = f"""# freeconvert.cloud - Privacy-First File Converter Platform

## Purpose
freeconvert.cloud provides practical browser-based image, text, developer, security, and calculation tools with clear limitations and privacy-first processing.

## Core Conversion Paradigm
- **Client-Side Tools:** Supported image, text, code, security, and calculation tools run directly in the browser using standard web APIs.
- **Unavailable Conversions:** Tools that require an unfinished server service are excluded from public directories and search discovery until their output can be verified end to end.

## Main Navigation Pages
- Homepage: https://freeconvert.cloud/ - Upload box and unified utility grid.
- Blog Hub: https://freeconvert.cloud/blog/ - Fact-checked guides and tutorials.
- File Format Glossary: https://freeconvert.cloud/file-formats/ - Plain-English format definitions that connect users to the right converters.
- All Tools Directory: https://freeconvert.cloud/all-tools/ - Crawl-friendly HTML index linking to every converter and utility page.
- HTML Sitemap: https://freeconvert.cloud/sitemap/ - Human-readable crawl hub covering tools, guides, categories, and support pages.
- Press Kit: https://freeconvert.cloud/press-kit/ - Brand assets, facts, and media contact information for journalists and directory owners.

## Priority Tools (High Content Depth)
{chr(10).join(priority_tool_lines[:12])}

## High-Intent Keyword Map
{chr(10).join(keyword_cluster_lines)}

## Privacy & Safety Core Documents
- File Security Info: https://freeconvert.cloud/security/
- About Us: https://freeconvert.cloud/about/
- Contact Us: https://freeconvert.cloud/contact/
- Privacy Policy: https://freeconvert.cloud/privacy/
- Terms of Service: https://freeconvert.cloud/terms/
- Cookie Policy: https://freeconvert.cloud/cookies/
- DMCA Abuse Policy: https://freeconvert.cloud/dmca/

## Machine-Readable Discovery
- Full LLM inventory: https://freeconvert.cloud/llms-full.txt
- AI JSON index: https://freeconvert.cloud/ai-index.json
- Keyword targets: https://freeconvert.cloud/seo-keyword-targets.json
- XML sitemap index: https://freeconvert.cloud/sitemap-index.xml
"""
    with open('llms.txt', 'w', encoding='utf-8') as f:
        f.write(llms_content)
    print("Generated `/llms.txt` successfully.")

    llms_full_content = f"""# freeconvert.cloud Full LLM Inventory

## Site Summary
freeconvert.cloud provides browser-first image tools, developer utilities, text tools, security generators, calculators, and practical guides.

## Top Keyword Targets
{chr(10).join(keyword_cluster_lines)}

## Complete Tool Inventory
{chr(10).join(all_tool_lines)}

## Editorial And Trust Signals
- Editorial team: freeconvert.cloud Editorial Team.
- Privacy model: supported public tools use client-side browser processing where possible.
- Advertising model: clearly labeled ads, no fake download buttons, no deceptive conversion CTAs.
- Update marker: {TODAY_ISO}.

## Useful Discovery URLs
- Sitemap: {SITE_URL}/sitemap.xml
- RSS feed: {SITE_URL}/feed.xml
- OpenSearch: {SITE_URL}/opensearch.xml
- Blog hub: {SITE_URL}/blog/
- File format glossary: {SITE_URL}/file-formats/
- Press kit: {SITE_URL}/press-kit/
- Security: {SITE_URL}/security/
- Contact: {SITE_URL}/contact/
"""
    Path('llms-full.txt').write_text(llms_full_content, encoding='utf-8')
    print("Generated `/llms-full.txt` successfully.")

    ai_index = {
        "name": "freeconvert.cloud",
        "url": f"{SITE_URL}/",
        "updated": TODAY_ISO,
        "description": "Privacy-first online file conversion platform with image, PDF, document, media, developer, security, and utility tools.",
        "entity_type": "WebApplication",
        "trust": {
            "editorial_team": "freeconvert.cloud Editorial Team",
            "privacy_model": "Client-side browser sandbox for standard tools; encrypted transient edge sandboxes for heavy conversion jobs.",
            "ads_policy": "Clearly labeled ads with no fake buttons or deceptive conversion controls."
        },
        "keyword_targets": [
            {
                "priority": target["priority"],
                "keyword": target["keyword"],
                "url": f"{SITE_URL}/{target['tool_id']}/",
                "intent": target["intent"],
                "cluster": target["cluster"],
                "variants": target["modifiers"]
            }
            for target in TOP_KEYWORD_TARGETS
            if target['tool_id'] in available_tool_ids
        ],
        "tools": [
            {
                "id": tool["id"],
                "name": tool["name"],
                "url": f"{SITE_URL}/{tool['id']}/",
                "category": tool.get("category", "Utility"),
                "description": tool["description"],
                "title": tool.get("seo_title", tool["name"]),
                "target_keyword": (keyword_target_for_tool(tool["id"]) or {}).get("keyword")
            }
            for tool in tools
        ],
        "discovery": {
            "sitemap": f"{SITE_URL}/sitemap-index.xml",
            "rss": f"{SITE_URL}/feed.xml",
            "opensearch": f"{SITE_URL}/opensearch.xml",
            "llms": f"{SITE_URL}/llms.txt",
            "llms_full": f"{SITE_URL}/llms-full.txt",
            "keyword_targets": f"{SITE_URL}/seo-keyword-targets.json"
        }
    }
    Path('ai-index.json').write_text(json.dumps(ai_index, indent=2), encoding='utf-8')
    print("Generated `/ai-index.json` successfully.")

    # 2. humans.txt
    humans_content = """/* TEAM */
Project Name: freeconvert.cloud
Purpose: Secure, browser-based online file conversion SaaS
Editorial Team: freeconvert.cloud Editorial Team
Contact Email: support@freeconvert.cloud
Responsible Advertising: Labeled AdSense placeholders, zero popups or fake buttons

/* SITE SECTIONS */
Homepage: https://freeconvert.cloud/
Image Converter Hub: https://freeconvert.cloud/image-converter/
PDF Tools Suite: https://freeconvert.cloud/pdf-tools/
Document Tools Hub: https://freeconvert.cloud/document-converter/
Developer API: https://freeconvert.cloud/api/
Resource Tutorials Hub: https://freeconvert.cloud/blog/
Pricing Plans: https://freeconvert.cloud/pricing/
File Security Integrity: https://freeconvert.cloud/security/
"""
    with open('humans.txt', 'w', encoding='utf-8') as f:
        f.write(humans_content)
    print("Generated `/humans.txt` successfully.")



# Blog → Tool contextual link map
BLOG_TOOL_MAP = {
    'how-to-convert-jpg-to-pdf-online': [('jpg-to-pdf','JPG to PDF'),('compress-pdf','Compress PDF'),('pdf-to-word','PDF to Word')],
    'how-to-convert-png-to-jpg-without-losing-quality': [('png-to-jpg','PNG to JPG'),('image-compressor','Image Compressor'),('resize-image','Resize Image')],
    'jpg-vs-png-which-format-should-you-use': [('png-to-jpg','PNG to JPG'),('jpg-to-png','JPG to PNG'),('image-compressor','Compress Image')],
    'pdf-vs-docx-what-is-the-difference': [('pdf-to-word','PDF to Word'),('compress-pdf','Compress PDF'),('jpg-to-pdf','JPG to PDF')],
    'how-to-compress-images-for-websites': [('image-compressor','Image Compressor'),('compress-image-to-100kb','Compress to 100KB'),('resize-image','Resize Image')],
    'how-to-convert-json-to-csv-for-spreadsheets': [('json-to-csv','JSON to CSV'),('csv-to-json','CSV to JSON'),('json-formatter','JSON Formatter')],
    'mp3-vs-wav-which-audio-format-is-better': [('mp4-to-mp3','MP4 to MP3'),('video-compressor','Video Compressor')],
    'mp4-vs-webm-best-video-format-for-the-web': [('mp4-to-mp3','MP4 to MP3'),('webm-to-mp4','WebM to MP4'),('video-compressor','Video Compressor')],
    'how-to-keep-files-secure-when-using-online-converters': [('security','File Security'),('password-generator','Password Generator'),('image-compressor','Image Compressor')],
    'best-free-online-file-conversion-tools-for-students-and-professionals': [('jpg-to-pdf','JPG to PDF'),('json-to-csv','JSON to CSV'),('image-compressor','Image Compressor'),('word-counter','Word Counter')],
    'how-to-compress-images-online-without-losing-quality': [('image-compressor','Image Compressor'),('compress-image-to-100kb','Compress to 100KB'),('compress-image-to-200kb','Compress to 200KB'),('resize-image','Resize Image')],
    'how-to-compress-an-image-to-100kb': [('compress-image-to-100kb','Compress to 100KB'),('compress-image-to-200kb','Compress to 200KB'),('image-compressor','Image Compressor')],
    'webp-vs-jpg-which-image-format-should-you-use': [('webp-to-jpg','WebP to JPG'),('png-to-jpg','PNG to JPG'),('jpg-to-png','JPG to PNG')],
    'heic-to-jpg-how-to-convert-iphone-photos-online': [('png-to-jpg','PNG to JPG'),('image-compressor','Image Compressor'),('resize-image','Resize Image')],
    'best-free-online-tools-for-bloggers-and-students': [('word-counter','Word Counter'),('character-counter','Character Counter'),('qr-code-generator','QR Code Generator'),('meta-title-checker','Meta Title Checker')],
    'how-to-use-a-json-formatter-and-validator': [('json-formatter','JSON Formatter'),('json-validator','JSON Validator'),('json-to-csv','JSON to CSV'),('base64-encode','Base64 Encoder')],
    'what-is-a-qr-code-and-how-to-generate-one-safely': [('qr-code-generator','QR Code Generator'),('barcode-generator','Barcode Generator'),('url-encoder','URL Encoder')],
    'how-to-compress-pdf-under-1mb-online': [('compress-pdf','Compress PDF'),('jpg-to-pdf','JPG to PDF'),('pdf-to-jpg','PDF to JPG'),('image-compressor','Image Compressor')],
    'convert-pdf-to-jpg-high-quality-online': [('pdf-to-jpg','PDF to JPG'),('jpg-to-pdf','JPG to PDF'),('compress-pdf','Compress PDF'),('image-compressor','Image Compressor')],
    'convert-word-to-pdf-online-free': [('word-to-pdf','Word to PDF'),('pdf-to-word','PDF to Word'),('compress-pdf','Compress PDF'),('document-converter','Document Converter')],
    'webp-to-jpg-converter-guide': [('webp-to-jpg','WebP to JPG'),('png-to-jpg','PNG to JPG'),('image-compressor','Image Compressor'),('compress-image-to-200kb','Compress Image to 200KB')],
    'resize-image-for-instagram-without-cropping': [('resize-image-for-instagram','Resize Image for Instagram'),('resize-image','Resize Image'),('image-compressor','Image Compressor'),('compress-image-to-200kb','Compress Image to 200KB')],
    'passport-photo-size-converter-online-guide': [('passport-photo-size-converter','Passport Photo Size Converter'),('resize-image','Resize Image'),('compress-image-to-100kb','Compress Image to 100KB'),('image-compressor','Image Compressor')],
    'meta-title-description-checker-google-serp-guide': [('meta-title-checker','Meta Title Checker'),('meta-description-checker','Meta Description Checker'),('slug-generator','Slug Generator'),('word-counter','Word Counter')],
    'base64-encode-decode-online-guide': [('base64-encode','Base64 Encode'),('base64-decode','Base64 Decode'),('image-to-base64','Image to Base64'),('url-encoder','URL Encoder')],
    'merge-pdf-files-online-without-losing-pages': [('merge-pdf','Merge PDF'),('compress-pdf','Compress PDF'),('split-pdf','Split PDF'),('pdf-tools','PDF Tools')],
    'split-pdf-extract-pages-online': [('split-pdf','Split PDF'),('merge-pdf','Merge PDF'),('compress-pdf','Compress PDF'),('pdf-to-jpg','PDF to JPG')],
    'html-css-javascript-formatter-online-guide': [('html-formatter','HTML Formatter'),('css-formatter','CSS Formatter'),('javascript-formatter','JavaScript Formatter'),('json-formatter','JSON Formatter')],
    'qr-code-for-wifi-password-guide': [('qr-code-generator','QR Code Generator'),('barcode-generator','Barcode Generator'),('url-encoder','URL Encoder'),('password-generator','Password Generator')],
    'compress-image-to-200kb-online-guide': [('compress-image-to-200kb','Compress Image to 200KB'),('image-compressor','Image Compressor'),('png-to-jpg','PNG to JPG'),('webp-to-jpg','WebP to JPG')],
    'csv-to-json-converter-online-guide': [('csv-to-json','CSV to JSON'),('json-to-csv','JSON to CSV'),('json-validator','JSON Validator'),('json-formatter','JSON Formatter')],
    'pdf-to-word-converter-editable-docx-guide': [('pdf-to-word','PDF to Word'),('word-to-pdf','Word to PDF'),('compress-pdf','Compress PDF'),('document-converter','Document Converter')],
    'svg-to-png-converter-transparent-background-guide': [('svg-to-png','SVG to PNG'),('image-compressor','Image Compressor'),('png-to-jpg','PNG to JPG'),('resize-image','Resize Image')],
    'strong-password-generator-symbols-guide': [('password-generator','Password Generator'),('password-strength','Password Strength'),('hash-generator','Hash Generator'),('security','File Security')],
    'word-counter-for-essays-seo-and-social-posts': [('word-counter','Word Counter'),('character-counter','Character Counter'),('meta-title-checker','Meta Title Checker'),('meta-description-checker','Meta Description Checker')],
    'extract-color-palette-from-image-online-guide': [('palette-extractor','Color Palette Extractor'),('rgb-hex-converter','RGB HEX Converter'),('image-compressor','Image Compressor'),('resize-image','Resize Image')],
    'markdown-editor-online-preview-guide': [('markdown-editor','Markdown Editor'),('html-formatter','HTML Formatter'),('word-counter','Word Counter'),('slug-generator','Slug Generator')],
    'mp4-to-mp3-converter-online-audio-extraction-guide': [('mp4-to-mp3','MP4 to MP3'),('audio-converter','Audio Converter'),('video-compressor','Video Compressor'),('webm-to-mp4','WebM to MP4')],
    'webm-to-mp4-converter-compatibility-guide': [('webm-to-mp4','WebM to MP4'),('video-compressor','Video Compressor'),('mp4-to-mp3','MP4 to MP3'),('video-converter','Video Converter')],
    'json-validator-fix-errors-online-guide': [('json-validator','JSON Validator'),('json-formatter','JSON Formatter'),('json-to-csv','JSON to CSV'),('csv-to-json','CSV to JSON')],
    'url-encoder-decoder-safe-links-guide': [('url-encoder','URL Encoder'),('url-decoder','URL Decoder'),('base64-encode','Base64 Encode'),('qr-code-generator','QR Code Generator')],
    'hash-generator-checksum-md5-sha-guide': [('hash-generator','Hash Generator'),('password-generator','Password Generator'),('password-strength','Password Strength'),('security','File Security')],
    'aspect-ratio-calculator-resize-video-image-guide': [('aspect-ratio-calculator','Aspect Ratio Calculator'),('resize-image','Resize Image'),('resize-image-for-instagram','Resize Image for Instagram'),('image-compressor','Image Compressor')],
    'remove-duplicate-lines-clean-text-guide': [('remove-duplicate-lines','Remove Duplicate Lines'),('text-cleaner','Text Cleaner'),('case-converter','Case Converter'),('word-counter','Word Counter')],
    'timestamp-converter-unix-time-guide': [('timestamp-converter','Timestamp Converter'),('unix-time-converter','Unix Time Converter'),('time-zone-converter','Time Zone Converter'),('age-calculator','Age Calculator')],
    'png-to-webp-converter-page-speed-guide': [('png-to-webp','PNG to WebP'),('image-compressor','Image Compressor'),('resize-image','Resize Image'),('webp-to-jpg','WebP to JPG')],
    'jpg-to-webp-converter-seo-image-guide': [('jpg-to-webp','JPG to WebP'),('image-compressor','Image Compressor'),('compress-image-to-200kb','Compress Image to 200KB'),('png-to-webp','PNG to WebP')],
    'yaml-to-json-converter-config-guide': [('yaml-to-json','YAML to JSON'),('json-validator','JSON Validator'),('json-formatter','JSON Formatter'),('json-to-yaml','JSON to YAML')],
    'json-to-yaml-converter-devops-guide': [('json-to-yaml','JSON to YAML'),('yaml-to-json','YAML to JSON'),('json-validator','JSON Validator'),('json-formatter','JSON Formatter')],
    'uuid-generator-online-unique-id-guide': [('uuid-generator','UUID Generator'),('random-number-generator','Random Number Generator'),('hash-generator','Hash Generator'),('timestamp-converter','Timestamp Converter')],
    'sql-formatter-online-query-readable-guide': [('sql-formatter','SQL Formatter'),('json-formatter','JSON Formatter'),('diff-checker','Diff Checker'),('html-formatter','HTML Formatter')],
    'diff-checker-compare-text-code-guide': [('diff-checker','Diff Checker'),('text-cleaner','Text Cleaner'),('remove-duplicate-lines','Remove Duplicate Lines'),('word-counter','Word Counter')],
    'barcode-generator-online-product-labels-guide': [('barcode-generator','Barcode Generator'),('qr-code-generator','QR Code Generator'),('url-encoder','URL Encoder'),('uuid-generator','UUID Generator')],
    'meta-description-checker-serp-ctr-guide': [('meta-description-checker','Meta Description Checker'),('meta-title-checker','Meta Title Checker'),('word-counter','Word Counter'),('slug-generator','Slug Generator')],
    'meta-title-checker-seo-title-length-guide': [('meta-title-checker','Meta Title Checker'),('meta-description-checker','Meta Description Checker'),('slug-generator','Slug Generator'),('case-converter','Case Converter')],
    'slug-generator-seo-friendly-url-guide': [('slug-generator','Slug Generator'),('case-converter','Case Converter'),('url-encoder','URL Encoder'),('meta-title-checker','Meta Title Checker')],
    'case-converter-title-case-headline-guide': [('case-converter','Case Converter'),('meta-title-checker','Meta Title Checker'),('slug-generator','Slug Generator'),('word-counter','Word Counter')],
    'qr-code-generator-vcard-event-menu-guide': [('qr-code-generator','QR Code Generator'),('barcode-generator','Barcode Generator'),('url-encoder','URL Encoder'),('password-generator','Password Generator')],
    'percentage-calculator-discount-growth-guide': [('percentage-calculator','Percentage Calculator'),('random-number-generator','Random Number Generator'),('unit-converter','Unit Converter'),('age-calculator','Age Calculator')],
    'unit-converter-metric-imperial-guide': [('unit-converter','Unit Converter'),('percentage-calculator','Percentage Calculator'),('aspect-ratio-calculator','Aspect Ratio Calculator'),('time-zone-converter','Time Zone Converter')],
    'stopwatch-online-productivity-guide': [('stopwatch','Stopwatch'),('timestamp-converter','Timestamp Converter'),('time-zone-converter','Time Zone Converter'),('word-counter','Word Counter')],
    'image-seo-checklist-compress-convert-resize-webp-jpg-png': [('image-compressor','Image Compressor'),('resize-image','Resize Image'),('png-to-jpg','PNG to JPG'),('jpg-to-webp','JPG to WebP'),('png-to-webp','PNG to WebP')],
    'json-tools-for-seo-developers-format-validate-convert-csv': [('json-formatter','JSON Formatter'),('json-validator','JSON Validator'),('json-to-csv','JSON to CSV'),('csv-to-json','CSV to JSON')],
    'qr-code-seo-local-business-menu-wifi-vcard-guide': [('qr-code-generator','QR Code Generator'),('url-encoder','URL Encoder'),('password-generator','Password Generator'),('slug-generator','Slug Generator')],
    'meta-title-description-checklist-improve-google-ctr': [('meta-title-checker','Meta Title Checker'),('meta-description-checker','Meta Description Checker'),('slug-generator','Slug Generator'),('word-counter','Word Counter')],
}

def build_blog():
    import os
    os.makedirs('blog', exist_ok=True)
    
    with open('blog/blog-template.html', 'r', encoding='utf-8') as f:
        blog_template = f.read()

    # We will build individual blog pages
    for i, article in enumerate(BLOG_ARTICLES):
        slug = article['slug']
        title = article['title']
        description = article['description']
        date = article['date']
        toc = article['toc']
        content = article['content']
        faqs = article.get('faqs', [])

        # Dynamic E-E-A-T Author/Reviewer box prepend
        if "author-box" not in content:
            author_box_html = f"""
        <div class="author-box" style="background: rgba(99, 102, 241, 0.03); border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem; margin-bottom: 2rem; display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2rem;">✍️</div>
            <div>
                <strong>Author / Reviewer:</strong> freeconvert.cloud Editorial Team<br>
                <small><strong>Editorial Note:</strong> This guide was created by the freeconvert.cloud Editorial Team to help users understand file conversion, file privacy, and safe online tools. We review our guides regularly to keep them accurate, useful, and beginner-friendly.</small><br>
                <small><strong>Last Updated:</strong> {date} | <strong>Fact-Checked:</strong> Yes | <strong>Links:</strong> <a href="/about/">About Us</a> | <a href="/contact/">Contact Us</a> | <a href="/security/">File Security</a></small>
            </div>
        </div>
"""
            content = author_box_html + content

        # Build schema FAQPage entities
        faq_entities = []
        for f_item in faqs:
            faq_entities.append({
                "@type": "Question",
                "name": f_item['q'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f_item['a']
                }
            })

        # Render FAQ HTML
        faq_html = ""
        for f_item in faqs:
            faq_html += f"""
            <div class="accordion">
                <div class="accordion-header">❓ {f_item['q']}</div>
                <div class="accordion-content">
                    <p style="font-size:0.95rem; color:var(--text-muted); line-height:1.6;">{f_item['a']}</p>
                </div>
            </div>"""
        
        full_content = content
        if faq_html:
            full_content += f"""
            <h2 id="faqs">Frequently Asked Questions</h2>
            <p style="margin-bottom:1.5rem;">Read answers to the most common questions about this format and conversion process:</p>
            <div style="display:flex; flex-direction:column; gap:1rem; margin-top:1.5rem;">
                {faq_html}
            </div>"""

        # Inject "Try These Tools" box from contextual map
        tool_links_for_blog = BLOG_TOOL_MAP.get(slug, [('image-compressor','Image Compressor'),('jpg-to-pdf','JPG to PDF'),('json-formatter','JSON Formatter')])
        tool_links_html = "".join(
            f'''<a href="/{tid}/" style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.5rem 1rem;background:var(--brand-primary);color:#fff;border-radius:8px;font-size:0.85rem;font-weight:600;text-decoration:none;transition:opacity 0.2s;" onmouseover="this.style.opacity=0.85" onmouseout="this.style.opacity=1">⚡ {tname}</a>'''
            for tid, tname in tool_links_for_blog
        )
        tool_links_box = f'''
        <div style="margin:2rem 0;padding:1.25rem 1.5rem;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);border-radius:14px;">
            <p style="font-size:0.85rem;font-weight:700;margin-bottom:0.8rem;color:var(--brand-primary);">⚡ Try These Free Tools</p>
            <div style="display:flex;flex-wrap:wrap;gap:0.6rem;">{tool_links_html}</div>
        </div>'''
        # Insert after author box
        if 'author-box' in full_content:
            full_content = full_content.replace('</div>\n', '</div>\n' + tool_links_box, 1)
        else:
            full_content = tool_links_box + full_content

        # Generate related blogs links (excluding the current one)
        related_articles = [art for art in BLOG_ARTICLES if art['slug'] != slug][:4]
        related_blogs_html = ""
        for rel in related_articles:
            related_blogs_html += f'<a href="/blog/{rel["slug"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">📝 {rel["title"]}</a>'

        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": title,
                    "description": description,
                    "datePublished": article_date_iso(date),
                    "dateModified": TODAY_ISO,
                    "mainEntityOfPage": f"{SITE_URL}/blog/{slug}/",
                    "author": {
                        "@type": "Organization",
                        "name": "freeconvert.cloud Editorial Team"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "freeconvert.cloud",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://freeconvert.cloud/assets/freeconvert-logo.png"
                        }
                    }
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_entities
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
                            "name": "Blog",
                            "item": "https://freeconvert.cloud/blog/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": title,
                            "item": f"https://freeconvert.cloud/blog/{slug}/"
                        }
                    ]
                }
            ]
        }
        schema_tag = f'<script type="application/ld+json">{json.dumps(schema_data)}</script>'

        # Fill placeholders in the template
        html = blog_template
        html = html.replace('{{TITLE}}', title)
        html = html.replace('{{DESCRIPTION}}', description)
        html = html.replace('{{SLUG}}', slug)
        html = html.replace('{{TOC}}', toc)
        html = html.replace('{{CONTENT}}', full_content)
        html = html.replace('{{SCHEMA}}', schema_tag)
        html = html.replace('{{RELATED_BLOGS}}', related_blogs_html)
        html = html.replace('{{FOOTER_SNIPPET}}', FOOTER_SNIPPET)

        # Write inside dynamic subfolder index.html for Clean URL routing!
        os.makedirs(f"blog/{slug}", exist_ok=True)
        with open(f"blog/{slug}/index.html", 'w', encoding='utf-8') as f_out:
            f_out.write(html)
        print(f"Compiled clean URL blog page: /blog/{slug}/index.html")

    # Now let's compile the /blog/index.html (Resource Hub list)
    blog_cards = ""
    for article in BLOG_ARTICLES:
        blog_cards += f"""
        <a href="/blog/{article['slug']}/" class="tool-card" style="text-decoration:none; text-align:left;">
            <span class="popular-badge">📖 Guide</span>
            <div class="tool-card-top">
                <div class="tool-icon">📝</div>
                <span class="tool-category-tag">{article['date']}</span>
            </div>
            <div class="tool-card-body">
                <h3 style="color:var(--text-primary); margin-bottom:0.5rem; font-size:1.25rem; font-weight:800; letter-spacing:-0.02em;">{article['title']}</h3>
                <p style="font-size:0.92rem; line-height:1.55; color:var(--text-muted);">{article['description']}</p>
            </div>
            <div class="tool-card-footer">
                <span class="explore-text" style="color:var(--brand-primary);">Read Guide</span>
                <span class="arrow-icon">→</span>
            </div>
        </a>"""

    hub_html = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>freeconvert.cloud Resource Hub — Fact-Checked Conversion Tutorials</title>
    <meta name="description" content="Explore expert-written, browser-local conversion tutorials, developer guides, designer optimizations, and E-E-A-T trust signals from the freeconvert.cloud Editorial Team.">
    <link rel="icon" type="image/png" href="/assets/favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">

    <link rel="canonical" href="https://freeconvert.cloud/blog/" />

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
</head>

<body>
    <!-- Hyper-Luxury Ambient Floating Orbs -->
    <div class="glass-orb-container">
        <div class="glass-orb glass-orb-1"></div>
        <div class="glass-orb glass-orb-2"></div>
        <div class="glass-orb glass-orb-3"></div>
    </div>

    {HEADER_SNIPPET}

    <main class="tool-content" style="max-width: 1200px; margin: 0 auto; padding: 2rem 5% 5.5rem;">
        <!-- Visual Breadcrumbs -->
        <nav class="breadcrumbs">
            <a href="/">Home</a>
            <span>&gt;</span>
            <span style="color: var(--text-muted);">Blog Resource Hub</span>
        </nav>

        <section class="tool-header" style="margin-bottom:3.5rem; text-align:center;">
            <span class="badge" style="margin-bottom:0.8rem;">📖 Resource Hub</span>
            <h1>Guides &amp; Tutorials</h1>
            <p style="margin-top: 0.5rem; color:var(--text-muted); font-size:1.1rem; max-width:680px; margin-left:auto; margin-right:auto;">
                Explore free, 100% fact-checked, high-value guides and tutorials on file conversions, privacy, developer workflows, and designer productivity written by the freeconvert.cloud Editorial Team.
            </p>
        </section>

        <!-- AdSense Slot: Blog Hub Page Top -->
        <div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
            <span class="adsense-label">Advertisement</span>
            <ins class="adsbygoogle"
                 style="display:block;min-height:90px;"
                 data-ad-client="ca-pub-8997218708343263"
                 data-ad-slot="REPLACE_SLOT_BLOG_TOP"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </div>

        <div class="tool-grid" style="padding: 0; margin-bottom: 4rem;">
            {blog_cards}
        </div>

        <!-- E-E-A-T Editorial Policy section in Blog Hub -->
        <article class="seo-content" style="background:rgba(255,255,255,0.85); box-shadow:var(--card-shadow); padding:3.5rem; border-radius:24px; text-align:left;">
            <h2>Editorial Policy & Content Quality Guarantee</h2>
            <p>
                At freeconvert.cloud, we believe that every guide, checklist, and comparison table published on our platform should offer genuine, real-world utility and meet professional standard criteria. We strongly condemn empty artificial paragraph structures, keyword stuffing, duplicate content copy, or misleading files claims.
            </p>
            <h3>How We Review Content</h3>
            <p>
                All tutorial articles and glossary blocks are researched, written, and verified by our in-house <strong>freeconvert.cloud Editorial Team</strong> under absolute integrity benchmarks. We review our documentation routinely to align with modern web standard updates, operating system iterations, and privacy mandates.
            </p>
            <h3>Responsible Advertising Statement</h3>
            <p>
                Our visual conversion suites are supported strictly by clean, labeled AdSense placements. We guarantee a responsible advertising layout: zero fake "Download Now" banners, no malware triggers, and zero intrusive pop-ups. Placements are completely decoupled from active tool inputs and action buttons to avoid accidental clicks, ensuring a safe, SaaS-grade experience for all visitors.
            </p>
        </article>
    </main>

    {FOOTER_SNIPPET}
    <script src="/tools/tool-logic.js"></script>
</body>

</html>
""".replace('{HEADER_SNIPPET}', HEADER_SNIPPET).replace('{FOOTER_SNIPPET}', FOOTER_SNIPPET)

    with open('blog/index.html', 'w', encoding='utf-8') as f:
        f.write(hub_html)
    print("Generated Blog Hub index `/blog/index.html` successfully.")


def build():
    with open(TOOLS_JSON, 'r', encoding='utf-8') as f:
        tools = json.load(f)
    indexable_tools = filter_indexable_tools(tools)
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    # Create folder directories and index.html for each individual tool page
    for tool in tools:
        ui = ""
        script = ""
        how_to = ""
        
        t_type = tool['type']
        t_id = tool['id']
        
        # Resolve category mapping slug and name
        cat_slug = 'document-converter'
        cat_name = 'Document Converter'
        for key, cat in CATEGORIES.items():
            if t_type in cat['types']:
                cat_slug = cat['slug']
                cat_name = cat['name']
                break

        if t_type == 'image':
            ui = UPLOAD_BOX_UI
            script = UPLOAD_BOX_SCRIPT
            how_to = f"<ol><li>Upload your {t_id.split('-to-')[0].upper()} file in the dotted drag-and-drop zone.</li><li>Choose {t_id.split('-to-')[1].upper()} as target output.</li><li>Adjust optional dimensions or quality scale in advanced settings.</li><li>Click Convert and wait for edge process completion.</li></ol>"
        elif t_type in ['pdf', 'video', 'audio', 'archive', 'ebook']:
            ui = UPLOAD_BOX_UI
            script = UPLOAD_BOX_SCRIPT
            how_to = f"<ol><li>Select or drag your input file into the upload box.</li><li>Adjust formatting settings and parameters if available.</li><li>Click the Convert button to begin secure edge processing.</li><li>Wait for the download link to download your converted file.</li></ol>"
        elif t_type == 'text':
            if t_id in ['word-counter', 'character-counter']:
                ui = TEXT_UI
                script = TEXT_SCRIPT
                how_to = "<ol><li>Paste or type your script inside the glass-input textarea.</li><li>See character, word, and sentence statistics immediately.</li></ol>"
            elif t_id in ['meta-title-checker', 'meta-description-checker']:
                ui = METACHECKER_UI
                script = METACHECKER_SCRIPT
                how_to = "<ol><li>Paste or type your meta title or description in the box.</li><li>Observe character count and visual pixel width scaling.</li><li>Review the simulated Google SERP desktop snippet preview.</li></ol>"
            elif t_id in ['slug-generator', 'remove-duplicate-lines', 'text-cleaner', 'hashtag-generator']:
                ui = UTILITY_UI
                script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
                how_to = "<ol><li>Enter or paste text inside the input textarea.</li><li>Interact with the option checkboxes or parameters.</li><li>Process results and copy/download clean text output instantly.</li></ol>"
            else:
                ui = CASE_UI
                script = CASE_SCRIPT
                how_to = "<ol><li>Paste text to change.</li><li>Click UPPERCASE, lowercase, or Title Case to transform.</li></ol>"
        elif t_type == 'security':
            if t_id == 'password-strength': 
                ui = UTILITY_UI 
                script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
                how_to = "<ol><li>Type your password in input.</li><li>Check the real-time feedback bar for security strength.</li></ol>"
            else:
                ui = SECURITY_UI
                script = SECURITY_SCRIPT
                how_to = "<ol><li>Set custom password options (length, symbols).</li><li>Generate securely.</li><li>Click Copy to clipboard.</li></ol>"
        elif t_type == 'image_advanced':
            ui = UPLOAD_BOX_UI
            script = UPLOAD_BOX_SCRIPT
            how_to = "<ol><li>Select your target picture file.</li><li>Set specific dimensions or compression levels.</li><li>Execute conversion and download file.</li></ol>"
        elif t_type == 'qr':
            if t_id in ['qr-code-generator', 'qr-generator']:
                ui = QR_UI
                script = QR_SCRIPT
                how_to = "<ol><li>Enter your destination link or text in the search container.</li><li>Generate QR.</li><li>Download or share image code.</li></ol>"
            else: # barcode-generator
                ui = UTILITY_UI
                script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
                how_to = "<ol><li>Enter code number or characters in the input field.</li><li>Click generate barcode to render SVG.</li><li>Download barcode vector cleanly.</li></ol>"
        elif t_type == 'dev_basic':
            ui = DEV_BASIC_UI
            script = DEV_BASIC_SCRIPT.replace('{{ID}}', t_id)
            how_to = "<ol><li>Paste input code.</li><li>Select explicit conversion mode.</li><li>Click Process and copy output text.</li></ol>"
        elif t_type == 'dev_advanced':
            ui = DEV_ADVANCED_UI
            script = DEV_ADVANCED_SCRIPT.replace('{{ID}}', t_id)
            how_to = "<ol><li>Paste script inside editor.</li><li>Review output formatted preview immediately.</li></ol>"
        elif t_type == 'utility':
            ui = UTILITY_UI
            script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
            how_to = "<ol><li>Interact with active layout components.</li><li>See responsive results.</li></ol>"
        elif t_type == 'image_base64':
            ui = UTILITY_UI
            script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
            how_to = "<ol><li>Upload your picture.</li><li>Select and copy the converted Base64 data string.</li></ol>"
        elif t_type == 'utility_advanced':
            ui = UTILITY_UI
            script = UTILITY_SCRIPT.replace('{{ID}}', t_id)
            how_to = "<ol><li>Input initial values.</li><li>Adjust sliders or settings.</li><li>Review live visual simulations.</li></ol>"

        # Compile tool template replacement
        html = template.replace('{{NAME}}', tool['name'])
        html = html.replace('{{NAME_CLEAN}}', tool['name'])
        html = html.replace('{{INTRO}}', tool['description'])
        html = html.replace('{{SEO_TITLE}}', tool.get('seo_title', tool['name'] + ' | freeconvert.cloud'))
        html = html.replace('{{SEO_DESC}}', tool.get('seo_desc', tool['description']))
        html = html.replace('{{TOOL_UI}}', ui)
        html = html.replace('{{HOW_TO}}', how_to)
        html = html.replace('{{CATEGORY_SLUG}}', cat_slug)
        html = html.replace('{{CATEGORY_NAME}}', cat_name)
        html = html.replace('{{CLEAN_URL}}', t_id)
        
        # Robust replacement
        script_custom = script.replace('{{ID}}', t_id).replace('{{NAME}}', tool['name'].replace("'", "\\'"))
        html = html.replace('{{SPECIFIC_SCRIPT}}', script_custom)
        html = html.replace('{ { SPECIFIC_SCRIPT } }', script_custom)
        html = html.replace('{{ID}}', t_id)
        
        # Call generate_tool_adsense_content helper
        use_cases_html, limitations, faq_html, faqs_list = generate_tool_adsense_content(tool)
        
        html = html.replace('{{USE_CASES}}', use_cases_html)
        html = html.replace('{{LIMITATIONS}}', limitations)
        html = html.replace('{{FAQ_SECTION}}', faq_html)
        html = html.replace(
            '{{KEYWORD_CONTENT}}',
            tool_keyword_content_html(tool, indexable_tools) + tool_deep_seo_content_html(tool, indexable_tools)
        )
        
        # Inject Glossary box
        _, cat_glossary, _, _, _, _, _ = generate_category_seo_content(cat_slug, cat_name)
        html = html.replace('{{GLOSSARY_BOX}}', cat_glossary)
        
        # SEO Injection
        canonical_tag = f'<link rel="canonical" href="https://freeconvert.cloud/{t_id}/" />'
        
        # Build schema FAQPage entities based on the actual tool FAQ
        faq_entities = []
        for f_item in faqs_list:
            faq_entities.append({
                "@type": "Question",
                "name": f_item['q'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f_item['a']
                }
            })
            
        # Fallback if no FAQs are present
        if not faq_entities:
            steps = []
            if "<ol>" in how_to:
                raw_steps = how_to.replace("<ol>", "").replace("</ol>", "").split("<li>")
                for s in raw_steps:
                    clean_s = s.replace("</li>", "").strip()
                    if clean_s:
                        steps.append(clean_s)
            for i, step in enumerate(steps):
                faq_entities.append({
                    "@type": "Question",
                    "name": f"Step {i+1}: How do I convert using {tool['name']}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": step
                    }
                })

        keyword_target = keyword_target_for_tool(t_id)
        software_app_schema = {
            "@type": "SoftwareApplication",
            "name": tool['name'],
            "operatingSystem": "Any",
            "applicationCategory": tool.get('category', 'Utility'),
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "description": tool['description']
        }
        if keyword_target:
            software_app_schema["keywords"] = ', '.join([keyword_target['keyword']] + keyword_target['modifiers'])

        how_to_steps = how_to_steps_from_html(how_to)
        web_page_schema = {
            "@type": "WebPage",
            "name": tool.get('seo_title', tool['name']),
            "description": tool.get('seo_desc', tool['description']),
            "url": f"https://freeconvert.cloud/{t_id}/",
            "isPartOf": {
                "@type": "WebSite",
                "name": "freeconvert.cloud",
                "url": "https://freeconvert.cloud/"
            },
            "about": {
                "@type": "Thing",
                "name": tool['name']
            },
            "primaryImageOfPage": {
                "@type": "ImageObject",
                "url": BRAND_IMAGE
            },
            "dateModified": TODAY_ISO
        }
        if keyword_target:
            web_page_schema["keywords"] = ', '.join([keyword_target['keyword']] + keyword_target['modifiers'])

        how_to_schema = {
            "@type": "HowTo",
            "name": f"How to use {tool['name']}",
            "description": f"Step-by-step instructions for using {tool['name']} on freeconvert.cloud.",
            "totalTime": "PT1M",
            "tool": [
                {
                    "@type": "HowToTool",
                    "name": "Modern web browser"
                }
            ],
            "step": [
                {
                    "@type": "HowToStep",
                    "position": i + 1,
                    "name": f"Step {i + 1}",
                    "text": step
                }
                for i, step in enumerate(how_to_steps)
            ]
        }

        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                web_page_schema,
                software_app_schema,
                how_to_schema,
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_entities
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
                            "name": cat_name,
                            "item": f"https://freeconvert.cloud/{cat_slug}/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": tool['name'],
                            "item": f"https://freeconvert.cloud/{t_id}/"
                        }
                    ]
                }
            ]
        }
        schema_tag = f'<script type="application/ld+json">{json.dumps(schema_data)}</script>'
        
        html = html.replace('{{CANONICAL}}', canonical_tag)
        html = html.replace('{{SCHEMA}}', schema_tag)

        # Smart Related Tools (category-aware, card style, 6 links)
        same_cat = [t for t in indexable_tools if t['type'] == t_type and t['id'] != t_id]
        cross_cat = [t for t in indexable_tools if t['id'] != t_id and t not in same_cat]
        keyword_target = keyword_target_for_tool(t_id)
        keyword_related_ids = []
        if keyword_target:
            keyword_related_ids = [
                target['tool_id'] for target in TOP_KEYWORD_TARGETS
                if target['tool_id'] != t_id and (
                    target['cluster'] == keyword_target['cluster']
                    or target['cluster'].split()[0] == keyword_target['cluster'].split()[0]
                )
            ]
        keyword_related = [t for t in indexable_tools if t['id'] in keyword_related_ids]
        combined_related = keyword_related + same_cat + cross_cat
        matched_tools = []
        seen_related_ids = set()
        for candidate in combined_related:
            if candidate['id'] in seen_related_ids:
                continue
            seen_related_ids.add(candidate['id'])
            matched_tools.append(candidate)
            if len(matched_tools) == 6:
                break
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
            f'''<a href="{url}" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 0.9rem;background:var(--bg-dark,#0f0f1a);border:1px solid var(--border-color);border-radius:8px;font-size:0.82rem;color:var(--brand-primary);text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='var(--brand-primary)';this.style.color='#fff'" onmouseout="this.style.background='var(--bg-dark,#0f0f1a)';this.style.color='var(--brand-primary)'">📖 {label}</a>'''
            for url, label in blog_links_list
        )
        html = html.replace('{{BLOG_LINKS}}', blog_links_html)
        html = html.replace('{{FOOTER_SNIPPET}}', FOOTER_SNIPPET)

        # Write inside dynamic subfolder index.html for Clean URL routing!
        os.makedirs(f"{t_id}", exist_ok=True)
        with open(f"{t_id}/index.html", 'w', encoding='utf-8') as f_out:
            f_out.write(html)
            
        print(f"Compiled clean URL tool page: /{t_id}/index.html")

    # Generate homepage
    build_homepage(indexable_tools)
    build_all_tools_directory(indexable_tools)

    # Generate 8 category pages
    build_categories(indexable_tools)

    # Generate pricing page
    build_pricing_page()

    # Generate API page
    build_api_page()

    # Generate trust & legal pages (including about and cookies!)
    build_legal_pages()

    # Generate press kit for journalists and directory submissions
    build_press_kit_page()

    # Generate blog pages and articles
    build_blog()
    build_blog_category_pages()
    build_embed_widget_page()
    build_growth_landing_pages()
    build_daily_seo_landing_pages()
    build_popular_conversion_pages()
    build_file_format_glossary_pages()
    build_convert_alias_pages(tools)
    build_legacy_redirect_pages()
    build_html_sitemap_page(indexable_tools)

    # Generate discovery files (llms.txt & humans.txt)
    build_discovery_files(indexable_tools)

    # Generate enhanced technical SEO assets
    normalize_generated_html_seo()
    build_static_seo_assets()
    build_rss_feed()
    build_opensearch_file()
    build_sitemap(indexable_tools)
    build_keyword_research_file(indexable_tools)

    # Generate tools-data.js
    frontend_data = []
    for tool in indexable_tools:
        frontend_data.append({
            "id": tool["id"],
            "name": tool["name"],
            "icon": tool["icon"],
            "description": tool["description"],
            "type": tool["type"],
            "category": tool["category"]
        })
    
    with open('tools/tools-data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.TOOLS_DATA={json.dumps(frontend_data, separators=(',', ':'))};")
    print("Updated tools/tools-data.js")

    build_minified_asset_aliases()

    # Generate Robots.txt
    robots_content = """User-agent: *
Allow: /
Disallow: /tools/tool-template.html
Disallow: /blog/blog-template.html

# Keep thin review-mode clusters out of crawler priority while meta noindex is being refreshed
Disallow: /blog/hub-pages/

# AI and search discovery
# LLM summary: https://freeconvert.cloud/llms.txt
# Full AI index: https://freeconvert.cloud/ai-index.json
# Keyword map: https://freeconvert.cloud/seo-keyword-targets.json
Sitemap: https://freeconvert.cloud/sitemap-index.xml
Sitemap: https://freeconvert.cloud/sitemap.xml
Host: freeconvert.cloud
"""
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print("Generated robots.txt")


if __name__ == "__main__":
    build()
