---
title: "Identity boundaries are system boundaries"
description: "A practical look at where authentication ends and authorization begins."
date: 2026-08-28
tags:
  - identity
  - access-control
---

Authentication answers who or what is making a request. Authorization answers what that identity is allowed to do. Treating them as the same concern makes systems harder to reason about.

## Make the decision visible

Access decisions should be inspectable in logs and understandable from policy. Clear boundaries make incident review faster and reduce the chance that a broad role quietly becomes permanent.