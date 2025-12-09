
You are extracting a self-contained implementation from a GitHub repository. 
Your task is to iteratively implement unresolved symbols based on provided reference code, 
while adhering to constraints to ensure minimal changes and preserve core logic.
A symbol could be a function, a struct/enum/union type, a typedef, a macro, or a global variable.

## Process and Workflow

- Iterative flow:
  1) For each iteration, you will be given:
     - The current design.
     - A list titled “Unresolved Symbols to Implement.”
  2) Implement only the symbols listed in “Unresolved Symbols to Implement,” using the identified reference code where applicable.
  3) Merge the implementations back into the current design and return the updated, incremental design.
  4) If, within an implemented symbol, additional dependencies are referenced that are not yet implemented:
     - Do not implement those dependencies.
     - Leave them unresolved in the design to be handled in later iterations.
  5) These dependencies will be surfaced as they are identified and be implemented in next iterations.
  6) Repeat the process until all symbols are implemented.

## Constraints and Requirements

- Only implement symbols explicitly listed in “Unresolved Symbols to Implement.”
- Do not implement or modify any other symbols.
- Do not refactor, rename, reorder, or remove code outside the minimal edits necessary to implement the listed symbols.
- Minimize diffs: Make the smallest possible edits. Keep the original code, except where implementing a listed symbol or removing/stubbing a dependency is strictly required.
- Dependency-free in standard C: Ensure the implementation does not rely on any non-standard libraries or hardware/platform-specific features or extensions.

### Placeholder

In the design or the reference code provided, you may encounter placeholders formatted as `_PH_XXXX_`. These placeholders are used to represent lengthy code segments that do not require modification, such as array initializations. Continue to use the placeholders as they appear.

### Error in Already Implemented Symbols

If you find that a already implemented symbol is having some errors, You can delete the entire symbol implementation and leave it for re-implementation in the following iterations.

## Output Format

Provide the content of two files, `design.h` and `design.c`.
The output format is as follows:

```c
<complete content of design.h>
```

```c
<complete content of design.c>
```

## Input for Current Iteration

### Design:

```c
{{__DESIGN_H__}}
```

```c
{{__DESIGN_C__}}
```

## Reference:

```c
{{__REFERENCE_CODE_CONTEXT__}}
```

## Unresolved Symbols to Implement:

```
{{__SYMBOLS_TO_IMPLEMENT__}}
```

**NOTE:**
ONLY implement the symbols that are specified above and leave all other symbols unresolved. DO NOT provide any codes beyond the specified symbols. The design is not necessarily complete or compilation-ready.