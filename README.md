⚠️ Coming Soon

# Waypoints [WIP]

A simple and lightweight utility for making multi-step Python workflows durable. Built for the messy, experimental phase when you find yourself rerunning the same steps to test a variant, recovering after a kernel crash, or manually saving intermediate outputs. With zero dependencies and no setup needed, it can fit into any project.

## Install

```
pip install waypoints
```

## How It Works

### Example

At minimum, this functions as a simple cache which can be useful on its own. But it also enables branching.

### Branching Example

### What's On Disk

```
.waypoints/
```

## Core Concepts

- **run** — a named execution session for a pipeline. Created with `wp.start()`. All operations hang off the run object.
- **step** — a named unit of work within a run. Produces a value. Reused if already complete.
- **reuse** — when a step's saved result is returned without recomputing.
- **recompute** — when a step is run fresh, either because it hasn't run before or was cleared.
- **cascade** — when a step is recomputed, all steps after it in execution order are automatically invalidated.

## Why?

Ultimately I built this for my own workflow first and now I'm hoping others find it useful too!

Experimental work tends to be fast-moving and very unstructured. You run a few steps, inspect the output, tweak something upstream, and rerun. You save intermediate results when things get expensive, but those saves are usually ad-hoc pickle files here, CSVs there, maybe a log file or two. After a restart or a few days away, it’s not always clear what was run, what can be reused, or what needs to be recomputed. Waypoints is meant to cover some middle ground:

- more structured than one-off saves and glue code
- much lighter than a full orchestration or MLOps framework
