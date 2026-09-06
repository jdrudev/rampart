# Design decisions

## 001: Static Astro site with npm

**Date:** 2026-09-06

**Decision:** Use Astro for static rendering and npm for dependency management.

**Why:** The portfolio is primarily static content, GitHub Pages needs no server runtime, and Astro keeps browser JavaScript small while retaining a straightforward Markdown content model.

**Trade-off:** The site has a Node-based build step, but avoids a custom build system and remains easy to run locally with standard npm commands.

## 002: Confluence label-gated publishing

**Date:** 2026-09-06

**Decision:** Synchronize only Confluence pages carrying the exact `portfolio-public` label.

**Why:** Page location alone is not an adequate publication control. The explicit label makes the public boundary intentional.

**Trade-off:** Articles need correct metadata before they appear, but accidental publication is less likely.