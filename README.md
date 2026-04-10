# Waypoints [WIP]

A simple utility for giving data science development workflows memory with zero dependencies.

Whether you use it with messy notebook code or decorate functions, Waypoints can help keep your mind on what's important and save you time rerunning expensive steps.

## Features

No server, no UI, just local files.

---

## Why?

Nothing did exactly what I wanted so I kept developing the same bespoke functionality over and over again that was tangential to my actual project at hand. While my teams have generally adopted heavier frameworks for production, development and the experimental phase is usually the ad-hoc and cumbersome. Saving intermediate reults, reusing artifacts for different runs, recording what happened, staying resilient to kernel restarts in anotebook environment; it gets messy. I wanted something to help me focus on what's important but doesn't impose too much structure. Notebooks are popular because they allow a sort of "stream of conciousness" approach to coding, and anything that takes away from that will be tough to accept.

I built this for myself first and now I'm hoping others find it useful too!

---

## Aren't there tools out there for this?

There are many out there that overlap and are very good. Most of them aim do much more than this tool does. Waypoints is trying to solve a tiny problem to help in the messy experimental phase - when projects are iterating fast. While it's certainly safe for production pipelines, that's not what it's built for and you will probably end up wanting a more robust framework.

Libraries/tools that inspired design choices:

- MLflow
- Prefect
- joblib
- Hamilton
- ipycache
