---
title: "Threat modeling small features"
description: "A lightweight way to find security risks before implementation gets expensive."
date: 2026-07-30
tags:
  - threat-modeling
  - design
---

Threat modeling does not need a large workshop or a complicated diagram. For a small feature, identify the assets, entry points, trust boundaries, and most plausible abuse cases.

## Ask what can go wrong

A short conversation during design is often enough to expose an insecure default, an overly broad permission, or an assumption that nobody had written down.