// 手册正文加载：src/content/manual/<slug>/<engine>.md → 自由叙述渲染。
// 有内容文件：整篇 markdown 渲染为连续正文，标题与分节结构完全由作者自定；
// 无内容文件：返回 null，页面渲染固定 7 节骨架（每节正文「待填充」）。
import { getCollection } from 'astro:content';
import { createSatteriMarkdownProcessor } from '@astrojs/markdown-satteri';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

export async function availableManualIds() {
  const entries = await getCollection('manual');
  return new Set(entries.filter((entry) => entry.body?.trim()).map((entry) => entry.id));
}

// 无内容文件时骨架使用的固定 7 节标题（仅用于占位骨架，不是内容契约）。
export const MANUAL_SECTION_TITLES = [
  '需要 / 产出',
  '本步与相邻步骤不同之处',
  '参数（只列本步）',
  '命令与输出',
  '后处理',
  '失败与假阳性',
  '可选脚本 + 检查清单',
];

// 保留终端原文、缩进与引号；提示符配色在 Markdown 完成 HTML 转义后添加。
let processorPromise = null;
function getProcessor() {
  if (!processorPromise) {
    processorPromise = createSatteriMarkdownProcessor({
      syntaxHighlight: false,
      smartypants: false,
      gfm: true,
    });
  }
  return processorPromise;
}

// 返回整篇正文渲染后的 HTML；无内容文件或空文件时返回 null。
export async function loadManualBody(slug, engine) {
  const id = `${slug}/${engine}`;
  const entries = await getCollection('manual', (entry) => entry.id === id);
  const entry = entries[0];
  if (!entry || typeof entry.body !== 'string') return null;
  const raw = entry.body.trim();
  if (!raw) return null;
  const processor = await getProcessor();
  const { code } = await processor.render(raw);
  let section = 0;
  function downloads(src) {
    const base = import.meta.env.BASE_URL.replace(/\/$/, '');
    if (!src.startsWith(base + '/') || !/\.(png|svg)$/.test(src)) return null;
    const pdf = src.replace(/\.(png|svg)$/, '.pdf');
    const root = resolve(process.cwd(), 'public');
    const file = resolve(root, pdf.slice(base.length + 1));
    if (!file.startsWith(root + '/') || !existsSync(file)) return null;
    return `<a href="${pdf}">矢量 PDF</a><span aria-hidden="true"> · </span><a href="${base}/plotting/">重绘与导出</a>`;
  }
  return code
    .replace(/<figure\b([^>]*)>([\s\S]*?)<\/figure>/g, (whole, attrs, body) => {
      const src = body.match(/<img\s[^>]*src="([^"]+)"/)?.[1];
      const links = src && downloads(src);
      if (!links) return whole;
      const classes = /\bclass="([^"]*)"/.test(attrs)
        ? attrs.replace(/\bclass="([^"]*)"/, 'class="$1 research-figure"')
        : `${attrs} class="research-figure"`;
      const footer = `<span class="figure-downloads">${links}</span>`;
      let content = body.replace(/<img (?![^>]*loading=)/g, '<img loading="lazy" ');
      content = content.includes('</figcaption>')
        ? content.replace('</figcaption>', `${footer}</figcaption>`)
        : `${content}<figcaption>${footer}</figcaption>`;
      return `<figure${classes}>${content}</figure>`;
    })
    .replace(/<p>(<img\s[^>]*src="([^"]+)"[^>]*>)<\/p>/g, (whole, img, src) => {
      const links = downloads(src);
      if (!links) return whole;
      const preview = img.replace('<img ', '<img loading="lazy" ');
      return `<figure class="research-figure"><a href="${src}">${preview}</a><figcaption>${links}</figcaption></figure>`;
    })
    .replace(/<h2(?:\s+id="[^"]*")?>/g, () => `<h2 id="section-${++section}">`)
    .replace(/(<pre><code(?:\s[^>]*)?>)([\s\S]*?)(<\/code><\/pre>)/g, (_, open, body, close) => {
      // 仅包裹已转义的文字，不解析命令，不改写复制出来的会话内容。
      const painted = body.split('\n').map((line) => {
        const prompt = line.match(/^(\[)([\w.-]+@[\w.-]+)( )([^\]\n]+)(\]\$)(.*)$/);
        if (prompt) {
          return `${prompt[1]}<span class="terminal-user">${prompt[2]}</span>${prompt[3]}<span class="terminal-directory">${prompt[4]}</span>${prompt[5]}${prompt[6]}`;
        }
        const shellPrompt = line.match(/^(\([^)]+\) )?([\w.-]+@[\w.-]+)(:)([^$\n]*)(\$)(.*)$/);
        if (shellPrompt) {
          return `${shellPrompt[1] ?? ''}<span class="terminal-user">${shellPrompt[2]}</span>${shellPrompt[3]}<span class="terminal-directory">${shellPrompt[4]}</span>${shellPrompt[5]}${shellPrompt[6]}`;
        }
        if (/^\s*(?:bfgs failed\b|Error in routine\b|convergence NOT achieved\b)/i.test(line)) {
          return `<span class="terminal-error">${line}</span>`;
        }
        return line;
      }).join('\n');
      return open + painted + close;
    });
}
