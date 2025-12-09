
struct __attribute__((packed)) Foo {
    int x;
};

struct Point {
    int x;
    int y;
};

enum Color {
    COLOR_NONE = 0,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE
};

struct Rectangle {
    struct Point top_left;
    struct Point bottom_right;
    struct _Style {
        int border_width;
        unsigned filled : 1;
        enum Color fill_color;
    } style;
};

union Number;

union Number {
    int i;
    float f;
    struct {
        unsigned sign : 1;
        unsigned exponent : 8;
        unsigned mantissa : 23;
    } bits;
};


// Should not be extracted:

struct Rectangle create_rectangle(int x1, int y1, int x2, int y2) {
    struct Rectangle rect;
    rect.top_left.x = x1;
    rect.top_left.y = y1;
    rect.bottom_right.x = x2;
    rect.bottom_right.y = y2;
    return rect;
}

struct Rectangle global_rect;
