# Andrey Bychkov Memorial Site

Hugo-based static site migrating from GetSimple CMS. Memorial for Russian alpinist Andrey Bychkov (1977-2006). Russian language only. Deployed to GitHub Pages.

## Quick Reference

**Dev**: `hugo server -D` → http://localhost:1313/andrey-bychkov/
**Build**: `hugo --minify` → outputs to `docs/`
**Deploy**: GitHub Pages serves from `/docs` on master branch

## Architecture

### Layouts
- No Hugo themes - custom layouts only
- `layouts/_default/baseof.html` - base template with background image
- `layouts/partials/` - head, header, footer
- `layouts/index.html` - homepage
- `layouts/biography/single.html` - biography page
- `layouts/photos/single.html` - photo galleries index

### Styling
- **Tailwind CSS** via Hugo Pipes (`css.PostCSS`)
- Colors: menu-active `#5091B1`, menu-inactive `#A1BBD1`
- Font: PT Sans (Google Fonts, Cyrillic subset)
- Mobile-first, max-width `max-w-4xl` (896px)
- Background: `static/images/bg.jpg`

### Content Structure
**NO HTML tags in .md files** - pure Markdown only. Hugo templates render HTML.

**Menu pages** (single .md files, NOT directories):
- ✅ `content/biography.md` → `/biography/`
- ✅ `content/photos.md` → `/photos/`
- ❌ `content/photos/_index.md` (wrong)

**Front matter structure**:
```yaml
---
title: "Page Title"
sections:
  - heading: "Section Title"
    paragraphs:
      - "Paragraph text with [links](url)"
      - "Another paragraph"
---
```

## Migration Pipeline

### Source Data
```
getsimple-html/
├── data/pages/*.xml        # ~95 XML pages
└── data/uploads/           # Images, galleries
```

### Migration Steps
1. **Extract XML content**: `getsimple-html/data/pages/<page>.xml`
2. **Decode HTML entities**: `&lt;` → `<`, `&quot;` → `"`, etc.
3. **Convert to structured YAML**:
   - Parse XML `<content>` to sections/paragraphs
   - Extract links, preserve markdown format
   - NO HTML tags in output
4. **Create content file**: `content/<page>.md`
5. **Create layout if needed**: `layouts/<page>/single.html`
6. **Copy images**: `getsimple-html/data/uploads/*` → `static/images/*`

### XML Structure
```xml
<item>
  <title><![CDATA[Title]]></title>
  <url><![CDATA[slug]]></url>
  <content><![CDATA[HTML content with &entities;]]></content>
</item>
```

### Completed Pages
- ✅ Homepage (`content/_index.md`, `layouts/index.html`)
- ✅ Biography (`content/biography.md`, `layouts/biography/single.html`)
- ✅ Photos index (`content/photos.md`, `layouts/photos/single.html`)

### Remaining Work
- Videos page (`/videos`)
- Texts page (`/texts`)
- ~90 child pages (articles, routes, stories)
- Gallery pages (individual albums under `/photos/*`)

## Configuration

**hugo.toml**:
- `baseURL = 'https://odemakov.github.io/andrey-bychkov/'`
- `publishDir = 'docs'`
- `markup.goldmark.renderer.unsafe = true` (allows HTML in markdown if needed)

**PostCSS**: Hugo v0.128+ uses `css.PostCSS` not deprecated `resources.PostCSS`

## Common Issues

- **Page Not Found**: Missing layout template (create `layouts/<page>/single.html`)
- **Images missing**: Copy from `getsimple-html/data/uploads/` to `static/images/`
- **Tailwind not applying**: Check `tailwind.config.js` content paths
- **Taxonomy warnings**: Ignore unless using tags/categories
