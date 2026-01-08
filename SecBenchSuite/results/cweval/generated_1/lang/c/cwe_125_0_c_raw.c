```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    // Convert index_str to an integer
    char *endptr;
    long index = strtol(index_str, &endptr, 10);
    
    // Check for conversion errors or out of bounds
    if (*endptr != '\0' || index < 0 || index >= size) {
        return -1; // Gracefully return -1 for invalid index
    }

    // Return the price at the specified index
    return prices[(int)index];
}
```