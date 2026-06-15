/**
 * Generate additional popular-conversions landing pages by cloning an existing page.
 */
const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://freeconvert.cloud';
const TODAY_ISO = '2026-06-15';

// Use an existing page as a template
const templatePath = 'popular-conversions/png-to-jpg-for-website/index.html';
let template = fs.readFileSync(templatePath, 'utf-8');

const newPages = [
    {
        slug: 'jpg-to-png-transparent-background',
        title: 'JPG to PNG Transparent Background',
        desc: 'Convert JPG images to PNG format so they support transparency for logos, overlays, and design projects.',
        keyword: 'JPG to PNG transparent background',
        tool: 'jpg-to-png',
        tool_label: 'JPG to PNG',
        problem: 'JPG images cannot have transparent backgrounds, which limits their use in designs and overlays.',
        best_for: 'Convert to PNG when you need transparency, then remove the background in an editor if needed.'
    },
    {
        slug: 'compress-image-to-200kb-online',
        title: 'Compress Image to 200KB Online',
        desc: 'Shrink image file size under 200KB for exam forms, job portals, visa uploads, and website performance.',
        keyword: 'compress image to 200KB online',
        tool: 'compress-image-to-200kb',
        tool_label: 'Compress Image to 200KB',
        problem: 'Government portals and job sites often reject images larger than 200KB.',
        best_for: 'Compress the image, check the final KB, and confirm the face or text remains clear.'
    },
    {
        slug: 'png-to-jpg-for-instagram',
        title: 'PNG to JPG for Instagram Posts',
        desc: 'Convert PNG designs and photos to JPG for faster Instagram uploads, stories, and carousel posts.',
        keyword: 'PNG to JPG for Instagram',
        tool: 'png-to-jpg',
        tool_label: 'PNG to JPG',
        problem: 'High-resolution PNG posts can be slow to upload and consume more mobile data.',
        best_for: 'Use JPG for photo posts where transparency is not needed.'
    },
    {
        slug: 'pdf-to-jpg-for-whatsapp',
        title: 'PDF to JPG for WhatsApp Sharing',
        desc: 'Convert PDF pages to JPG images for easy WhatsApp sharing, previews, and status updates.',
        keyword: 'PDF to JPG for WhatsApp',
        tool: 'pdf-to-jpg',
        tool_label: 'PDF to JPG',
        problem: 'WhatsApp previews PDFs differently and some contacts prefer image previews.',
        best_for: 'Convert key pages to JPG when you need a quick visual share.'
    },
    {
        slug: 'heic-to-jpg-on-iphone',
        title: 'HEIC to JPG on iPhone',
        desc: 'Convert iPhone HEIC photos to JPG directly on your phone for sharing, uploading, and editing anywhere.',
        keyword: 'HEIC to JPG on iPhone',
        tool: 'heic-to-jpg',
        tool_label: 'HEIC to JPG',
        problem: 'HEIC files may not open on older devices or upload forms.',
        best_for: 'Convert to JPG before sending photos to Android users or legacy systems.'
    },
    {
        slug: 'json-to-csv-for-excel',
        title: 'JSON to CSV for Excel',
        desc: 'Convert JSON data to CSV format for Excel analysis, pivot tables, and spreadsheet reporting.',
        keyword: 'JSON to CSV for Excel',
        tool: 'json-to-csv',
        tool_label: 'JSON to CSV',
        problem: 'Excel cannot import raw JSON arrays without conversion.',
        best_for: 'Flatten nested JSON and import the CSV into Excel or Google Sheets.'
    },
    {
        slug: 'password-generator-strong',
        title: 'Strong Password Generator',
        desc: 'Generate strong, random passwords with symbols, numbers, and mixed case for secure accounts.',
        keyword: 'strong password generator',
        tool: 'password-generator',
        tool_label: 'Password Generator',
        problem: 'Weak passwords are easily cracked by brute force and dictionary attacks.',
        best_for: 'Use 16+ characters with symbols for banking, email, and admin accounts.'
    },
    {
        slug: 'word-counter-for-essays',
        title: 'Word Counter for Essays',
        desc: 'Count words, characters, and paragraphs for essays, assignments, and social media posts.',
        keyword: 'word counter for essays',
        tool: 'word-counter',
        tool_label: 'Word Counter',
        problem: 'School and platform limits require exact word or character counts.',
        best_for: 'Paste your draft and check the count before submission.'
    },
    {
        slug: 'ico-converter-favicon',
        title: 'ICO Converter for Website Favicon',
        desc: 'Convert PNG or JPG images to ICO format for browser favicons and website bookmarks.',
        keyword: 'ICO converter favicon',
        tool: 'ico-converter',
        tool_label: 'ICO Converter',
        problem: 'Browsers require ICO or specific PNG sizes for favicons.',
        best_for: 'Upload a square logo and download a multi-size ICO file.'
    },
    {
        slug: 'image-compressor-for-website',
        title: 'Image Compressor for Website Speed',
        desc: 'Compress images for faster website loading, better Core Web Vitals, and improved SEO rankings.',
        keyword: 'image compressor for website',
        tool: 'image-compressor',
        tool_label: 'Image Compressor',
        problem: 'Large images slow down page load and hurt search rankings.',
        best_for: 'Compress hero images, product photos, and blog thumbnails before uploading.'
    },
];

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function replaceAll(str, find, replace) {
    return str.split(find).join(replace);
}

function generatePage(item) {
    let html = template;
    const oldSlug = 'png-to-jpg-for-website';
    const oldTitle = 'PNG to JPG for Website Images';
    const oldDesc = 'Convert heavy PNG website images into smaller JPG files for faster page speed, galleries, blog posts, and CMS uploads.';
    const oldKeyword = 'PNG to JPG for website';
    const oldTool = 'png-to-jpg';
    const oldToolLabel = 'PNG to JPG';
    const oldProblem = 'Large PNG photos can slow down landing pages, especially when transparency is not needed.';
    const oldBestFor = 'Use JPG for photographs, screenshots without transparency, blog images, and product previews where smaller delivery matters.';

    html = replaceAll(html, oldSlug, item.slug);
    html = replaceAll(html, escapeHtml(oldTitle), escapeHtml(item.title));
    html = replaceAll(html, escapeHtml(oldDesc), escapeHtml(item.desc));
    html = replaceAll(html, escapeHtml(oldKeyword), escapeHtml(item.keyword));
    html = replaceAll(html, `/${oldTool}/`, `/${item.tool}/`);
    html = replaceAll(html, escapeHtml(oldToolLabel), escapeHtml(item.tool_label));
    html = replaceAll(html, escapeHtml(oldProblem), escapeHtml(item.problem));
    html = replaceAll(html, escapeHtml(oldBestFor), escapeHtml(item.best_for));

    // Regenerate schema to match the new page
    const pageUrl = `${SITE_URL}/popular-conversions/${item.slug}/`;
    const schema = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'WebPage',
                name: item.title,
                url: pageUrl,
                description: item.desc,
                dateModified: TODAY_ISO,
                keywords: item.keyword,
                isPartOf: { '@type': 'CollectionPage', name: 'Popular Conversions', url: `${SITE_URL}/popular-conversions/` }
            },
            {
                '@type': 'HowTo',
                name: `How to use ${item.tool_label} for ${item.keyword}`,
                totalTime: 'PT1M',
                step: [
                    { '@type': 'HowToStep', position: 1, text: `Open the ${item.tool_label} tool.` },
                    { '@type': 'HowToStep', position: 2, text: 'Add your file or paste your content.' },
                    { '@type': 'HowToStep', position: 3, text: 'Review output settings and convert.' },
                    { '@type': 'HowToStep', position: 4, text: 'Download the result and check quality before sharing.' }
                ]
            }
        ]
    };

    // Replace the first schema block (the page-specific one)
    html = html.replace(/<script type="application\/ld\+json">\{[^}]*WebPage[^}]*HowTo[^}]*\}\]<\/script>/, `<script type="application/ld+json">${JSON.stringify(schema)}</script>`);

    // Update canonical
    html = replaceAll(html, `https://freeconvert.cloud/popular-conversions/${oldSlug}/`, pageUrl);

    return html;
}

for (const item of newPages) {
    const dir = path.join('popular-conversions', item.slug);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'index.html'), generatePage(item), 'utf-8');
    console.log('Generated /popular-conversions/' + item.slug + '/');
}

console.log(`Generated ${newPages.length} new popular conversion landing pages.`);
