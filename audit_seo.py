"""Fail-fast technical SEO checks for the generated static site."""

from pathlib import Path
from urllib.parse import urlparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent
SITE_URL = 'https://freeconvert.cloud'
SITEMAPS = ('sitemap.xml', 'sitemaps/pages.xml', 'sitemaps/tools.xml', 'sitemaps/blog.xml')
URLSET_NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
LEGACY_PATHS = {
    'about-freeconvert/index.html',
    'base64-tool/index.html',
    'contact-us/index.html',
    'dev_basic/index.html',
    'image-resizer/index.html',
    'lorem-ipsum/index.html',
    'qr-generator/index.html',
    '2025/11/02/hello-world/index.html',
    '2025/12/18/qr-codes-on-business-cards/index.html',
}


def public_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == 'index.html':
        return f'{SITE_URL}/'
    return f'{SITE_URL}/{relative[:-11]}/'


def meta_content(page: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+[^>]*(?:name|property)=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)',
        page,
        re.IGNORECASE,
    )
    return match.group(1) if match else ''


def main() -> int:
    issues = []
    pages = [
        page for page in ROOT.rglob('index.html')
        if '.git' not in page.parts and '__pycache__' not in page.parts
    ]
    indexed_pages = 0

    for page_path in pages:
        page = page_path.read_text(encoding='utf-8')
        rel = page_path.relative_to(ROOT).as_posix()
        canonical_match = re.search(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', page, re.IGNORECASE)
        robots = meta_content(page, 'robots')
        expected = public_url(page_path)
        is_alias = rel.startswith('convert/') or rel in LEGACY_PATHS
        if not canonical_match:
            issues.append(f'{rel}: canonical is missing')
        elif canonical_match.group(1) != expected and not is_alias:
            issues.append(f'{rel}: canonical mismatch ({canonical_match.group(1)})')
        if not robots:
            issues.append(f'{rel}: robots meta is missing')
        elif is_alias and 'noindex' not in robots.lower():
            issues.append(f'{rel}: alias must be noindex')
        elif 'noindex' not in robots.lower():
            indexed_pages += 1

    sitemap_urls = set()
    for sitemap_name in SITEMAPS:
        sitemap_path = ROOT / sitemap_name
        if not sitemap_path.exists():
            issues.append(f'{sitemap_name}: file is missing')
            continue
        tree = ET.parse(sitemap_path)
        for node in tree.findall('s:url', URLSET_NS):
            loc = node.findtext('s:loc', namespaces=URLSET_NS)
            if not loc:
                issues.append(f'{sitemap_name}: URL entry has no loc')
                continue
            sitemap_urls.add(loc)
            relative = urlparse(loc).path.strip('/')
            target = ROOT / relative / 'index.html'
            if not target.exists():
                issues.append(f'{sitemap_name}: missing target {loc}')
                continue
            target_html = target.read_text(encoding='utf-8')
            if 'noindex' in meta_content(target_html, 'robots').lower():
                issues.append(f'{sitemap_name}: noindex target submitted {loc}')

    print(f'Checked {len(pages)} HTML pages, {indexed_pages} indexable pages, and {len(sitemap_urls)} sitemap URLs.')
    if issues:
        print('SEO_AUDIT_FAILED')
        print('\n'.join(issues[:50]))
        return 1
    print('SEO_AUDIT_OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
