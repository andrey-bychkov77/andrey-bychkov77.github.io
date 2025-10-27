# Andrey Bychkov Memorial Site - Development Guide

## Project Overview
Hugo-based static site migrating from GetSimple CMS. Memorial site for Russian alpinist Andrey Bychkov (1977-2006). Russian language only. Deployed to GitHub Pages.

## Architecture

### Layout Structure
- **No Hugo themes** - custom layouts only
- `layouts/_default/baseof.html` - base template with background image
- `layouts/partials/` - reusable components (head, header, footer)
- `layouts/index.html` - homepage layout
- Future: section-specific layouts in `layouts/biography/`, `layouts/photos/`, etc.

### Styling
- **Tailwind CSS** via Hugo Pipes
- Custom colors: `menu-active: #5091B1`, `menu-inactive: #A1BBD1`
- Font: PT Sans (Google Fonts with Cyrillic subset)
- Mobile-first responsive design
- Background image: `static/images/bg.jpg` (covers entire viewport)

### Content Source
- Original site: `getsimple-html/` directory
- Content stored in XML files: `getsimple-html/data/pages/*.xml`
- ~95 pages to migrate
- Images/galleries: `getsimple-html/data/uploads/`
- Theme assets: `getsimple-html/theme/Andy/`

## Site Structure

### Menu Items (defined in layouts/partials/header.html:3-7)
1. Главная (/)
2. Биография (/biography)
3. Фотоальбомы (/photos)
4. Видео (/videos)
5. Тексты (/texts)

### Sections to Create
- **biography** - biographical content (XML: biography.xml)
- **photos** - photo galleries (need gallery shortcode/plugin)
- **videos** - video content
- **texts** - written works, articles, poetry

## Migration Process

### XML to Markdown Conversion
Original XML structure:
```xml
<item>
  <title><![CDATA[Title]]></title>
  <url><![CDATA[slug]]></url>
  <menu><![CDATA[Menu Name]]></menu>
  <content><![CDATA[HTML content with entities]]></content>
  <template><![CDATA[template.php]]></template>
</item>
```

Convert to Hugo front matter:
```yaml
---
title: "Title"
slug: "slug"
menu: "Menu Name"
---
Content (decode HTML entities, preserve HTML if needed)
```

### Content Migration Strategy
1. Start with key pages: index (done), biography, main photo albums
2. Create Python/Go script to batch convert XML → Markdown
3. Handle HTML entities properly (&lt;, &gt;, &amp;, etc.)
4. Preserve embedded HTML (markup.goldmark.renderer.unsafe = true)
5. Move images from `getsimple-html/data/uploads/` to `static/uploads/`

## GitHub Pages Deployment

### Configuration (hugo.toml:1-5)
- `baseURL = 'https://odemakov.github.io/andrey-bychkov/'`
- `publishDir = 'docs'` - GitHub Pages serves from /docs
- Build command: `hugo --minify`

### GitHub Actions Workflow
- File: `.github/workflows/hugo.yml` (not created yet)
- Trigger: push to master branch
- Steps: Install Hugo Extended, npm install, hugo build, deploy to gh-pages

### Manual Deployment
```bash
hugo --minify
git add docs/
git commit -m "Update site"
git push origin master
```

## Development Workflow

### Local Development
```bash
npm install          # First time only
hugo server -D       # Start dev server at http://localhost:1313/andrey-bychkov/
```

### File Watching
Hugo watches: content/, layouts/, static/, assets/, hugo.toml
Tailwind rebuilds automatically via Hugo Pipes

### Build for Production
```bash
hugo --minify        # Outputs to docs/ directory
```

## Technical Details

### Hugo Pipes CSS Processing (layouts/partials/head.html:7)
```
{{ $css := resources.Get "css/main.css" | css.PostCSS }}
```
- Hugo v0.128+ uses `css.PostCSS` (not deprecated `resources.PostCSS`)
- Processes Tailwind directives
- Minified and fingerprinted in production

### Responsive Breakpoints
- Mobile: default styles
- Tablet: `md:` prefix (768px+)
- Desktop: `lg:` prefix (1024px+) if needed
- Max content width: `max-w-4xl` (896px)

### Image Handling
- Background: inline style in baseof.html (required for dynamic path)
- Content images: `{{ "images/file.jpg" | relURL }}`
- Preserves aspect ratios, mobile-friendly scaling

## Next Steps Priority

1. **Biography page** - Most important content after homepage
   - Create `content/biography.md`
   - Extract content from `getsimple-html/data/pages/biography.xml`
   - May need custom layout for long-form content

2. **Photo galleries** - Core feature
   - Research Hugo gallery options (shortcodes, Hugo modules, or custom)
   - Migrate gallery structure from `getsimple-html/data/uploads/gallery/`
   - Lightbox functionality needed

3. **Batch migration script** - Convert remaining ~90 pages
   - Python script recommended (BeautifulSoup for XML parsing)
   - Handle HTML entity decoding
   - Organize by sections

4. **GitHub Actions** - Automated deployment
   - Create `.github/workflows/hugo.yml`
   - Test deployment pipeline

## Important Notes

- **Copyright year**: Footer uses `{{ now.Year }}` for dynamic year (layouts/partials/footer.html:2)
- **HTML in Markdown**: Enabled via `markup.goldmark.renderer.unsafe = true`
- **Russian language**: All content in Russian, no i18n needed
- **Original URLs**: Try to preserve URL structure from GetSimple for SEO
- **No analytics yet**: Original had Yandex.Metrika (commented out for now)

## Common Issues

- **PostCSS error**: Ensure using `css.PostCSS` not `resources.PostCSS` (Hugo v0.128+)
- **Taxonomy warning**: Ignore unless creating tags/categories
- **Background image not showing**: Check path in baseof.html, verify file in static/images/
- **Tailwind not applying**: Verify PostCSS config, check content paths in tailwind.config.js

## Files Reference

### Configuration
- `hugo.toml` - Hugo configuration
- `package.json` - npm dependencies (Tailwind)
- `tailwind.config.js` - Tailwind configuration
- `postcss.config.js` - PostCSS processing

### Key Layouts
- `layouts/_default/baseof.html` - Base template
- `layouts/index.html` - Homepage
- `layouts/partials/head.html` - HTML head
- `layouts/partials/header.html` - Navigation menu
- `layouts/partials/footer.html` - Footer with copyright

### Content
- `content/_index.md` - Homepage content
- `static/images/` - Static assets (bg.jpg, index_photo.png)

### Source Data
- `getsimple-html/data/pages/` - Original XML pages (~95 files)
- `getsimple-html/data/uploads/` - Original uploaded files/images
- `getsimple-html/theme/Andy/` - Original theme (reference for styling)
