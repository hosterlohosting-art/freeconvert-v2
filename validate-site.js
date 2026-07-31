/**
 * Quick site-wide validation for common SEO/AdSense issues.
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const SITE_URL = 'https://freeconvert.cloud';
const LEGACY_ALIAS_PATHS = new Set([
    'about-freeconvert/index.html', 'base64-tool/index.html', 'contact-us/index.html',
    'dev_basic/index.html', 'image-resizer/index.html', 'lorem-ipsum/index.html',
    'qr-generator/index.html', '2025/11/02/hello-world/index.html',
    '2025/12/18/qr-codes-on-business-cards/index.html'
]);

function findHtmlFiles(dir, files = []) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === '__pycache__') continue;
            findHtmlFiles(fullPath, files);
        } else if (entry.name === 'index.html') {
            files.push(fullPath);
        }
    }
    return files;
}

const htmlFiles = findHtmlFiles(ROOT);
const issues = [];
const stats = {
    total: htmlFiles.length,
    adsenseScript: 0,
    adsTxt: fs.existsSync(path.join(ROOT, 'ads.txt')),
    robotsTxt: fs.existsSync(path.join(ROOT, 'robots.txt')),
    sitemapIndex: fs.existsSync(path.join(ROOT, 'sitemap-index.xml')),
    canonical: 0,
    title: 0,
    description: 0,
    schema: 0,
    noIndex: 0
};

function getMetaContent(html, name) {
    const match = html.match(new RegExp(`<meta\\s+[^>]*(?:name|property)="${name}"[^>]*content="([^"]*)"`, 'i'))
        || html.match(new RegExp(`<meta\\s+[^>]*content="([^"]*)"[^>]*(?:name|property)="${name}"`, 'i'));
    return match ? match[1] : '';
}

for (const file of htmlFiles) {
    const html = fs.readFileSync(file, 'utf-8');
    const rel = path.relative(ROOT, file).replace(/\\/g, '/');

    if (html.includes('pagead2.googlesyndication.com')) stats.adsenseScript++;
    if (html.includes('<link rel="canonical"')) stats.canonical++;
    if (html.includes('<title>')) stats.title++;
    if (html.includes('name="description"')) stats.description++;
    if (html.includes('application/ld+json')) stats.schema++;
    const robots = getMetaContent(html, 'robots');
    const canonical = (html.match(/<link\s+[^>]*rel="canonical"[^>]*href="([^"]+)"/i) || [])[1];
    const expectedCanonical = rel === 'index.html'
        ? `${SITE_URL}/`
        : `${SITE_URL}/${rel.replace(/\/index\.html$/, '')}/`;
    if (/\bnoindex\b/i.test(robots)) stats.noIndex++;
    const isAlias = rel.startsWith('convert/') || LEGACY_ALIAS_PATHS.has(rel);
    if (canonical && canonical !== expectedCanonical && !isAlias) {
        issues.push(`${rel}: canonical mismatch (${canonical})`);
    }
    if (isAlias && !/\bnoindex\b/i.test(robots)) {
        issues.push(`${rel}: alias must remain noindex`);
    }

    // Check for broken internal links (href="/.../" that don't exist)
    const linkMatches = html.match(/href="\/([^"]+)\//g) || [];
    for (const match of linkMatches) {
        const href = match.replace('href="/', '').replace(/"$/, '');
        if (href.startsWith('http') || href.startsWith('#') || href.includes('?')) continue;
        const targetPath = path.join(ROOT, href, 'index.html');
        if (!fs.existsSync(targetPath) && !fs.existsSync(path.join(ROOT, href))) {
            // Some are files like /style.css or /tools/tool-logic.js
            const filePath = path.join(ROOT, href);
            if (!fs.existsSync(filePath)) {
                issues.push(`${rel}: broken link /${href}/`);
            }
        }
    }
}

// A sitemap must only contain canonical, indexable URLs. This catches the
// exact issue that wastes crawl attention on duplicate or review-only pages.
for (const sitemapFile of ['sitemap.xml', 'sitemaps/pages.xml', 'sitemaps/tools.xml', 'sitemaps/blog.xml']) {
    const sitemapPath = path.join(ROOT, sitemapFile);
    if (!fs.existsSync(sitemapPath)) continue;
    const sitemap = fs.readFileSync(sitemapPath, 'utf8');
    const urls = [...sitemap.matchAll(/<loc>(https:\/\/freeconvert\.cloud\/[^<]*)<\/loc>/g)].map(match => match[1]);
    for (const url of urls) {
        const pathname = new URL(url).pathname.replace(/^\//, '').replace(/\/$/, '');
        const htmlPath = path.join(ROOT, pathname, 'index.html');
        if (!fs.existsSync(htmlPath)) {
            issues.push(`${sitemapFile}: missing sitemap target ${url}`);
            continue;
        }
        const targetHtml = fs.readFileSync(htmlPath, 'utf8');
        if (/\bnoindex\b/i.test(getMetaContent(targetHtml, 'robots'))) {
            issues.push(`${sitemapFile}: noindex URL submitted ${url}`);
        }
    }
}

console.log('=== Validation Summary ===');
console.log(`Total HTML pages scanned: ${stats.total}`);
console.log(`AdSense script present:   ${stats.adsenseScript}/${stats.total}`);
console.log(`Canonical tags present:   ${stats.canonical}/${stats.total}`);
console.log(`Title tags present:       ${stats.title}/${stats.total}`);
console.log(`Meta descriptions present: ${stats.description}/${stats.total}`);
console.log(`JSON-LD schema present:   ${stats.schema}/${stats.total}`);
console.log(`Noindex pages:            ${stats.noIndex}`);
console.log(`ads.txt exists:           ${stats.adsTxt}`);
console.log(`robots.txt exists:        ${stats.robotsTxt}`);
console.log(`sitemap-index.xml exists: ${stats.sitemapIndex}`);
console.log('');

if (issues.length > 0) {
    console.log(`=== ${issues.length} potential issues ===`);
    issues.slice(0, 30).forEach(i => console.log(i));
    if (issues.length > 30) console.log(`... and ${issues.length - 30} more`);
} else {
    console.log('No obvious broken internal links found.');
}
