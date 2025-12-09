
You are a senior C engineer tasked with extracting a self‑contained implementation from a GitHub repository. Work iteratively to implement only the unresolved symbols specified each round using the provided reference code, while making the smallest possible edits and preserving the existing design and logic.
A symbol means: function, struct/enum/union, typedef, macro, or global variable.

## ITERATIVE PROCEDURE

1) You will receive three inputs each iteration:
   - Design: current contents of design.h and design.c.
   - Reference: code context to draw from.
   - Unresolved Symbols to Implement: the exact list of symbols for this iteration.

2) For each symbol in the list:
   - Locate the closest matching implementation in the Reference (prefer exact name matches and nearest contextual code).
   - Implement it in the appropriate file:
     • Types/macros/globals -> design.h.
     • Functions -> design.c.
   - Adjust the order and location of implemented symbols to fit naturally within the existing design
     and prevent linking issues or dependency problems.
   - If the implementation references additional dependencies that are not yet implemented:
     • Do not implement those dependencies.
     • Leave those references unresolved; do not introduce new helpers, stubs, or refactors.

## PRIORITIES (highest first)

P0 — SCOPE: Implement only symbols listed in "Unresolved Symbols to Implement."

P1 — MINIMIZE DIFFS: Preserve all existing interfaces and qualifiers:
  - Function signatures (parameters, return types)
  - Type definitions
  - Qualifiers (const, static, inline, volatile, restrict)
  - Linkage and visibility attributes
  - DO NOT refactor, rename, reorder, or remove code except as specified in P2 and P3.

P2 — ALLOWED MODIFICATIONS:
  P2.1 — Printing/logging: Directly replace any logging/printing statements or functions
         (e.g., printf/fprintf, log_info including 3rd-party) with NO-OPs or stubs 
         that maintain the same interface.
  P2.2 — External dependencies: If an implementation would require external 
         dependencies or project/hardware-specific code, use a stub or simplified 
         version with EXACTLY the same interface.
  P2.3 — Includes: ONLY standard C library headers are allowed. Project-specific 
         or third-party headers are FORBIDDEN, even if they appear in reference 
         materials or repository code.
  P2.4 — Conditional compilation: Remove all conditional compilation directives 
         (#ifdef, #ifndef, #if, #else, #elif, #endif) and their branches. Retain 
         only the code relevant to a standard C environment or the most common case
         for Ubuntu/Linux with GCC and Intel x86-64 architecture.
  P2.5 — Storage and linkage: If an implementation relies on specific storage 
         classes (e.g., static, extern) or linkage specifications that are not 
         feasible in the extracted context, adjust them to the most appropriate 
         standard C equivalent while preserving functionality.

P3 — INCOMPLETE/AMBIGUOUS REFERENCE HANDLING:
P3.1 — Missing/Incomplete references: If an implementation would require references
       that are missing or incomplete in the reference materials, provide a minimal stub 
       implementation that allows compilation, while preserving the original interface.
P3.2 — Multiple references: If multiple candidate implementations exist, just pick the 
       closest and most contextually relevant one and implement that.

P4 — ERROR HANDLING: If an already-implemented symbol is determined to be 
     erroneous, delete its entire implementation (definition/body only). 
     Do not implement it again; leave it unresolved for future iterations.

P5 — PLACEHOLDERS: placeholder tokens (looks like `_PH_XXXX_`) are used in the program
     to indicate long code segments or data that are not relevant to the current symbols
     being implemented. Keep these tokens exactly as they are. Do not expand or modify them.

## OUTPUT FORMAT (strict)

Return exactly two fenced C code blocks containing the complete files after your changes, in this order, and nothing else:

```c
#ifndef DESIGN_H
#define DESIGN_H
// <complete content of design.h>
#endif // DESIGN_H
```

```c
#include "design.h"
// <complete content of design.c>
```

## INPUT FOR CURRENT ITERATION

Design:

```c
{{__DESIGN_H__}}
```

```c
{{__DESIGN_C__}}
```

Reference:

```c
{{__REFERENCE_CODE_CONTEXT__}}
```

Unresolved Symbols to Implement:

```
{{__SYMBOLS_TO_IMPLEMENT__}}
```

NOTE
- Implement only the specified symbols; leave all others unresolved.
- The design may be incomplete or not compilation‑ready.
- Think step‑by‑step internally, but output only the two code blocks (no explanations or analysis).
