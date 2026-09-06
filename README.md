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
- `/blog/<confluence-id>/` - individual post pages.

The production site uses the custom domain [rampart.jdru.dev](https://rampart.jdru.dev). Local development uses the same routes from the Astro dev server.

## Quick start

```bash
npm install
npm run dev
```

Run the project checks before publishing:

```bash
npm run check
npm run validate
npm run build
```

Posts live in `content/blog/` as generated Markdown files. Confluence is the source of truth for this directory, so a successful sync can remove manually authored posts placed there. Each generated post requires a title, description, date, tags, and immutable `confluence_id`.

## Confluence sync

The sync job publishes only Confluence pages explicitly labelled `portfolio-public`. It reads content, converts it to Markdown, and reconciles `content/blog/` with the published pages. Credentials are used by the sync process only and are never exposed to the browser.

### Local configuration

Copy `.env.example` to `.env` and provide a read-only Confluence API token. `.env` is ignored by Git.

The required values are:

```text
CONFLUENCE_BASE_URL
CONFLUENCE_EMAIL
CONFLUENCE_API_TOKEN
```

Optional values are:

```text
CONFLUENCE_CLOUD_ID
CONFLUENCE_SPACE=Portfolio
CONFLUENCE_CONTENT_TYPE=page
```

`CONFLUENCE_BASE_URL` accepts either `tenant.atlassian.net` or a full HTTPS URL. The client normalizes hostnames to HTTPS and rejects insecure URLs. Set `CONFLUENCE_SPACE` when using a different space. Set `CONFLUENCE_CONTENT_TYPE=blogpost` only when using Confluence Blog Posts instead of regular pages.

### Required permissions

Create a Confluence-scoped token with:

```text
search:confluence
read:confluence-content.all
read:confluence-space.summary
read:confluence-user
```

The token owner must also be able to view the configured Confluence space and pages. Jira access is not required. The default source is a normal Confluence page.

### Local diagnostic

Test the credentials without changing content:

```bash
python -m scripts.confluence.check_credentials
```

The diagnostic loads `.env`, checks authentication and access to the configured query, and never prints the email or token.

### GitHub Actions

The scheduled sync requires these repository secrets:

```text
CONFLUENCE_BASE_URL
CONFLUENCE_EMAIL
CONFLUENCE_API_TOKEN
```

`CONFLUENCE_CLOUD_ID`, `CONFLUENCE_SPACE`, and `CONFLUENCE_CONTENT_TYPE` can be configured as repository variables. A failed API query stops the workflow before reconciliation, preserving the existing published content.

To check GitHub credentials without syncing content, open **Actions**, select **Check Confluence credentials**, and choose **Run workflow**. This workflow has read-only repository permissions and does not commit or deploy.

### Failure handling

- Missing-variable errors mean a required local `.env` value is absent.
- A page or API `401` usually means the email, token, or token permissions are incorrect.
- Network errors mean the runner could not reach Confluence.
- An empty publication query fails closed when local content exists, preventing accidental deletion.

Set `CONFLUENCE_ALLOW_EMPTY_SYNC=true` only when intentionally removing all published content. Attachments and embedded images are not synchronized.

## Deployment

GitHub Pages must be configured to use `rampart.jdru.dev` in the repository Pages settings. The DNS provider should have a CNAME record for `rampart` pointing to the repository owner's GitHub Pages hostname. `public/CNAME` is included in every build so the domain remains attached to future deployments.
