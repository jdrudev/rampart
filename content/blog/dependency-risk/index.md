---
title: "A small dependency is still a security decision"
description: "Lessons from reviewing third-party packages in otherwise simple services."
date: 2026-08-14
tags:
  - supply-chain
  - dependencies
---

Every dependency adds code, maintenance, and a new source of change. The right question is not whether dependencies are bad; it is whether their value and update path are understood.

## Keep the path visible

Lockfiles, automated updates, and a short record of why a package exists make review practical. The goal is not zero dependencies. The goal is no invisible dependencies.