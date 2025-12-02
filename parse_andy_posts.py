#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import html
import re

def parse_forum_xml(xml_path):
    """Parse GetSimple XML and extract forum posts"""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    title = root.find('.//title').text
    content = root.find('.//content').text

    # Decode HTML entities
    content = html.unescape(content)

    # Split into posts - each post is in a <p> tag
    posts = []
    # Match <p>...</p> blocks
    for match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        post_html = match.group(1).strip()
        if post_html:
            # Clean up HTML tags but preserve structure
            post_text = post_html.replace('<br />', '\n')
            post_text = re.sub(r'<[^>]+>', '', post_text)
            # Clean up &nbsp; entities
            post_text = post_text.replace('&nbsp;', ' ')
            # Remove leading/trailing whitespace and dedent
            lines = [line.strip() for line in post_text.split('\n')]
            # Join with single line breaks (markdown needs 2 spaces at end for <br>)
            post_text = '  \n'.join(line for line in lines if line)
            if post_text:
                posts.append(post_text)

    return title, posts

def create_markdown(title, posts):
    """Generate Hugo markdown front matter + content"""
    md = f"""---
title: "{title}"
type: "forum"
---

"""
    # Author line patterns to detect and make bold
    # Use single-line mode to avoid blank line splits
    author_pattern = re.compile(r'(^|\n\n)(\s*Автор:\s*.+\d{4}\s+в\s+\d{2}:\d{2}:\d{2})(\n\n|$)')
    author_pattern2 = re.compile(r'(^|\n\n)(\(.+?\)\s+\d+\s+\w+\s+\d{4}\s+в\s+\d{2}:\d{2}:\d{2})(\n\n|$)')
    author_pattern3 = re.compile(r'(^|\n\n)(\w+\s+\d+\s+\w+\s+\d{4}\s+в\s+\d{2}:\d{2}:\d{2})(\n\n|$)')

    for post in posts:
        # Make author lines bold, preserving surrounding newlines
        post = author_pattern.sub(r'\1**\2**\3', post)
        post = author_pattern2.sub(r'\1**\2**\3', post)
        post = author_pattern3.sub(r'\1**\2**\3', post)

        # Add newlines before quote markers only if not already at line start
        post = re.sub(r'([^\n])\s+(>>(?=\s)|>(?=\s))', r'\1\n\n\2', post)

        md += f"{post}\n\n---\n\n"

    return md.rstrip() + "\n"

if __name__ == "__main__":
    import sys

    xml_file = sys.argv[1]
    output_file = sys.argv[2]

    title, posts = parse_forum_xml(xml_file)
    markdown = create_markdown(title, posts)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Converted {len(posts)} posts from {xml_file} to {output_file}")
