# Diagrams

We use [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) to document and generate diagrams.

C4-PlantUML combines the benefits of PlantUML and the C4 model for providing a simple way of describing and communicate software architectures.  [PlantUML](http://en.plantuml.com/) is an open source project that allows you to create UML diagrams using code.  [C4 model](https://c4model.com/) for software architecture is an "abstraction-first" approach to diagramming, based upon abstractions that reflect how software architects and developers think about and build software.

## Structures
Each `.puml` file in the `./src` folder represents one diagram written in C4-PlantUML. The file structure is as follows:
- `@startuml`
- included files - specific type of C4 diagram this file represents and other files it uses
- elements - define elements like system, container, person
- relationships - define relationships between elements
- `@enduml`
