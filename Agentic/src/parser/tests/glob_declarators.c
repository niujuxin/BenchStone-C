
int global_flag;
volatile unsigned status_register;
extern int extern_only;
binary_op operation_table[2];
extern float external_float_array[5];

int global_counter = 0;
static int static_internal_state = 1;
const double PI = 3.141592653589793;
extern int extern_initialized = 42;
static int array_of_ints[] = { 1, 2, 3 };
const char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
_Bool flags[4] = { 0, 1, 0, 1 };
signed char tiny_numbers[3] = { -128, 0, 127 };
ulong_t huge_number = 18446744073709551615UL;
static Node static_node_instance = { .value = 99, .next = NULL };

int global_array[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
static const char *string_table[] = {
    "alpha",
    "beta",
    "gamma",
    "delta"
};

int multi_dimensional[2][3][4] = {
    {
        {  1,  2,  3,  4 },
        {  5,  6,  7,  8 },
        {  9, 10, 11, 12 }
    },
    {
        { 13, 14, 15, 16 },
        { 17, 18, 19, 20 },
        { 21, 22, 23, 24 }
    }
};

struct Point polygon_vertices[3] = {
    {0.0, 0.0},
    {1.0, 0.0},
    {0.0, 1.0}
};

union Data mixed_data = { .f = 3.14f };


int add(int a, int b);
int subtract(int a, int b);
char *sc_adb_parse_device_ip_from_line(char *line);

static void init_operations(void);
static void print_status(void);
void process_node_chain(Node *head);

int *pointer_to_int = &global_counter;
int **pointer_to_pointer = &pointer_to_int;
int (*function_pointer)(int, int) = add;
int (*array_of_function_pointers[3])(int, int) = { add, subtract, add };

struct {
    int id;
    union {
        double real;
        struct Point point;
    } payload;
} anonymous_struct = {
    .id = 1,
    .payload.point = { 2.0, 3.0 }
};

volatile struct Node *volatile volatile_node_ptr = NULL;

static struct {
    enum Color color;
    int intensity;
} color_table;
