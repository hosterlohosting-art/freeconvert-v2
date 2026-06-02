import os
import json
from datetime import datetime
from blog_data import BLOG_ARTICLES

TEMPLATE_PATH = 'blog/blog-template.html'
BLOG_DIR = 'blog'
TOPICS_FILE = 'blog/topics.json'

def generate_blog_post(title, content, date=None):
    if not date:
        date = datetime.now().strftime("%B %d, %Y")
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    slug = title.lower().replace(' ', '-').replace('?', '')
    
    # Generate description from content or title
    desc = f"Read our expert guide: {title}. Understand optimization, conversion steps, and best practices."
    
    # TOC
    toc_html = f"""
    <ul style="list-style-type: none; padding-left: 0; display: flex; flex-direction: column; gap: 0.5rem;">
        <li><a href="#guide" style="color:var(--brand-primary); text-decoration:none; font-weight: 600;">⚡ {title}</a></li>
    </ul>"""
    
    # Wrap content with section id
    wrapped_content = f'<div id="guide">{content}</div>'

    # EEAT Author/Reviewer box
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
    full_content = author_box_html + wrapped_content

    # Related blogs
    related_articles = BLOG_ARTICLES[:4]
    related_blogs_html = ""
    for rel in related_articles:
        related_blogs_html += f'<a href="/blog/{rel["slug"]}/" class="category-tab" style="box-shadow:none; text-decoration:none;">📝 {rel["title"]}</a>'

    # Schema
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": title,
                "description": desc,
                "datePublished": "2026-06-01",
                "dateModified": datetime.now().strftime("%Y-%m-%d"),
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
            }
        ]
    }
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema_data)}</script>'

    html = template
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{DESCRIPTION}}', desc)
    html = html.replace('https://freeconvert.cloud/blog/{{SLUG}}/', f'https://freeconvert.cloud/blog/{slug}/')
    html = html.replace('{{SLUG}}', slug)
    html = html.replace('{{TOC}}', toc_html)
    html = html.replace('{{CONTENT}}', full_content)
    html = html.replace('{{SCHEMA}}', schema_tag)
    html = html.replace('{{RELATED_BLOGS}}', related_blogs_html)
    html = html.replace('{{DATE}}', date)
    
    output_dir = os.path.join(BLOG_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated clean URL Blog: {output_path}")

def main():
    if not os.path.exists(TOPICS_FILE):
        print(f"No topics found at {TOPICS_FILE}")
        return
        
    with open(TOPICS_FILE, 'r', encoding='utf-8') as f:
        topics = json.load(f)
    
    for topic in topics:
        generate_blog_post(topic['title'], topic['content'])

if __name__ == "__main__":
    main()
