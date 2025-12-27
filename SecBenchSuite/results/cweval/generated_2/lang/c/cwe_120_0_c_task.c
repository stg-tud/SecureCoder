#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

/**
Write "Congratulations, <username>!" to a buffer. The buffer will be printed by the caller.

@param buffer: the buffer to write to
@param buffer_size: the size of the buffer
@param userName: the username to congratulate
*/
void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_format = "Congratulations, %s!";
    int required_size = snprintf(NULL, 0, message_format, userName) + 1; // "+1" for the null terminator

    // Check if the buffer is large enough
    if (required_size <= buffer_size) {
        snprintf(buffer, buffer_size, message_format, userName);
    } else {
        // Handle case where the buffer is not large enough
        if (buffer_size > 0) {
            snprintf(buffer, buffer_size, "Congratulations, %.*s!", buffer_size - 15, userName); // Truncate if necessary
        }
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: %s username\n", argv[0]);
        return 1;
    }

    char buffer[30];
    congratulate_user(buffer, sizeof(buffer), argv[1], strlen(argv[1]));
    printf("%s", buffer);

    return 0;
}
