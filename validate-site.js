/**
 * Quick site-wide validation for common SEO/AdSense issues.
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const SITE_URL = 'https://freeconvert.cloud';

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

for (const file of htmlFiles) {
    const html = fs.readFileSync(file, 'utf-8');
    const rel = path.relative(ROOT, file).replace(/\\/g, '/');

    if (html.includes('pagead2.googlesyndication.com')) stats.adsenseScript++;
    if (html.includes('<link rel="canonical"')) stats.canonical++;
    if (html.includes('<title>')) stats.title++;
    if (html.includes('name="description"')) stats.description++;
    if (html.includes('application/ld+json')) stats.schema++;
    if (html.includes('name="robots"') && html.includes('noindex')) stats.noIndex++;

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
