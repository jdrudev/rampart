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

Posts live in `content/blog/` as generated Markdown files. Confluence is the source of truth for this directory: a successful sync reconciles it to pages carrying `portfolio-public`, so manually authored posts placed there may be removed. Each generated post requires a title, description, date, tags, and immutable `confluence_id`.

## Confluence sync

Copy `.env.example` to a local environment and provide a read-only Confluence API token. The sync job only reads pages explicitly labelled `portfolio-public`; credentials are never committed or exposed to the browser.

### Required permissions

Create a Confluence-scoped token with these permissions:

```text
search:confluence
read:attachment:confluence
read:confluence-content.all
read:confluence-space.summary
read:confluence-user
readonly:content.attachment:confluence
```

`readonly:content.attachment:confluence` is required for image sync: the sync job lists and downloads page attachments via `/wiki/rest/api/content/{id}/child/attachment`, which is a separate scope from page content read access.

The token owner must also have permission to view the `Portfolio` space and page `3309652`. Jira or any other Atlassian product is not required. The published source is a normal Confluence page, not a Blog Post, so the default content type is `page`.

The scheduled GitHub Action requires repository secrets named `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN`. `CONFLUENCE_BASE_URL` may be entered as either `tenant.atlassian.net` or `https://tenant.atlassian.net`; the client normalizes hostnames to HTTPS and rejects insecure URLs. For scoped API tokens such as `read:page:confluence`, the client automatically resolves the public Cloud ID from the tenant metadata endpoint and routes requests through the Atlassian API gateway. `CONFLUENCE_CLOUD_ID` is optional if you prefer to configure it explicitly. Set `CONFLUENCE_SPACE` to the space name or key if it differs from `Portfolio`. A failed API query stops the workflow before reconciliation so existing published content is preserved.

To test the same credentials locally without changing Confluence content, copy `.env.example` to `.env`, fill in the values, and run:

```bash
python -m scripts.confluence.check_credentials
```

The diagnostic loads `.env` automatically and checks authentication, readable spaces, and the intended query: `Portfolio` space, `page` type, and `portfolio-public` label. Set `CONFLUENCE_CONTENT_TYPE=blogpost` only if you intentionally use Confluence Blog Posts. It never prints the email or token. Keep `.env` uncommitted; it is ignored by Git.

The same diagnostic can run against GitHub Secrets without syncing content: open **Actions**, choose **Check Confluence credentials**, and click **Run workflow**. This workflow has read-only repository permissions and does not commit or deploy anything.

Diagnostic and sync errors have different meanings: a missing-variable configuration error means a required local `.env` value is absent; a Cloud ID resolution error means the tenant metadata endpoint could not be read; a page/API `401` means the email/token authentication or scoped-token gateway configuration is not accepted; an attachment `401` means page discovery succeeded but attachment access was rejected; an attachment `403` means authentication succeeded but the account/token lacks attachment access; a network error means the runner could not reach Confluence; `0 matching pages` fails closed when local content exists, preventing accidental deletion. Attachment checks use the REST v2 endpoint `/wiki/api/v2/pages/<id>/attachments`, which requires the exact scoped permission `read:attachment:confluence`; `readonly:content.attachment:confluence` is a different v1 permission and does not satisfy the v2 route. Set `CONFLUENCE_ALLOW_EMPTY_SYNC=true` only when intentionally removing all published content. The diagnostic also checks attachment access for matched pages because image synchronization uses the attachment endpoint. A successful publication query prints the matched page title and ID before sync continues.

## Custom domain

GitHub Pages must be configured to use `rampart.jdru.dev` in the repository Pages settings. The DNS provider should have a CNAME record for `rampart` pointing to the repository owner's GitHub Pages hostname. `public/CNAME` is included in every build so the domain remains attached to future deployments.
