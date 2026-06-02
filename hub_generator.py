import os
import json
from blog_data import BLOG_ARTICLES

TEMPLATE_PATH = 'blog/blog-template.html'
BLOG_DIR = 'blog/hub-pages'
TOPICS_FILE = 'blog/hub_topics.json'

if not os.path.exists(BLOG_DIR):
    os.makedirs(BLOG_DIR)

def generate_hub_page(topic):
    title = topic['title']
    tool_id = topic['tool_id']
    keywords = topic['keywords']
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    slug = title.lower().replace(' ', '-').replace('?', '')
    desc = f"Learn how to use our free online {title} tool. {keywords[0].capitalize()} safely, securely, and quickly in your browser."

    # Generate content optimized for Hub Page
    content = f"""
    <p>Are you looking for a way to <strong>{keywords[0]}</strong>? You've come to the right place. Our free online tool makes it easy to {title.lower()} in seconds.</p>
    
    <h2 id="why">Why use our {title} tool?</h2>
    <ul>
        <li><strong>Fast & Secure:</strong> All processing happens locally in your browser. No files are uploaded to any server.</li>
        <li><strong>Free Forever:</strong> No hidden costs, registration, or subscriptions.</li>
        <li><strong>High Quality:</strong> Professional results with zero latency.</li>
    </ul>

    <div class="cta-box" style="background: rgba(99,102,241,0.06); padding: 2.5rem; border-radius: 1.25rem; text-align: center; margin: 2.5rem 0; border: 1px solid rgba(99,102,241,0.2);">
        <h3 style="margin-bottom: 1rem; color: var(--text-primary);">Ready to get started?</h3>
        <a href="/{tool_id}/" class="btn primary" style="text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem; font-size: 1.2rem; font-weight: 700; padding: 0.8rem 1.8rem; background: var(--brand-primary); color: #fff; border-radius: 8px; transition: opacity 0.2s;">🚀 Open {title} Tool</a>
    </div>

    <h2 id="how">How to {keywords[0]}?</h2>
    <p>Using freeconvert.cloud is simple and takes just three steps:</p>
    <ol>
        <li>Click the button above to open the tool page.</li>
        <li>Follow the on-screen instructions (e.g. upload your file or enter text).</li>
        <li>Download or copy your results instantly.</li>
    </ol>
    
    <p>Thousands of users trust us for {keywords[1]} every day. Try it now!</p>
    """
    
    filename = slug + '.html'
    
    # Table of Contents
    toc_html = f"""
    <ul style="list-style-type: none; padding-left: 0; display: flex; flex-direction: column; gap: 0.5rem;">
        <li><a href="#why" style="color:var(--brand-primary); text-decoration:none; font-weight: 600;">⚡ Why use our {title} tool?</a></li>
        <li><a href="#how" style="color:var(--brand-primary); text-decoration:none; font-weight: 600;">📋 How to {keywords[0]}?</a></li>
    </ul>"""

    # Related Articles
    related_articles = BLOG_ARTICLES[:4]
    related_blogs_html = ""
    for rel in related_articles:
        related_blogs_html += f'<a href="/blog/{rel["slug"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">📝 {rel["title"]}</a>'

    # Schema markup
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"https://freeconvert.cloud/blog/hub-pages/{slug}.html",
                "url": f"https://freeconvert.cloud/blog/hub-pages/{slug}.html",
                "name": f"{title} Guide - freeconvert.cloud",
                "description": desc,
                "breadcrumb": {
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
                            "item": f"https://freeconvert.cloud/blog/hub-pages/{slug}.html"
                        }
                    ]
                }
            }
        ]
    }
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema_data)}</script>'

    # Replacements
    html = template
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{DESCRIPTION}}', desc)
    html = html.replace('https://freeconvert.cloud/blog/{{SLUG}}/', f'https://freeconvert.cloud/blog/hub-pages/{slug}.html')
    html = html.replace('{{SLUG}}', f'hub-pages/{slug}.html')
    html = html.replace('{{TOC}}', toc_html)
    html = html.replace('{{CONTENT}}', content)
    html = html.replace('{{SCHEMA}}', schema_tag)
    html = html.replace('{{RELATED_BLOGS}}', related_blogs_html)
    html = html.replace('{{DATE}}', "Updated Today")
    
    output_path = os.path.join(BLOG_DIR, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated Hub Page: {output_path}")

def update_sitemap(topics):
    sitemap_path = 'sitemap.xml'
    if not os.path.exists(sitemap_path):
        print("Sitemap not found, skipping update.")
        return

    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove closing tag to append
    content = content.replace('</urlset>', '')
    
    new_urls = ""
    for topic in topics:
        slug = topic['title'].lower().replace(' ', '-').replace('?', '')
        url = f"https://freeconvert.cloud/blog/hub-pages/{slug}.html"
        if url not in content:
            new_urls += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
            
    content += new_urls + '</urlset>'
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Added {len(topics)} hub pages to sitemap.xml")

def main():
    if not os.path.exists(TOPICS_FILE):
        print(f"No topics found at {TOPICS_FILE}")
        return
        
    with open(TOPICS_FILE, 'r', encoding='utf-8') as f:
        topics = json.load(f)
    
    for topic in topics:
        generate_hub_page(topic)
    
    update_sitemap(topics)

if __name__ == "__main__":
    main()
