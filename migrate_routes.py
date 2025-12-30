#!/usr/bin/env python3
"""Migrate climbing route pages from GetSimple XML to Hugo markdown."""

import xml.etree.ElementTree as ET
import html
import os
import re
from pathlib import Path
from html.parser import HTMLParser

class RouteHTMLToMarkdown(HTMLParser):
    """Convert route HTML to markdown with proper structure."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_paragraph = False
        self.in_bold_p = False
        self.in_list = False
        self.in_list_item = False
        self.list_item_count = 0
        self.list_item_has_content = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'p':
            # Check if it's a bold paragraph (heading)
            if attrs_dict.get('class') == 'b':
                # Add spacing before heading if there's previous content
                if self.text and not self.text[-1].endswith('\n\n'):
                    self.text.append('\n\n')
                self.in_bold_p = True
            else:
                self.in_paragraph = True
        elif tag == 'br':
            self.text.append('  \n')
        elif tag == 'ol':
            self.in_list = True
            self.list_item_count = 0
        elif tag == 'li':
            # Close previous list item if it wasn't explicitly closed
            if self.in_list_item:
                self.text.append('\n')
            self.in_list_item = True
            self.list_item_count += 1
            self.list_item_has_content = False
        elif tag == 'h2':
            self.text.append('\n## ')

    def handle_endtag(self, tag):
        if tag == 'p':
            if self.in_bold_p:
                self.text.append('\n\n')
                self.in_bold_p = False
            elif self.in_paragraph:
                self.text.append('\n\n')
                self.in_paragraph = False
        elif tag == 'ol':
            # Make sure we're not treating subsequent content as list items
            if self.in_list_item:
                self.text.append('\n')
            self.in_list = False
            self.in_list_item = False
            self.text.append('\n')
        elif tag == 'li':
            self.text.append('\n')
            self.in_list_item = False
        elif tag == 'h2':
            self.text.append('\n\n')

    def handle_data(self, data):
        decoded = html.unescape(data).strip()
        if not decoded:
            return

        # If it's a bold paragraph (heading), make it a heading
        if self.in_bold_p:
            self.text.append(f'### {decoded}')
        # If it's a list item, add numbered markdown list syntax only once
        elif self.in_list_item:
            if not self.list_item_has_content:
                self.text.append(f'{self.list_item_count}. {decoded}')
                self.list_item_has_content = True
            else:
                # Subsequent content within same list item (after <br>)
                self.text.append(decoded)
        else:
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
    date = "2011-07-06"  # default for routes
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
    parser = RouteHTMLToMarkdown()
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

    # Migrate arkhiz_routes index page
    routes_xml = source_dir / "arkhiz_routes.xml"
    if routes_xml.exists():
        md_content, url, parent = xml_to_markdown(routes_xml)
        target_path = Path("content/texts/arkhiz_routes.md")
        target_path.write_text(md_content, encoding='utf-8')
        print(f"Created {target_path}")

    # Migrate individual route pages
    route_slugs = ['tokmak', 'chuchhur', 'magana', 'pshish', 'psish_vost']
    route_dir = Path("content/texts/arkhiz_routes")
    route_dir.mkdir(parents=True, exist_ok=True)

    migrated = 0
    for slug in route_slugs:
        xml_path = source_dir / f"{slug}.xml"
        if not xml_path.exists():
            print(f"Skipping {slug} - XML not found")
            continue

        md_content, url, parent = xml_to_markdown(xml_path)
        md_path = route_dir / f"{slug}.md"

        if md_path.exists():
            print(f"Skipping {slug}.md - already exists")
            continue

        md_path.write_text(md_content, encoding='utf-8')
        print(f"Created {slug}.md")
        migrated += 1

    print(f"\nMigration complete: {migrated + 1} pages")

if __name__ == "__main__":
    main()
