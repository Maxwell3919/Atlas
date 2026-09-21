// 手册正文加载：src/content/manual/<slug>/<engine>.md → 按 7 个固定 H2 分节。
// 约定：正文 = 恰好这 7 个 H2（顺序即下表）；可省略若干节，省略/空节渲染为「待填充」。
// 节内可用 H3 及以下小标题，但不得出现其他 H2。首个 H2 之前的文字不渲染。
import { getCollection } from 'astro:content';
import { createSatteriMarkdownProcessor } from '@astrojs/markdown-satteri';

export const MANUAL_SECTION_TITLES = [
  '需要 / 产出',
  '本步与相邻步骤不同之处',
  '参数（只列本步）',
  '命令与输出',
  '后处理',
  '失败与假阳性',
  '可选脚本 + 检查清单',
];

// 一次构建共享一个 markdown 处理器；关闭 shiki 与 smartypants，
// 让围栏代码块走站内 CSS 变量（明暗两套主题都干净），CLI 选项不被弯引号改写。
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

// 按「恰好等于 ## <固定标题> 的行」切分；``` / ~~~ 围栏内的行不参与切分。
function splitSections(body) {
  const parts = new Map();
  let current = null;
  let fence = null;
  for (const line of body.split('\n')) {
    const trimmed = line.trim();
    const fenceOpen = trimmed.match(/^(```|~~~)/);
    if (fenceOpen) {
      fence = fence ? null : fenceOpen[1];
      if (current) current.push(line);
      continue;
    }
    if (!fence) {
      const title = MANUAL_SECTION_TITLES.find((t) => trimmed === '## ' + t);
      if (title) {
        current = [];
        parts.set(title, current);
        continue;
      }
    }
    if (current) current.push(line);
  }
  return parts;
}

// 返回固定 7 节：{ title, html }；html 为 null 表示该节应渲染「待填充」。
export async function loadManualSections(slug, engine) {
  const id = `${slug}/${engine}`;
  const entries = await getCollection('manual', (entry) => entry.id === id);
  const entry = entries[0];

  const filled = new Map();
  if (entry && typeof entry.body === 'string') {
    const parts = splitSections(entry.body);
    const processor = await getProcessor();
    for (const [title, lines] of parts) {
      const raw = lines.join('\n').trim();
      if (!raw) continue;
      const { code } = await processor.render(raw);
      filled.set(title, code);
    }
  }

  return MANUAL_SECTION_TITLES.map((title) => ({
    title,
    html: filled.get(title) ?? null,
  }));
}
