---
title: "Keeping secrets out of CI logs"
description: "A checklist for handling credentials safely in automated pipelines."
date: 2026-08-07
tags:
  - ci-cd
  - secrets
---

Credentials should enter a pipeline as late as possible, exist only for the steps that need them, and never be printed as part of normal diagnostics.

## Reduce exposure

Use short-lived credentials where possible, keep permissions narrow, and treat pull request workflows from untrusted code as a separate trust boundary.