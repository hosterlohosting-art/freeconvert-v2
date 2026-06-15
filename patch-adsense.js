/**
 * Patch existing generated HTML files with AdSense infrastructure and
 * performance fixes without requiring a full Python rebuild.
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const ADSENSE_CLIENT = 'ca-pub-8997218708343263';

const ADSENSE_HEAD = `    <!-- AdSense preconnects -->
    <link rel="preconnect" href="https://pagead2.googlesyndication.com">
    <link rel="dns-prefetch" href="//pagead2.googlesyndication.com">
    <link rel="preconnect" href="https://googleads.g.doubleclick.net">
    <link rel="dns-prefetch" href="//googleads.g.doubleclick.net">

    <!-- AdSense script (loads async; ad units hidden via CSS until approved) -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}" crossorigin="anonymous"></script>`;

const AD_UNITS = {
    'tool-mid': `<div class="adsense-wrap">
    <span class="adsense-label">Advertisement</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_MID_CONTENT"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`,
    'footer': `<div class="adsense-wrap footer-ad-wrap">
    <span class="adsense-label">Sponsored Links</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_FOOTER"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`,
    'home-top': `<div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
    <span class="adsense-label">Advertisement</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_HOME_TOP"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`,
    'cat-top': `<div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
    <span class="adsense-label">Advertisement</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_CAT_TOP"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`,
    'legal-mid': `<div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
    <span class="adsense-label">Advertisement</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_LEGAL_MID"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`,
    'blog-top': `<div class="adsense-wrap" style="margin-top: 0; margin-bottom: 3.5rem;">
    <span class="adsense-label">Advertisement</span>
    <ins class="adsbygoogle"
         style="display:block;min-height:90px;"
         data-ad-client="${ADSENSE_CLIENT}"
         data-ad-slot="REPLACE_SLOT_BLOG_TOP"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>`
};

const OLD_PLACEHOLDER_REGEX = /<div class="adsense-placeholder-wrap"[^>]*>[\s\S]*?<\/div>\s*<\/div>/g;
const OLD_FOOTER_PLACEHOLDER_REGEX = /<div class="adsense-placeholder-wrap footer-ad-wrap"[^>]*>[\s\S]*?<\/div>\s*<\/div>/g;

function findHtmlFiles(dir, files = []) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            // Skip hidden dirs, node_modules, git, etc.
            if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === '__pycache__') continue;
            findHtmlFiles(fullPath, files);
        } else if (entry.name === 'index.html') {
            files.push(fullPath);
        }
    }
    return files;
}

function patchFile(filePath) {
    let html = fs.readFileSync(filePath, 'utf-8');
    let modified = false;

    // 1. Inject AdSense head snippet after gtag config if not already present
    if (!html.includes('pagead2.googlesyndication.com')) {
        const gtagEnd = html.indexOf("gtag('config', 'G-8XCZT6R7PL');");
        if (gtagEnd !== -1) {
            const insertPos = html.indexOf('</script>', gtagEnd) + '</script>'.length;
            html = html.slice(0, insertPos) + '\n' + ADSENSE_HEAD + html.slice(insertPos);
            modified = true;
        }
    }

    // 2. Replace old placeholder boxes with real AdSense units based on context
    if (html.includes('adsense-placeholder-wrap')) {
        const relPath = path.relative(ROOT, filePath).replace(/\\/g, '/');

        // Footer placeholder
        if (html.includes('footer-ad-wrap')) {
            html = html.replace(OLD_FOOTER_PLACEHOLDER_REGEX, AD_UNITS['footer']);
        }

        // Tool page mid-content placeholder (inside article.seo-content)
        if (relPath.split('/').length === 2 && !relPath.startsWith('blog/') && !relPath.startsWith('popular-conversions/') && !relPath.startsWith('free-online-converter-guides/') && !relPath.startsWith('file-formats/')) {
            html = html.replace(OLD_PLACEHOLDER_REGEX, AD_UNITS['tool-mid']);
        }

        // Homepage
        if (relPath === 'index.html') {
            html = html.replace(OLD_PLACEHOLDER_REGEX, AD_UNITS['home-top']);
        }

        // Category pages (e.g., /image-converter/index.html)
        const catPages = ['image-converter', 'video-converter', 'audio-converter', 'document-converter', 'pdf-tools', 'archive-converter', 'ebook-converter', 'unit-converter'];
        if (catPages.some(c => relPath === `${c}/index.html`)) {
            html = html.replace(OLD_PLACEHOLDER_REGEX, AD_UNITS['cat-top']);
        }

        // Legal pages
        const legalPages = ['about', 'contact', 'privacy', 'terms', 'security', 'cookies', 'dmca', 'advertising-policy', 'help', 'api', 'pricing'];
        if (legalPages.some(p => relPath === `${p}/index.html`)) {
            html = html.replace(OLD_PLACEHOLDER_REGEX, AD_UNITS['legal-mid']);
        }

        // Blog hub
        if (relPath === 'blog/index.html') {
            html = html.replace(OLD_PLACEHOLDER_REGEX, AD_UNITS['blog-top']);
        }

        modified = true;
    }

    // 3. Add width/height to logo img if missing
    if (html.includes('/assets/freeconvert-logo.png') && !html.includes('width="512" height="512"')) {
        html = html.replace(
            /<img src="\/assets\/freeconvert-logo\.png" alt="freeconvert\.cloud[^"]*" class="logo-img" style="height:38px;width:auto;display:block;"/g,
            '<img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud privacy-first online file converter" class="logo-img" width="512" height="512" style="height:38px;width:auto;display:block;"'
        );
        modified = true;
    }

    // 4. Lazy-load footer logo and other below-fold images
    html = html.replace(
        /<img src="\/assets\/freeconvert-logo\.png" alt="freeconvert\.cloud[^"]*" style="height:36px;width:auto;margin-bottom:0\.75rem;display:block;"/g,
        '<img src="/assets/freeconvert-logo.png" alt="freeconvert.cloud privacy-first online file converter" width="512" height="512" style="height:36px;width:auto;margin-bottom:0.75rem;display:block;" loading="lazy" decoding="async"'
    );

    if (modified) {
        fs.writeFileSync(filePath, html, 'utf-8');
        return true;
    }
    return false;
}

const htmlFiles = findHtmlFiles(ROOT);
let patched = 0;
for (const file of htmlFiles) {
    try {
        if (patchFile(file)) {
            console.log('Patched:', path.relative(ROOT, file));
            patched++;
        }
    } catch (err) {
        console.error('Error patching', file, err.message);
    }
}
console.log(`\nPatched ${patched} files out of ${htmlFiles.length} scanned.`);
