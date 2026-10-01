import katex from '../vendor/katex/katex.mjs';
import { defineMdastPlugin, markdownToMdast } from 'satteri';

export function createMathPlugin() {
  function render(node, ctx, displayMode) {
    // Parse before Markdown escapes; fail the build on invalid TeX.
    const html = katex.renderToString(node.value, {
      displayMode, throwOnError: true,
      output: 'htmlAndMathml', trust: false,
    });
    ctx.replaceNode(node, { type: 'html', value: html });
  }
  return defineMdastPlugin({
    name: 'atlas-math',
    inlineMath: (node, ctx) => render(node, ctx, false),
    math: (node, ctx) => render(node, ctx, true),
  });
}

export function protectHtmlCode(raw) {
  if (!/<(?:code|pre|kbd|samp)\b/i.test(raw)) return raw;
  const tree = markdownToMdast(raw, { features: { math: false }, position: true });
  const tags = [];
  function walk(node) {
    if (node.type === 'html' && !node.value.startsWith('<!--')) {
      for (const match of node.value.matchAll(/<(\/?)(code|pre|kbd|samp)\b[^>]*>/gi)) {
        tags.push({
          close: Boolean(match[1]), tag: match[2].toLowerCase(),
          selfClosing: /\/>$/.test(match[0]),
          start: node.position.start.offset + match.index,
          end: node.position.start.offset + match.index + match[0].length,
        });
      }
    }
    node.children?.forEach(walk);
  }
  walk(tree);
  tags.sort((a, b) => a.start - b.start);
  const stack = [], ranges = [];
  for (const token of tags) {
    if (token.selfClosing) continue;
    if (!token.close) stack.push(token);
    else if (stack.at(-1)?.tag === token.tag) {
      const opening = stack.pop();
      if (!stack.length) ranges.push([opening.start, token.end]);
    }
  }
  // Only HTML source nodes are shielded; fenced and backtick code are untouched.
  for (const [start, end] of ranges.reverse()) {
    raw = raw.slice(0, start) + raw.slice(start, end).replace(/\$/g, '&#36;') + raw.slice(end);
  }
  return raw;
}
