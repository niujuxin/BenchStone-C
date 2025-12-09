
void simple_void_function(void) {
    printf("Simple function\n");
}

float multiply(float x, float y, float z) {
    return x * y * z;
}

void pointer_params(int* ptr, char* str, void* generic) {
    *ptr = 10;
}

const char* const get_string(const char* input) {
    return input;
}

static inline void static_inline_combo(void) {
    return;
}

int apply_operation(int (*op)(int, int), int a, int b) {
    return op(a, b);
}

void process_array(int arr[], size_t len) {
    for (size_t i = 0; i < len; i++) {
        arr[i]++;
    }
}

void matrix_op(int matrix[10][10]) {
    matrix[0][0] = 1;
}

void log_message(const char* format, ...) {
    printf(format);
}

struct Point { int x, y; };

struct Point create_point(int x, int y) {
    struct Point p = {x, y};
    return p;
}

struct Point* allocate_point(void) {
    return malloc(sizeof(struct Point));
}

int complex_function(
    int param1,
    double param2,
    const char* param3,
    void* param4,
    size_t param5
) {
    return param1;
}

unsigned int get_unsigned(unsigned char c, unsigned long l) {
    return c + l;
}

char** get_strings(void) {
    return NULL;
}

/* 16. K&R style (old C) - if your parser supports it */
int old_style(a, b)
    int a;
    int b;
{
    return a + b;
}

int* (*complex_ptr(int x))[10] {
    return NULL;
}

void (*signal_handler(int sig, void (*handler)(int)))(int) {
    return handler;
}

int
    spaced_function
        (
            int     x,
            int     y
        )
{
    return x + y;
}

int /* comment */ commented /* more */ (
    int /* inline comment */ param
) /* trailing comment */ {
    return param;
}

EXPORT int exported_function(void) {
    return 1;
}

INLINE void macro_inline(void) {
    return;
}
