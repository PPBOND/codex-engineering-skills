"""Embed a diagram config in a standalone HTML and copy its browser checker."""
import argparse
import html
import json
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def build(config_path, output):
    """Read authored JSON and create a local page; no browser or network I/O."""
    config_path, output = Path(config_path), Path(output)
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if not config.get('pages') or not config['pages'][0].get('overview'):
        raise ValueError('pages must start with an overview')
    for key in ('title', 'subtitle', 'sourceNote'):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f'{key} must be nonempty text')
    title = config['title']
    template = (SKILL / 'assets/panel-template.html').read_text(encoding='utf-8')
    assert template.count('<!--LIVE_CONFIG-->') == 1
    blob = json.dumps(config, ensure_ascii=False).replace('</', '<\\/')
    page = template.replace('<!--PANEL_TITLE-->', html.escape(title))
    page = page.replace('<!--LIVE_CONFIG-->',
                        '<script id="live-config" type="application/json">' +
                        blob + '</script>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8', newline='\n')
    shutil.copyfile(SKILL / 'scripts/check_panel.js', output.parent / 'check-panel.js')
    return len(config['pages'])


def main():
    """Build the explicitly named local output from the provided config."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    count = build(args.config, args.out)
    print(f'Built {count} pages: {args.out.resolve()}')


if __name__ == '__main__':
    main()
