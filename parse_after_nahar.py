#!/usr/bin/env python3
"""Convert After Nahar section XML files to Hugo markdown."""

import xml.etree.ElementTree as ET
import html
import re


def clean_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""

    # Decode HTML entities (multiple passes to catch nested entities)
    text = html.unescape(text)
    text = html.unescape(text)  # Second pass for double-encoded entities

    # Replace common entities that might remain
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')

    # Replace <br /> with line breaks
    text = text.replace('<br />', '\n')
    text = text.replace('<br/>', '\n')
    text = text.replace('<br>', '\n')

    # Replace paragraph tags
    text = re.sub(r'<p>\s*', '\n\n', text)
    text = re.sub(r'</p>\s*', '\n\n', text)

    # Replace headers
    text = re.sub(r'<h3[^>]*>', '\n\n### ', text)
    text = re.sub(r'</h3>', '\n\n', text)
    text = re.sub(r'<h4[^>]*>', '\n\n#### ', text)
    text = re.sub(r'</h4>', '\n\n', text)

    # Replace bold
    text = re.sub(r'<b>', '**', text)
    text = re.sub(r'</b>', '**', text)
    text = re.sub(r'<strong>', '**', text)
    text = re.sub(r'</strong>', '**', text)

    # Replace italic
    text = re.sub(r'<i>', '*', text)
    text = re.sub(r'</i>', '*', text)

    # Handle links
    text = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', text)

    # Handle delimiters first (before quotes)
    text = re.sub(r'<div class="delimeter">.*?</div>', '\n\n---\n\n', text, flags=re.DOTALL)

    # Handle quotes/blockquotes - extract and format them before removing other HTML
    def format_quote_block(match):
        quote_content = match.group(1)
        # Remove HTML tags within the quote
        quote_content = re.sub(r'<br\s*/?>', '\n', quote_content)
        quote_content = re.sub(r'<p>', '\n\n', quote_content)
        quote_content = re.sub(r'</p>', '', quote_content)
        quote_content = re.sub(r'<b>(.*?)</b>', r'**\1**', quote_content)
        quote_content = re.sub(r'<[^>]+>', '', quote_content)

        # Clean up and split into paragraphs
        quote_content = quote_content.strip()
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', quote_content) if p.strip()]

        # Add > to each paragraph
        formatted = '\n\n> '.join(paragraphs)
        return f'\n\n> {formatted}\n\n'

    text = re.sub(r'<div class="quote">(.*?)</div>', format_quote_block, text, flags=re.DOTALL)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def parse_xml(xml_path):
    """Parse GetSimple XML and extract content."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    title = root.find('.//title').text
    content = root.find('.//content').text

    # Clean content
    content = clean_html(content)

    return title, content


def create_markdown(title, content):
    """Generate Hugo markdown file."""
    md = f"""---
title: "{title}"
type: "texts"
---

{content}
"""
    return md


# Process all 7 files
files = [
    ('tluchshe_gor', 'getsimple-html/data/pages/tluchshe_gor.xml', 'content/texts/tluchshe_gor.md'),
    ('ice_heart', 'getsimple-html/data/pages/ice_heart.xml', 'content/texts/ice_heart.md'),
    ('tlavina', 'getsimple-html/data/pages/tlavina.xml', 'content/texts/tlavina.md'),
    ('tnahar_exp', 'getsimple-html/data/pages/tnahar_exp.xml', 'content/texts/tnahar_exp.md'),
    ('mountain_ru_2006', 'getsimple-html/data/pages/mountain_ru_2006.xml', 'content/texts/mountain_ru_2006.md'),
    ('remember', 'getsimple-html/data/pages/remember.xml', 'content/texts/remember.md'),
    ('mem_bukovonet', 'getsimple-html/data/pages/mem_bukovonet.xml', 'content/texts/mem_bukovonet.md'),
]

for name, xml_path, md_path in files:
    print(f"Processing {name}...")
    title, content = parse_xml(xml_path)
    md = create_markdown(title, content)

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"  Created {md_path}")

print("\nDone! Created 7 markdown files.")
