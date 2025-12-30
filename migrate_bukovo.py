#!/usr/bin/env python3
"""Migrate bukovo_net forum pages from GetSimple XML to Hugo markdown."""

import xml.etree.ElementTree as ET
import html
import os
import re
from pathlib import Path
from html.parser import HTMLParser

class HTMLToMarkdown(HTMLParser):
    """Convert HTML to clean markdown text."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_paragraph = False

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.in_paragraph = True
        elif tag == 'br':
            # Use actual line break to preserve formatting (poetry, lists, etc.)
            self.text.append('  \n')  # Two spaces + newline = markdown line break

    def handle_endtag(self, tag):
        if tag == 'p':
            if self.in_paragraph:
                self.text.append('\n\n')
            self.in_paragraph = False

    def handle_data(self, data):
        # Decode HTML entities and strip leading/trailing whitespace from each chunk
        decoded = html.unescape(data).strip()
        if decoded:  # Only add non-empty text
            self.text.append(decoded)

    def get_text(self):
        result = ''.join(self.text)
        # Clean up multiple spaces
        result = re.sub(r' {2,}', ' ', result)
        # Clean up excessive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()

def xml_to_markdown(xml_path):
    """Convert GetSimple XML to Hugo markdown."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract metadata
    title_elem = root.find('.//title')
    title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"

    url_elem = root.find('.//url')
    url = url_elem.text if url_elem is not None and url_elem.text else ""

    parent_elem = root.find('.//parent')
    parent = parent_elem.text if parent_elem is not None and parent_elem.text else ""

    pubdate_elem = root.find('.//pubDate')
    # Extract date from pubDate (format: "Tue, 22 Jul 2014 15:49:08 -0400")
    date = "2005-01-01"  # default
    if pubdate_elem is not None and pubdate_elem.text:
        try:
            from datetime import datetime
            dt = datetime.strptime(pubdate_elem.text, "%a, %d %b %Y %H:%M:%S %z")
            date = dt.strftime("%Y-%m-%d")
        except:
            pass

    content_elem = root.find('.//content')
    raw_content = content_elem.text if content_elem is not None and content_elem.text else ""

    # First, unescape XML entities to get actual HTML
    html_content = html.unescape(raw_content)

    # Then parse HTML to markdown
    parser = HTMLToMarkdown()
    parser.feed(html_content)
    content = parser.get_text()

    # Build markdown
    md = f"""---
title: "{title}"
date: {date}
type: "text"
---

{content}
"""

    return md, url, parent

def main():
    source_dir = Path("getsimple-html/data/pages")
    target_base = Path("content/texts/bukovo-net")
    target_base.mkdir(parents=True, exist_ok=True)

    # Find all bukovo_net pages
    bukovo_pages = []
    for xml_file in source_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            parent_elem = root.find('.//parent')
            if parent_elem is not None and parent_elem.text == "bukovo_net":
                bukovo_pages.append(xml_file)
        except:
            continue

    print(f"Found {len(bukovo_pages)} bukovo_net pages to migrate")

    migrated = 0
    skipped = 0

    for xml_path in sorted(bukovo_pages):
        try:
            md_content, url, parent = xml_to_markdown(xml_path)

            if not url:
                print(f"Skipping {xml_path.name} - no URL")
                skipped += 1
                continue

            # Target markdown file
            md_path = target_base / f"{url}.md"

            # Check if already exists
            if md_path.exists():
                print(f"Skipping {url}.md - already exists")
                skipped += 1
                continue

            # Write markdown
            md_path.write_text(md_content, encoding='utf-8')
            print(f"Created {url}.md")
            migrated += 1

        except Exception as e:
            print(f"Error processing {xml_path.name}: {e}")
            skipped += 1

    print(f"\nMigration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped: {skipped}")

if __name__ == "__main__":
    main()
