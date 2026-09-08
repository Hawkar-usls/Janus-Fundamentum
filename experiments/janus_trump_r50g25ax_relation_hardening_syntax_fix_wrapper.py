from __future__ import annotations

from pathlib import Path

SOURCE = Path(__file__).with_name('janus_trump_r50g25ax_relation_hardening.py')
text = SOURCE.read_text(encoding='utf-8')
old = 'total_parity_rows = sum(sum(1 for b in (0, 1) if mask & (1 << b)) for mask in f["table"].values()) for f in factors)'
new = 'total_parity_rows = sum(sum(1 for b in (0, 1) if mask & (1 << b)) for f in factors for mask in f["table"].values())'
count = text.count(old)
assert count == 1, ('EXPECTED_EXACTLY_ONE_SYNTAX_PATCH_SITE', count)
fixed = text.replace(old, new, 1)
assert fixed.count(new) == 1
code = compile(fixed, str(SOURCE) + '::SYNTAX_FIX_WRAPPER', 'exec')
g = {
    '__name__': '__main__',
    '__file__': str(SOURCE),
    '__package__': None,
}
exec(code, g, g)
