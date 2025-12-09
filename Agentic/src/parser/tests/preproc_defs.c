#define DEBUG
#define PI 3.14159
#define VERSION "1.0.0"
#define EMPTY_STRING ""

#define MAX_SIZE (1024 * 1024)
#define OFFSET (sizeof(int) + sizeof(char))

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define CLAMP(val, min, max) (MIN(MAX((val), (min)), (max)))
#define UNSAFE_SQUARE(x) x * x

#define SWAP(a, b) \
    do { \
        typeof(a) temp = (a); \
        (a) = (b); \
        (b) = temp; \
    } while(0)

#define PRINT_DEBUG(fmt, ...) \
    fprintf(stderr, "[DEBUG] %s:%d: " fmt "\n", \
            __FILE__, __LINE__, ##__VA_ARGS__)

#define LOG(...) printf(__VA_ARGS__)
#define DEBUG(fmt, ...) printf("DEBUG: " fmt, __VA_ARGS__)
#define TRACE(msg, ...) fprintf(stderr, msg "\n", ##__VA_ARGS__)

#define PRINT_ERROR(fmt, ...) \
    fprintf(stderr, "Error: " fmt "\n", ##__VA_ARGS__)

#define STRINGIFY(x) #x
#define TO_STRING(x) STRINGIFY(x)

#define CONCAT(a, b) a##b
#define GLUE(x, y) x##y

#define CREATE_FUNCTION(name) \
    void func_##name(void) { \
        printf("Function: %s\n", #name); \
    }

#if defined(__linux__)
#define PLATFORM "Linux"
#elif defined(_WIN32)
#define PLATFORM "Windows"
#else
#define PLATFORM "Unknown"
#endif

#define OUTER(x) INNER(x)
#define INNER(x) ((x) + 1)
#define TRIPLE(x) OUTER(OUTER(OUTER(x)))

#define EMPTY()
#define DO_NOTHING() ((void)0)
#define NOP()

#define MAX_SAFE(a, b) \
    ({ typeof(a) _a = (a); \
       typeof(b) _b = (b); \
       _a > _b ? _a : _b; })

#define SPACED(  x  )  (  (x)  +  1  )
#define NOSPACE(x)(x+1)
#define   LEADING_SPACE(x)   ((x) * 2)

#define WITH_COMMENT(x) /* inline comment */ ((x) + 1)
#define COMMENTED(a, b) \
    /* This is a comment */ \
    ((a) + (b)) /* trailing comment */

#define BACKSLASH '\\'
#define QUOTE '\''
#define DOUBLE_QUOTE '"'
#define NEWLINE_CHAR '\n'

#define TEMP_MACRO 100
#undef TEMP_MACRO
#define TEMP_MACRO 200

#define IMMEDIATE(x)((x)*2)

#define OPTIONAL_ARGS(required, ...) printf(required, ##__VA_ARGS__)

#   define XTRA_SPACES(x)   ( ( x ) + 1 )