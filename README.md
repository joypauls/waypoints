# Waypoints [WIP]

A simple utility for giving data science development workflows memory with zero dependencies. Whether you use it with messy notebook code or to decorate functions, Waypoints can help reduce your cognitive load and save you time and compute rerunning expensive steps.

## Features

No server, no UI, just local files.

- simple object persistence

## Why?

Nothing did exactly what I wanted so I kept developing the same bespoke functionality over and over again that was tangential to my actual project at hand. While my teams have adopted heavier MLOps pipeline frameworks for production, initial development and the experimental phase is usually ad-hoc and cumbersome. Staying resilient to kernel restarts in a notebook environment, saving intermediate reults, reusing artifacts across different runs, recording what happened; it can get messy. I wanted something to help me focus on what's important but doesn't impose too much structure. Notebooks are popular because they allow for a sort of "stream of conciousness" approach to coding, and anything that takes away from that too much will be tough to accept, even for me.

Ultimately I built this for my own workflow first and now I'm hoping others find it useful too!

---

## Aren't there tools out there for this already?

There are many out there that overlap and are very good. Most of them aim do much more than this tool does. Waypoints is trying to solve a small subset of related problems to help in the messy experimental phase - when projects are iterating fast and people are resistent to heavy frameworks. While it's certainly safe for production, that's not what it's built for and you will probably end up wanting a more robust pipeline framework.

Libraries/tools that inspired design choices:

- MLflow
- Prefect
- joblib
- Hamilton
- ipycache
