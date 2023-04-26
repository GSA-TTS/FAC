# 1. Data validation schema in Jsonnet

Date: 2023-04-10

## Status

Accepted

## Context

We use JSON schema for data validation (ADR 0014). This ADR recommends *not* authoring the schema in vanilla JSON, but instead in [Jsonnet](https://jsonnet.org). This is an extended JSON.

Jsonnet provides several features:

1. Comments
2. Composability
3. Variables
4. Scoped imports

These allow for things like:

1. Inline documentation in the schema.
2. Base schema definitions that can be modified through functional/logical (e.g. union) operations on objects
3. Giving names to reusable components
4. Breaking reusable components into libraries

This also provides a layer of validation on our schema; a valid Jsonnet file will compile to JSON, and the resulting JSON document will be correct. An invalid Jsonnet will not compile. This provides a level of assurance that our JSON Schema are valid.

## Decision

We will author our schema (which validate forms and spreadsheets in the project) in Jsonnet.

We will keep the rendered JSON schemas in the repository, even though they are "build products." This gives us some stability (and makes testing easier). Changes to schema should not happen often.

We will organize the soure .jsonnet/libsonnet files and rendered JSON schemas in a sensible way, and create a `Makefile` or similar to aid with schema development.

## Consequences

This adds another tool to our backend pipeline, and a dependancy that could break in the future. However, Jsonnet is not new, and has broad community support. If support for the tool ends, we can always continue with our JSON Schema "as-is," and maintain them the hard way. (And, there are ways to achieve composability within JSON Schema, but we lose things like comments and variables.)

There are no security implications that we are aware of from use of this tool as a compiler; no more than using any other compiler, that is. This tooling is part of our build process, and is not exposed as part of the user-facing application.

