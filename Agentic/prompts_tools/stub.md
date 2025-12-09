
## Simplification Policy for Non-Core Concerns

To keep the implementation self-contained and dependency-free, you may simplify or stub non-core concerns. When doing so:
- Logging and Printing: Replace logging/formatting (including file I/O) with minimal print() calls or no-ops when acceptable.
- Memory Management: Use standard malloc()/free() for dynamic allocation; remove custom allocators or pooling systems.
- Error Handling: Simplify exceptions and error propagation to simple return codes or exit() where appropriate.
- Assertions and Validation: Replace custom assertion frameworks with assert() or remove them if non-critical to core logic.
- Non-STD Dependency Libraries: Replace third-party libraries or system calls with local implementations.
- Hardware Dependencies: Stub out hardware-specific code with software equivalents or no-ops.

If code does not meet the above policies, you CANNOT simplify or stub it.
For each simplification or stub, you must provide a brief justification explaining why it is necessary to maintain self-containment or to remove external dependencies while preserving core logic.
