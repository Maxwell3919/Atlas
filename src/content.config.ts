// Atlas 手册正文集合：src/content/manual/<slug>/<engine>.md
// 自由 Markdown 正文；分节随计算操作组织。
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const manual = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/manual' }),
});

export const collections = { manual };
