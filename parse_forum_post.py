#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import html
import sys
import re

def parse_forum_post(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    title = root.find('title').text
    content = root.find('content').text

    # Decode HTML entities
    content = html.unescape(content)

    # Parse paragraphs
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)

    posts = []
    for p in paragraphs:
        # Clean HTML tags but preserve line breaks
        p = re.sub(r'<br\s*/?\s*>', '\n', p)
        p = re.sub(r'<[^>]+>', '', p)
        p = re.sub(r'&nbsp;', ' ', p)
        p = p.strip()

        if p:
            posts.append(p)

    # Output markdown
    print(f"---")
    print(f"title: \"{title}\"")
    print(f"---")
    print()

    for post in posts:
        lines = post.split('\n')
        # Check if first line looks like a post header (username + date)
        if lines and ('bicheps' in lines[0].lower() or any(month in lines[0] for month in ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'])):
            print(f"**{lines[0].strip()}**")
            print()
            for line in lines[1:]:
                line = line.strip()
                if line:
                    print(line + "  ")
            print()
        else:
            for line in lines:
                line = line.strip()
                if line:
                    print(line + "  ")
            print()

if __name__ == '__main__':
    parse_forum_post(sys.argv[1])
