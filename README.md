# Rampart

Rampart is a collection of cybersecurity engineering notes, lessons learned, and practical systems thinking.

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

The scheduled GitHub Action requires repository secrets named `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN`. `CONFLUENCE_BASE_URL` may be entered as either `tenant.atlassian.net` or `https://tenant.atlassian.net`; the client normalizes hostnames to HTTPS and rejects insecure URLs. For scoped API tokens such as `read:page:confluence`, set the repository variable `CONFLUENCE_CLOUD_ID`; requests then use the Atlassian API gateway. Set `CONFLUENCE_SPACE` to the space name or key if it differs from `Portfolio`. A failed API query stops the workflow before reconciliation so existing published content is preserved.

To test the same credentials locally without changing Confluence content, copy `.env.example` to `.env`, fill in the values, and run:

```bash
python -m scripts.confluence.check_credentials
```

The diagnostic loads `.env` automatically and checks authentication, readable spaces, and the intended query: `Portfolio` space, `page` type, and `portfolio-public` label. Set `CONFLUENCE_CONTENT_TYPE=blogpost` only if you intentionally use Confluence Blog Posts. It never prints the email or token. Keep `.env` uncommitted; it is ignored by Git.

The same diagnostic can run against GitHub Secrets without syncing content: open **Actions**, choose **Check Confluence credentials**, and click **Run workflow**. This workflow has read-only repository permissions and does not commit or deploy anything.

## Custom domain

GitHub Pages must be configured to use `rampart.jdru.dev` in the repository Pages settings. The DNS provider should have a CNAME record for `rampart` pointing to the repository owner's GitHub Pages hostname. `public/CNAME` is included in every build so the domain remains attached to future deployments.
