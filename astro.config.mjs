import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://rampart.jdru.dev',
  base: '/',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
  integrations: [mdx()],
  markdown: {
    shikiConfig: { theme: 'github-dark' }
  }
});