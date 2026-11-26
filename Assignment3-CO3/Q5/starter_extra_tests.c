/* Reuse the completed functions while keeping the exact supplied main untouched. */
#define main supplied_main
#include "complete_the_code.c"
#undef main
int main(void) {
    printf("Tab-separated words: %d\n",word_count("Meet\tat\tthe\tlibrary"));
    printf("Empty words: %d; punctuation words: %d\n",word_count(""),word_count("Hi, world!"));
    printf("Empty palindrome: %d; punctuation-only palindrome: %d\n",is_palindrome(""),is_palindrome("!!!"));
    return 0;
}
