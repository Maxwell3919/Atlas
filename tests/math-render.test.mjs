import test from 'node:test';
import assert from 'node:assert/strict';
import { createSatteriMarkdownProcessor } from '@astrojs/markdown-satteri';
import { createMathPlugin, protectHtmlCode } from '../src/lib/math.js';

const processor = await createSatteriMarkdownProcessor({
  syntaxHighlight: false, smartypants: false,
  features: { math: true }, mdastPlugins: [createMathPlugin()],
});
const render = async (raw) => (await processor.render(protectHtmlCode(raw))).code;

test('separation-work display interrupts a paragraph and preserves TeX escapes', async () => {
  const tex = "W(d)=\\frac{E_{\\rm without\\ entropy}(d)-E_{\\rm without\\ entropy}(0)}{A},\\qquad\n1\\;\\mathrm{eV/\\mathring A^2}=16.02176634\\;\\mathrm{J/m^2}.";
  const html = await render('有限距离分离功：\n$$\n' + tex + '\n$$\n对应输出。');
  assert.match(html, /class="katex-display"/);
  assert.match(html, /<annotation encoding="application\/x-tex">/);
  assert.ok(html.includes(tex));
  assert.match(html, /<p>对应输出。<\/p>/);
});

test('inline subscripts, tables and folded formulas render before Markdown transforms', async () => {
  const html = await render("读出 $\\omega_{\\log}$ 与 $E_{AB}-E_A-E_B$。\n\n| 量 | 表达式 |\n| --- | --- |\n| 密度 | $\\Delta n(z)$ |\n\n<details>\n<summary>推导</summary>\n\n$\\lambda=2\\int_0^\\infty\\frac{\\alpha^2F(\\omega)}{\\omega}d\\omega$\n\n</details>");
  assert.equal((html.match(/class="katex"/g) ?? []).length, 4);
  assert.ok(!html.includes('<em>'));
  assert.match(html, /<details>/);
  assert.match(html, /<td><span class="katex">/);
});

test('terminal variables, heredoc and inline/raw code remain literal', async () => {
  const html = await render("~~~console\n[user@cluster work]$ cat > run.sh <<'EOF'\ncd $SLURM_SUBMIT_DIR\nprintf '$$\\alpha$$'\nEOF\n~~~\n\n`$HOME` <code>$PATH</code> 价格 \\$2。");
  assert.ok(!html.includes('class="katex"'));
  assert.match(html, /cd \$SLURM_SUBMIT_DIR/);
  assert.ok(html.includes("printf '$$\\alpha$$'") || html.includes('printf &#39;$$\\alpha$$&#39;'));
  assert.match(html, /<code>\$HOME<\/code>/);
  assert.match(html, /<code>\$PATH<\/code>/);
  assert.match(html, /价格 \$2。/);
});

test('invalid TeX is a build error', async () => {
  await assert.rejects(() => render('$\\atlasUnknownCommand{x}$'), /Undefined control sequence/);
});
