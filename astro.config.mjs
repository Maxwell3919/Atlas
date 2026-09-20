import { defineConfig } from 'astro/config'
import node from '@astrojs/node'

export default defineConfig({
  site: 'https://maxwell3919.github.io',
  base: '/Atlas',
  output: 'static',
  build: {
    format: 'directory'
  },
  integrations: [],
  adapter: node({
    mode: 'standalone'
  })
})
