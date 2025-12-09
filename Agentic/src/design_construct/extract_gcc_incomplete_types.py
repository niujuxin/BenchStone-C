import re

# Patterns to match error description lines and capture variable name
# Each pattern should capture the variable name in a group
_INCOMPLETE_TYPE_PATTERNS = [
    re.compile(r"field [`'‘’](\w+)[`'‘’] has incomplete type"),
    re.compile(r"storage size of [`'‘’](\w+)[`'‘’] isn't known"),
    re.compile(r"variable [`'‘’](\w+)[`'‘’] has initializer but incomplete type"),
    re.compile(r"parameter \d+ \([`'‘’](\w+)[`'‘’]\) has incomplete type"),
]

def extract_incomplete_types(gcc_lines: list[str]) -> list[str]:
    type_names = set()

    for i in range(len(gcc_lines) - 1):  # -1 to avoid index out of range
        line = gcc_lines[i]
        
        # Check if current line matches any error pattern and extract variable name
        var_name = None
        for pattern in _INCOMPLETE_TYPE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                var_name = match.group(1)  # Captured variable name
                break
        
        if var_name:
            # Next line should be the source code line
            next_line = gcc_lines[i + 1]
            
            # Check if it's a source code line (contains '|')
            if '|' in next_line:
                # Split by '|' and take the code part (right side)
                code_part = next_line.split('|', 1)[1]
                
                # Extract type name with precise variable name matching
                # Pattern: (enum|struct|union) typename variablename
                type_pattern = r'(enum|struct|union)\s+(\S+)\s+' + re.escape(var_name) + r'\b'
                
                match = re.search(type_pattern, code_part)
                if match:
                    type_name = match.group(2)  # group(1) is enum/struct/union, group(2) is type name
                    type_names.add(type_name)
    
    return list(type_names)


# Example usage:
if __name__ == "__main__":
    gcc_output = """In file included from design.c:1:
design.h:73:21: error: field 'keycode' has incomplete type
   73 |     enum sc_keycode keycode;
      |                     ^~~~~~~
design.h:74:22: error: field 'scancode' has incomplete type
   74 |     enum sc_scancode scancode;
      |                      ^~~~~~~~
design.c:48:39: error: parameter 1 ('scancode') has incomplete type
   48 | scancode_is_modifier(enum sc_scancode scancode) {
      |                      ~~~~~~~~~~~~~~~~~^~~~~~~~
design.c: In function 'sc_hid_keyboard_generate_input_from_key':
design.c:81:10: error: variable 'scancode' has initializer but incomplete type
   81 |     enum sc_scancode scancode = event->scancode;
      |          ^~~~~~~~~~~
design.c:81:22: error: storage size of 'scancode' isn't known
   81 |     enum sc_scancode scancode = event->scancode;
      |                      ^~~~~~~~"""
    
    lines = gcc_output.splitlines()
    result = extract_incomplete_types(lines)
    print("Incomplete types found:")
    for typename in result:
        print(f"  - {typename}")
