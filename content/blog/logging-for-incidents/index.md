---
title: "TEST: Logging for incident response"
description: "What useful security telemetry looks like before an incident starts."
date: 2026-08-21
tags:
  - detection
  - observability
---

Logs are only useful during an incident if they answer questions quickly. That means consistent timestamps, stable actor identifiers, useful request context, and retention that matches the risks being investigated.

## Start with questions

Instead of collecting everything, write down the questions an investigator will need to answer. Then check whether the current telemetry can answer them without guesswork.