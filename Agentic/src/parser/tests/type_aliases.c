// typedef_alias_test.c
// A compact stress test for typedef alias detection.

#include <stddef.h>

// Simple aliases
typedef int my_int;
typedef const my_int my_const_int;

// Pointer forms
typedef char *char_ptr;
typedef const char *const_char_ptr;
typedef char *restrict restrict_char_ptr;
typedef char_ptr ptr_to_char_ptr;

// Array forms
typedef int int_array[10];
typedef int_array array_of_arrays[5];
typedef int (*func_ptr_array[3])(double);

// Function pointer forms
typedef void (*void_fn)(void);
typedef int (*binary_op)(int, int);
typedef void_fn (*fn_returning_fn)(int);

// Struct/Union/Enum aliases
typedef struct point {
    double x, y;
} point_t;

typedef struct {
    int width, height;
} rect_t;

typedef union {
    int i;
    float f;
} number_t;

typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE
} color_t;

// Escoped typedef inside struct (GNU extension in C2x/clangs)
/*
typedef struct nested {
    typedef struct {
        int inner;
    } inner_t;  
    inner_t value;
} nested_t;
 */

// Anonymous aggregate typedefs
typedef struct {
    unsigned id;
    point_t location;
} anonymous_struct_t;

typedef union {
    unsigned char bytes[4];
    float fvalue;
} anonymous_union_t;

// Typedef to array/function pointer with qualifiers
typedef volatile int volatile_int;
typedef volatile_int *volatile volatile_int_ptr;

// Typedefs involving const/volatile and arrays
typedef const volatile unsigned long cv_ulong;
typedef cv_ulong cv_ulong_array[8];

// Typedef to bit-field type (indirect use)
typedef unsigned short ushort_t;
struct flag_holder {
    ushort_t flags : 9;
};

// Typedef inside function (block scope)
void make_typedef_local(void) {
    typedef unsigned long local_ulong;
    local_ulong value = 0;
    (void)value;
}

// Typedef referencing forward declaration
typedef struct node node_t;
struct node {
    node_t *next;
    int data;
};

typedef int __attribute__((aligned(16))) aligned_int_t;

// Typedef reused in declaration list
typedef unsigned index_t, count_t;

// Self-referential function pointer typedef
typedef int (*recursive_fn)(int, recursive_fn);
