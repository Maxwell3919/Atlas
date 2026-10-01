import { getCollection } from 'astro:content';
import { createSatteriMarkdownProcessor } from '@astrojs/markdown-satteri';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import publishedIds from '../data/published-manuals.json';
import { isManualVisible } from '../data/methods.js';
import legacyHeadings from '../data/legacy-headings.json';
import legacyDestinations from '../data/legacy-destinations.json';

// Publication is explicit: adding a draft to the collection does not publish it.
const published = new Set(publishedIds);
export async function availableManualIds() {
  const entries = await getCollection('manual');
  return new Set(entries.filter((entry) => published.has(entry.id) && isManualVisible(entry.id) && entry.body?.trim()).map((entry) => entry.id));
}

let processorPromise;
function getProcessor() {
  return processorPromise ??= createSatteriMarkdownProcessor({ syntaxHighlight: false, smartypants: false, gfm: true });
}
function plainText(html) {
  return html.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}
function headingId(label) {
  return `h-${plainText(label).normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '').slice(0, 90) || 'section'}`;
}
export function bodySections(body) {
  return [...body.matchAll(/<h2\b[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)<\/h2>/g)].map((match) => ({ id: match[1], label: match[2].replace(/<[^>]*>/g, '') }));
}

export async function renderMarkdownBody(raw, { id } = {}) {
  const processor = await getProcessor();
  const { code } = await processor.render(raw);
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  function downloads(src) {
    if (!src.startsWith(base + '/') || !/\.(png|svg)$/.test(src)) return null;
    const pdf = src.replace(/\.(png|svg)$/, '.pdf');
    const root = resolve(process.cwd(), 'public');
    const file = resolve(root, pdf.slice(base.length + 1));
    if (!file.startsWith(root + '/') || !existsSync(file)) return null;
    return `<a href="${pdf}">矢量 PDF</a><span aria-hidden="true"> · </span><a href="${base}/plotting/">重绘与导出</a>`;
  }
  const usedIds = new Set([...code.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));
  const headingLabels = [...code.matchAll(/<h2\b[^>]*>([\s\S]*?)<\/h2>/g)].map((match) => plainText(match[1]));
  const oldLabels = legacyHeadings[id] ?? headingLabels;
  const aliases = new Map();
  let introductoryAliases = '';
  oldLabels.forEach((label, index) => {
    const alias = `section-${index + 1}`;
    const destination = legacyDestinations[id]?.[label] ?? label;
    if (destination === '@intro') introductoryAliases += `<span id="${alias}" class="legacy-anchor" aria-hidden="true"></span>`;
    else if (typeof destination === 'object') introductoryAliases += `<span id="${alias}" class="legacy-anchor" data-legacy-target="${base}${destination.route}#${headingId(destination.heading)}" aria-hidden="true"></span>`;
    else {
      if (!headingLabels.includes(destination)) throw new Error(`Unmapped legacy heading: ${id} / ${label}`);
      aliases.set(destination, [...(aliases.get(destination) ?? []), alias]);
    }
  });
  const emitted = new Set();
  return introductoryAliases + code
    .replace(/<figure\b([^>]*)>([\s\S]*?)<\/figure>/g, (whole, attrs, body) => {
      const src = body.match(/<img\s[^>]*src="([^"]+)"/)?.[1];
      const links = src && downloads(src);
      if (!links) return whole;
      const classes = /\bclass="([^"]*)"/.test(attrs)
        ? attrs.replace(/\bclass="([^"]*)"/, 'class="$1 research-figure"')
        : `${attrs} class="research-figure"`;
      const footer = `<span class="figure-downloads">${links}</span>`;
      let content = body.replace(/<img (?![^>]*loading=)/g, '<img loading="lazy" ');
      content = content.includes('</figcaption>') ? content.replace('</figcaption>', `${footer}</figcaption>`) : `${content}<figcaption>${footer}</figcaption>`;
      return `<figure${classes}>${content}</figure>`;
    })
    .replace(/<p>(<img\s[^>]*src="([^"]+)"[^>]*>)<\/p>/g, (whole, img, src) => {
      const links = downloads(src);
      if (!links) return whole;
      return `<figure class="research-figure"><a href="${src}">${img.replace('<img ', '<img loading="lazy" ')}</a><figcaption>${links}</figcaption></figure>`;
    })
    .replace(/<h([23])\b([^>]*)>([\s\S]*?)<\/h\1>/g, (whole, level, attrs, label) => {
      const previousId = attrs.match(/\bid="([^"]+)"/)?.[1];
      if (previousId) usedIds.delete(previousId);
      let anchor = headingId(label);
      const root = anchor; let repeat = 2;
      while (usedIds.has(anchor) || emitted.has(anchor)) anchor = `${root}-${repeat++}`;
      usedIds.add(anchor);
      const compatible = level === '2' ? (aliases.get(plainText(label)) ?? []).filter((alias) => !usedIds.has(alias) && !emitted.has(alias)).map((alias) => {
        emitted.add(alias);
        return `<span id="${alias}" class="legacy-anchor" aria-hidden="true"></span>`;
      }).join('') : '';
      const previousAlias = previousId && previousId !== anchor && !emitted.has(previousId)
        ? `<span id="${previousId}" class="legacy-anchor" aria-hidden="true"></span>` : '';
      if (previousAlias) { emitted.add(previousId); usedIds.add(previousId); }
      return `${compatible}${previousAlias}<h${level}${attrs.replace(/\s*id="[^"]*"/, '')} id="${anchor}">${label}</h${level}>`;
    })
    .replace(/(<pre><code(?:\s[^>]*)?>)([\s\S]*?)(<\/code><\/pre>)/g, (_, open, body, close) => {
      const painted = body.split('\n').map((line) => {
        const prompt = line.match(/^(\[)([\w.-]+@[\w.-]+)( )([^\]\n]+)(\]\$)(.*)$/);
        if (prompt) return `${prompt[1]}<span class="terminal-user">${prompt[2]}</span>${prompt[3]}<span class="terminal-directory">${prompt[4]}</span>${prompt[5]}${prompt[6]}`;
        const shellPrompt = line.match(/^(\([^)]+\) )?([\w.-]+@[\w.-]+)(:)([^$\n]*)(\$)(.*)$/);
        if (shellPrompt) return `${shellPrompt[1] ?? ''}<span class="terminal-user">${shellPrompt[2]}</span>${shellPrompt[3]}<span class="terminal-directory">${shellPrompt[4]}</span>${shellPrompt[5]}${shellPrompt[6]}`;
        if (/^\s*(?:bfgs failed\b|Error in routine\b|convergence NOT achieved\b)/i.test(line)) return `<span class="terminal-error">${line}</span>`;
        return line;
      }).join('\n');
      return open + painted + close;
    });
}

export async function loadManualBody(slug, engine) {
  const id = `${slug}/${engine}`;
  if (!published.has(id)) return null;
  const entries = await getCollection('manual', (entry) => entry.id === id);
  const raw = entries[0]?.body?.trim();
  return raw ? renderMarkdownBody(raw, { id }) : null;
}
