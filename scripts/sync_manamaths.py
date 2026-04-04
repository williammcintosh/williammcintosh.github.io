#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SITE_ROOT.parent
SOURCE_ROOT = WORKSPACE_ROOT / 'manamaths'
TARGET_ROOT = SITE_ROOT / 'manamaths'
TARGET_PDFS_ROOT = TARGET_ROOT / 'pdfs'

LEVEL_ORDER = ['foundation', 'proficient', 'excellence']
LEVEL_LABELS = {
    'foundation': 'Foundation',
    'proficient': 'Proficient',
    'excellence': 'Excellence',
}
LEVEL_DESCRIPTIONS = {
    'foundation': 'Direct practice and accessible first-step questions.',
    'proficient': 'More variety and more independent recognition work.',
    'excellence': 'Richer reasoning, comparison, and multi-step thinking.',
}


def title_from_slug(slug: str) -> str:
    title = slug.removeprefix('lo-yr9-')
    return title.replace('-', ' ').title()


def collect_objectives() -> list[dict]:
    objectives = []
    for folder in sorted(SOURCE_ROOT.glob('lo-yr9-*')):
        if not folder.is_dir():
            continue
        pdfs = []
        for level in LEVEL_ORDER:
            source_pdf = folder / f'{level}-questions.pdf'
            if source_pdf.exists():
                pdfs.append(
                    {
                        'level': level,
                        'label': LEVEL_LABELS[level],
                        'description': LEVEL_DESCRIPTIONS[level],
                        'source_path': source_pdf,
                        'file_name': source_pdf.name,
                    }
                )
        if pdfs:
            objectives.append({'slug': folder.name, 'title': title_from_slug(folder.name), 'pdfs': pdfs})
    return objectives


def copy_pdfs(objectives: list[dict]) -> None:
    TARGET_PDFS_ROOT.mkdir(parents=True, exist_ok=True)
    live_slugs = {objective['slug'] for objective in objectives}
    for existing in TARGET_PDFS_ROOT.iterdir():
        if existing.is_dir() and existing.name not in live_slugs:
            shutil.rmtree(existing)
    for objective in objectives:
        destination = TARGET_PDFS_ROOT / objective['slug']
        destination.mkdir(parents=True, exist_ok=True)
        for pdf in objective['pdfs']:
            shutil.copy2(pdf['source_path'], destination / pdf['file_name'])


def render_page(objectives: list[dict]) -> str:
    sections = []
    jump_links = []
    total_pdfs = sum(len(objective['pdfs']) for objective in objectives)

    for objective in objectives:
        jump_links.append(
            f'<a href="#{html.escape(objective["slug"])}">{html.escape(objective["title"])}</a>'
        )
        cards = []
        for pdf in objective['pdfs']:
            href = f"/manamaths/pdfs/{objective['slug']}/{pdf['file_name']}"
            cards.append(
                f'''<article class="mm-card mm-worksheet-card">
  <p class="mm-level">{html.escape(pdf['label'])}</p>
  <p>{html.escape(pdf['description'])}</p>
  <p><a class="mm-button mm-button-secondary" href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">Open PDF</a></p>
  <p class="mm-filename"><a href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">{html.escape(pdf['file_name'])}</a></p>
</article>'''
            )
        sections.append(
            f'''<section id="{html.escape(objective['slug'])}" class="mm-objective-section">
  <div class="mm-section-heading">
    <p class="mm-kicker">Learning objective</p>
    <h2>{html.escape(objective['title'])}</h2>
    <p>Foundation, Proficient, and Excellence worksheets for this objective.</p>
  </div>
  <div class="mm-card-grid">
    {''.join(cards)}
  </div>
</section>'''
        )

    return f'''<!DOCTYPE html>
<html>
  <head>
    <title>Mana Maths | wmm.co.nz</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <meta name="description" content="Mana Maths worksheet PDFs organised by learning objective." />
    <link rel="stylesheet" href="/assets/css/main.css" />
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
  </head>
  <body class="is-preload">
    <script src="/assets/js/navbar.js" defer></script>
    <div id="navbar"></div>
    <script>
      fetch('/navbar.html')
        .then((response) => response.text())
        .then((data) => {{
          document.getElementById('navbar').innerHTML = data;
        }})
        .catch((error) => console.error('Error loading navbar:', error));
    </script>

    <article class="wrapper style5 mm-page-wrapper">
      <div class="container mm-page">
        <header class="mm-hero">
          <p class="mm-kicker">Mana Maths</p>
          <h1>Worksheet PDFs by learning objective</h1>
          <p class="mm-lead">Open the latest public worksheets directly as PDFs. Each learning objective groups its Foundation, Proficient, and Excellence files together.</p>
          <div class="mm-actions">
            <a class="mm-button" href="#mm-library">Browse worksheets</a>
            <a class="mm-button mm-button-secondary" href="https://github.com/williammcintosh/manamaths" target="_blank" rel="noopener noreferrer">View repo</a>
          </div>
        </header>

        <section class="mm-summary-row">
          <article class="mm-card mm-stat-card">
            <p class="mm-stat-number">{len(objectives)}</p>
            <p class="mm-stat-label">Learning objectives</p>
          </article>
          <article class="mm-card mm-stat-card">
            <p class="mm-stat-number">{total_pdfs}</p>
            <p class="mm-stat-label">Worksheet PDFs</p>
          </article>
        </section>

        <section id="mm-library" class="mm-library-intro">
          <p class="mm-kicker">Quick links</p>
          <div class="mm-jump-links">{' '.join(jump_links)}</div>
        </section>

        {''.join(sections)}
      </div>
    </article>

    <div id="contactbar"></div>
    <script>
      fetch('/contactbar.html')
        .then((response) => response.text())
        .then((data) => {{
          document.getElementById('contactbar').innerHTML = data;
          document.querySelector('.full-contact').style.display = 'none';
          document.querySelector('.default-contact').style.display = 'flex';
        }})
        .catch((error) => console.error('Error loading contact bar:', error));
    </script>

    <script src="/assets/js/jquery.min.js"></script>
    <script src="/assets/js/jquery.scrolly.min.js"></script>
    <script src="/assets/js/browser.min.js"></script>
    <script src="/assets/js/breakpoints.min.js"></script>
    <script src="/assets/js/util.js"></script>
    <script src="/assets/js/main.js"></script>
  </body>
</html>
'''


def main() -> int:
    objectives = collect_objectives()
    if not objectives:
        raise SystemExit('No worksheet PDFs found in manamaths repo.')
    copy_pdfs(objectives)
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    (TARGET_ROOT / 'index.html').write_text(render_page(objectives), encoding='utf-8')
    print(f'Synced {sum(len(o["pdfs"]) for o in objectives)} PDFs across {len(objectives)} learning objectives.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
