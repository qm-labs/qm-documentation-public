
# Quantum Machines Documentation

This is the documentation for the Quantum Orchestration Platform (QOP) programming environment, for developers and researchers working with QOP.

Use this page to navigate the main documentation areas and the most common starting points.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Get Started__

    ---

    Start with the core concepts, configuration model, and a first end-to-end example.

    - [:octicons-arrow-right-24: QOP Overview](docs/Introduction/qop_overview.md)
    - [:octicons-arrow-right-24: Configuration](docs/Introduction/config.md)
    - [:octicons-arrow-right-24: QUA Overview](docs/Introduction/qua_overview.md)
    - [:octicons-arrow-right-24: Example Use Case](docs/Introduction/use_case.md)

-   :material-book-open:{ .lg .middle } __Guides__

    ---

    Learn how to use QUA, work with hardware features, and build production workflows.

    - [:octicons-arrow-right-24: QUA Language Features](docs/Guides/features.md)
    - [:octicons-arrow-right-24: Best Practices](docs/Guides/best_practices.md)
    - [:octicons-arrow-right-24: Simulator](docs/Guides/simulator.md)

-   :material-chip:{ .lg .middle } __Hardware__

    ---

    Find installation guides, specifications, and hardware-specific operational details.

    - [:octicons-arrow-right-24: OPX1000 Specification](docs/Hardware/OPX1000_hardware.md)
    - [:octicons-arrow-right-24: OPX1000 Installation](docs/Hardware/OPX1000_installation.md)
    - [:octicons-arrow-right-24: OPX+ Installation](docs/Hardware/opx+installation.md)

-   :material-information:{ .lg .middle } __API References__

    ---

    Explore the QUA API, configuration schema, and device-specific APIs.

    - [:octicons-arrow-right-24: QUA API](docs/API_references/qua/dsl_main.md)
    - [:octicons-arrow-right-24: Configuration API](docs/API_references/config_spec.md)

-   :material-tag-outline:{ .lg .middle } __Releases__

    ---

    Check version-specific installation guidance, compatibility notes, and release history.

    - [:octicons-arrow-right-24: QOP Installation Guide](docs/Releases/qop_installation_guide.md)
    - [:octicons-arrow-right-24: OPX1000 Releases](docs/Releases/qop3_releases.md)
    - [:octicons-arrow-right-24: qm-qua Releases](docs/Releases/qm_qua_releases.md)

-   :material-source-repository-multiple:{ .lg .middle } __Solutions Repositories__

    ---

    Browse open-source QUA libraries and tools built on top of the platform.

    - [:octicons-arrow-right-24: QUA Libraries](docs/Libraries/libs_repository.md)
    - [:octicons-arrow-right-24: QUA Tools](docs/Libraries/tools_repository.md)

-   :material-lifebuoy:{ .lg .middle } __Support__

    ---

    Get help and provide feedback.

    - [:octicons-arrow-right-24: Feedback and Support](docs/support.md)

-   :material-shield-check:{ .lg .middle } __Safety Information__

    ---

    Review safety requirements and precautions for operating QM hardware.

    - [:octicons-arrow-right-24: Safety Information](docs/safety.md)
</div>

??? info "Shields usage in the documentation"

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
