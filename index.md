
# About this Document

Welcome to the official documentation of Quantum Machines.
This document introduces and details the Quantum Orchestration Platform (QOP) programming environment.
It is intended for quantum developers and researchers working with the QOP.

Here's what you will find here: 

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Introduction__

    ---

    Get an overview of the core concepts of the QOP as well as a usage example  

    [:octicons-arrow-right-24: QOP Overview](docs/Introduction/qop_overview.md)

-   :material-book-open:{ .lg .middle } __Guides__

    ---

    Dive into the details of all the features and capabilities of the QOP!

    [:octicons-arrow-right-24: Features Guide](docs/Guides/features.md)

-   :fontawesome-solid-gears:{ .lg .middle } __Hardware__

    ---

    Find installation guides and specification of our hardware components 

    [:octicons-arrow-right-24: Install](docs/Hardware/opx+installation.md)

-   :material-information:{ .lg .middle } __API References__

    ---

    Explore our [API](docs/API_references/qua/dsl_main.md)

[comment]: <> (    [:octicons-arrow-right-24: API]&#40;./docs/Hardware/opx+installation.md&#41;)

</div>

!!! Info "Shields Usage in the Documentation"

    As more and more hardware products and QUA features are joining the QM arsenal, the documentation grows and branches out.
    Keeping our documentation under a single (virtual) roof means that some of the features documented here are only applicable
    for specific combinations of hardware and software.

    To keep track of these specifications we introduce the usage of `shields`.

    - Blue shields specify the required hardware and QOP version.
    - Green shields indicate the required minimal version of QUA.
    - Orange shields indicate required hardware add-ons, such as Octave.

    For example, a feature that only works on an OPX+ with QOP version >2.0, with the Octave add-on, and requires QUA version >0.3.3 will have these shields:
    {{ requirement("OPX+", "2.0.0") }}
    {{ requirement("QUA", "0.3.3") }}
    {{ requirement("Octave") }}
