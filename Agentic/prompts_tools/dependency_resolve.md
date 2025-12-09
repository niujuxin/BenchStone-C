You will be provided with a current C design consisting of header and source files,
and code snippets that I want to merge into the design.
Your task is to merge the provided code snippets into the current design,
following the policies and instructions below.

## Merge Polity

P1 - MINIMIZE IMPLEMENTATION DIFFS: ONLY make changes following the rules below. Otherwise, copy them exactly as they are in the previous iteration.

  P1.1 — Replace stubs: If the implementation in design files are stubs (e.g., empty functions,
         functions that return constant values, empty structs, etc.), you MUST replace them with the provided real implementations.
  P1.2 — Printing/logging: Directly replace any logging/printing statements or functions
         (e.g., printf/fprintf, log_info including 3rd-party) with NO-OPs or stubs 
         that maintain the same interface.
  P1.3 — External dependencies: If an implementation would require external 
         dependencies or project/hardware-specific code, provide a simplified standard C 
         version with EXACTLY the same interface.
  P1.4 — Includes: ONLY standard C library headers are allowed. Project-specific 
         or third-party headers are FORBIDDEN, even if they appear in reference 
         materials or repository code.
  P1.5 — Conditional compilation: Remove all conditional compilation directives 
         (#ifdef, #ifndef, #if, #else, #elif, #endif) and their branches. Retain 
         only the code relevant to a standard C environment or the most common case
         for Ubuntu/Linux with GCC and Intel x86-64 architecture.
  P1.6 — Storage and linkage: 
         Remove all storage classes or linkage specifications, such as
         static, extern, register, volatile, inline, etc, as well as project-specific
         macros that modify storage or linkage.

P2 - CORRECT ORDER AND PLACEMENT:
     You must ensure that the merged code is in the correct order and placement
     according to standard C programming practices.
     You can change the order of functions, types, and macros as needed.
     Make sure that dependencies among functions, types, and macros are correctly resolved.

NOTE: For each symbol, special instructions may be provided along with reference code.
Follow that strictly when implementing the symbol.

## Indicate What You Need

When merge one provided code, inside that code,
it may require other something like data structures, help functions, macros, etc.
You MUST NOT provide the implementation arbitrarily.

For such situations, follow these rules:

1. If it is a user-defined (composite) type, ONLY provide forward declaration.
   For example, for a struct, you can declare it as `struct SymbolName;` 
   or `typedef struct SymbolName SymbolName;` without defining its fields.
2. If it is a function, ONLY provide the function prototype (declaration) without the body.
3. If it is a macro or constant, DO NOT provide anything.

After that, indicate the names of those required symbols at the end of your output.

## Output Format

Provide the content of two files, `design.h` and `design.c`, and indicate the required symbols.
Your output need three code blocks:

```c
<code for design.h>
```

```c
<code for design.c>
```

Required symbols (one per line, only the names, DO NOT add any other text):
```
symbol_1
symbol_2
...
```
