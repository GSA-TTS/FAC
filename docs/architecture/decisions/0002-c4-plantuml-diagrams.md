# 2. Use C4-Plantuml for system visualizations and diagrams

Date: 2022-03-16

## Status

Accepted

## Context

We need visualizations and system diagrams to document and share our efforts as well as meet compliance requirements.

## Decision

We will use [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) to implement our visualizations and diagrams.

C4-PlantUML combines the benefits of [PlantUML](https://plantuml.com/) and the [C4 model](https://c4model.com/) for providing a simple way of describing and communicate software architectures – especially during up-front design sessions – with an intuitive language using open source and platform independent tools.

## Consequences

 -  All visualizations and system diagrams will be implemented in C4-PlantUML markdown
 - C4-PlantUML has been and continues to be used successfully across projects at GSA such as login.gov, cloud.gov, data.gov, and more. We'll build upon this work and contribute back GSA's community leveraging C4-PlantUML.

