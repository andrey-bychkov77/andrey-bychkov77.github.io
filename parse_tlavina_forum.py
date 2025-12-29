#!/usr/bin/env python3
"""Convert tlavina XML to forum-style markdown."""

import xml.etree.ElementTree as ET
import html
import re


def parse_xml(xml_path):
    """Parse GetSimple XML and extract content."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    title = root.find('.//title').text
    content = root.find('.//content').text

    # Decode HTML entities
    content = html.unescape(content)
    content = html.unescape(content)  # Second pass

    # Replace common entities
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&quot;', '"')

    # Replace <br /> with line breaks
    content = content.replace('<br />', '\n')
    content = content.replace('<br/>', '\n')
    content = content.replace('<br>', '\n')

    # Replace paragraph tags
    content = re.sub(r'<p>\s*', '\n\n', content)
    content = re.sub(r'</p>\s*', '\n\n', content)

    # Replace bold/strong
    content = re.sub(r'<b>', '**', content)
    content = re.sub(r'</b>', '**', content)
    content = re.sub(r'<strong>', '**', content)
    content = re.sub(r'</strong>', '**', content)

    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Clean up whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()

    return title, content


def format_as_forum_posts(content):
    """Format content as forum posts with separators."""
    lines = content.split('\n')
    result = []
    current_post = []

    intro_section = True

    for line in lines:
        line = line.strip()

        # Check if this is a forum post header (username (гость) - date or From: pattern)
        is_post_header = (
            re.match(r'^[А-Яа-яA-Za-z0-9_\s]+\s*\(гость\)\s*-\s*\d{2}\.\d{2}\.\d{2}', line) or
            re.match(r'^From:\s+\w+', line) or
            re.match(r'^Date:\s+\d', line)
        )

        # End intro section when we hit forum posts
        if is_post_header and intro_section:
            intro_section = False
            if current_post:
                result.extend(current_post)
                result.append('')
                current_post = []

        # If we hit a post header after intro, save previous post
        if is_post_header and not intro_section and current_post:
            result.extend(current_post)
            result.append('')
            result.append('---')
            result.append('')
            current_post = []

        if line:
            # Make post headers bold
            if is_post_header:
                line = f'**{line}**'
            current_post.append(line)
        elif current_post:  # Empty line, keep it if we're in a post
            current_post.append('')

    # Add last post
    if current_post:
        result.extend(current_post)

    return '\n'.join(result)


def create_markdown(title, content):
    """Generate Hugo markdown file."""
    formatted_content = format_as_forum_posts(content)

    # Clean title from HTML entities
    title = title.replace('&quot;', '"')
    title = title.replace('&amp;', '&')

    md = f"""---
title: '{title}'
type: "forum"
---

{formatted_content}
"""
    return md


# Process the file
xml_path = 'getsimple-html/data/pages/tlavina.xml'
md_path = 'content/texts/tlavina.md'

print("Processing tlavina...")
title, content = parse_xml(xml_path)
md = create_markdown(title, content)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"  Created {md_path}")
print("Done!")
