#!/usr/bin/env python3
import re

# Read the large file
with open('content/texts/andy_on_mountainru/2002_2.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into front matter and posts
parts = content.split('---\n', 2)
front_matter_start = parts[0]
front_matter_title = parts[1]
posts_content = parts[2]

# Split posts by separator
posts = posts_content.split('\n---\n')

# Split into two halves
mid_point = len(posts) // 2
posts_part1 = posts[:mid_point]
posts_part2 = posts[mid_point:]

# Create first half
part1 = f"---\n{front_matter_title}---\n" + '\n---\n'.join(posts_part1)
with open('content/texts/andy_on_mountainru/2002_2a.md', 'w', encoding='utf-8') as f:
    f.write(part1)

# Create second half with modified title
front_matter_mod = front_matter_title.replace('2002 (2е полугодие)', '2002 (2е полугодие) - часть 2')
part2 = f"---\n{front_matter_mod}---\n" + '\n---\n'.join(posts_part2)
with open('content/texts/andy_on_mountainru/2002_2b.md', 'w', encoding='utf-8') as f:
    f.write(part2)

print(f"Split into {len(posts_part1)} + {len(posts_part2)} posts")
