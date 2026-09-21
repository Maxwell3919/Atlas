// Atlas 手册正文集合：src/content/manual/<slug>/<engine>.md
// 纯 markdown，无 front matter；正文按 7 个固定 H2 分节（见 src/lib/manual.js）。
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const manual = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/manual' }),
});

export const collections = { manual };
