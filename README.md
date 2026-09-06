# Rampart

Rampart is an anonymous collection of cybersecurity engineering notes, lessons learned, and practical systems thinking.

The production site is served at [rampart.jdru.dev](https://rampart.jdru.dev).

## Stack

- Astro + npm for the static website.
- Markdown content validated with Astro schemas and a Python content check.
- Python Confluence sync for pages carrying the `portfolio-public` label.
- GitHub Actions and GitHub Pages for CI and deployment.

## Site routes

- `/` - Rampart home page.
- `/blogs/` - searchable posts archive with tag filters.
- `/blogs/<post>/` - individual post pages.

The production site uses the custom domain [rampart.jdru.dev](https://rampart.jdru.dev). Local development uses the same routes from the Astro dev server.

## Local development

```bash
npm install
npm run dev
```

Useful checks:

```bash
npm run check
npm run validate
npm run build
```

Posts live in `content/blog/` as Markdown or MDX files. Each post requires a title, description, date, and tags. The sample collection includes several cybersecurity topics for testing search and filtering.

## Confluence sync

Copy `.env.example` to a local environment and provide a read-only Confluence API token. The sync job only reads pages explicitly labelled `portfolio-public`; credentials are never committed or exposed to the browser.

The scheduled GitHub Action requires repository secrets named `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN`. A failed API query stops the workflow before reconciliation so existing published content is preserved.

## Custom domain

GitHub Pages must be configured to use `rampart.jdru.dev` in the repository Pages settings. The DNS provider should have a CNAME record for `rampart` pointing to the repository owner's GitHub Pages hostname. `public/CNAME` is included in every build so the domain remains attached to future deployments.
