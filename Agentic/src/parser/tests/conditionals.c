
#ifndef A
#define A 1
#endif

#ifndef C
#define C 0
#endif

#define STR "OK"

#ifdef A
int t1_a = 1001;
#else
int t1_a = -1001;
#endif

#ifndef B
int t1_b = 1002;
#else
int t1_b = -1002;
#endif

#if A
int t2_a = 2001;
#else
int t2_a = -2001;
#endif

#if defined(B)
int t2_b = -2002;
#else
int t2_b = 2002; 
#endif

#if defined(B) && B
int t2_b_num = -2003;
#else
int t2_b_num = 2003;
#endif

#if 0
int t3 = -3001;
#elif defined(A) && A == 1
int t3 = 3001; 
#elif 1
int t3 = -3002;
#else
int t3 = -3003;
#endif

#ifdef A
  #ifndef B
    #if C
      int t4 = -4001;
    #else
      int t4 = 4001; 
    #endif
  #else
    int t4 = -4002;
  #endif
#else
  int t4 = -4003;
#endif

#if UNDEF_X + 5 == 5
int t5 = 5001;
#else
int t5 = -5001;
#endif

#if defined(UNDEF_Y) && (1/0)
int t6 = -6001;
#else
int t6 = 6001; 
#endif

#if 0 || (defined(A) && (A + 0))
int t6b = 6002; 
#else
int t6b = -6002;
#endif

#if 1
#define T7S "SEL1"
#else
#define T7S "SEL2"
#endif
const char *t7 = T7S STR;

#define M8 8
#ifndef M8
int t8 = -8001;
#else
int t8 = 8001; 
#endif
#define M8 9

#if (3 + 2 * 4) == 11 && !0 && ~(0) == -1
int t9 = 9001;
#else
int t9 = -9001;
#endif

#if 1 && \
    (defined(A) || defined(B)) && \
    !defined(NOT_DEFINED_EVER)
int t10 = 10001;
#else
int t10 = -10001;
#endif

#if defined(B)
int t11 = -11001;
#elif defined(C) && C
int t11 = -11002;
#elif !defined(B) && !C
int t11 = 11001; 
#else
int t11 = -11003;
#endif

#if 'A' == 65 || 'A' < 'B'
int t12 = 12001; 
#else
int t12 = -12001;
#endif

#if !!A && !(!A) && -(-1) == 1
int t13 = 13001;
#else
int t13 = -13001;
#endif

#if defined A
int t14a = 14001;
#else
int t14a = -14001;
#endif

#if defined (B)
int t14b = -14002;
#else
int t14b = 14002;
#endif

#if 0
int t15 = -15001;
#else
int t15 = 15001; 
#elif 1
int t15 = -15002;
#else
int t15 = -15003;
#endif

/* Test 16: Ensure comments don’t affect conditions */
#if /*comment*/ 1 /* another */ && \
    /* block */ 1
int t16 = 16001; /* expect included */
#else
int t16 = -16001;
#endif

/* Test 17: Macro used in expression before/after redefinition */
#define R 1
#if R == 1
int t17a = 17001; /* expect included */
#else
int t17a = -17001;
#endif
#undef R
#define R 2
#if R == 2
int t17b = 17002; /* expect included */
#else
int t17b = -17002;
#endif

/* Test 18: Ternary-like structure via conditionals producing a single definition */
#if defined(A)
#define PICK 18001
#else
#define PICK -18001
#endif
int t18 = PICK; /* expect 18001 if A defined */

/* Test 19: Guard against recursive defined() misuse in expression */
#if (defined(A) ? 1 : 0)
int t19 = 19001; /* expect included */
#else
int t19 = -19001;
#endif

/* Test 20: Ensure #elif with complex false, then #else */
#if 0 && defined(A)
int t20 = -20001;
#elif 0 || (0 && 1)
int t20 = -20002;
#else
int t20 = 20001; /* expect included */
#endif
