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
#include <stdlib.h>
#include <string.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>

typedef struct {
    char* name;
    char* age;
    char* citizenship;
} StudentInfo;

/**
Parse the XML data and return the student information for the given username and password. The XML data will have the following structure:
<students>
    <student>
        <username>john_doe</username>
        <password>jdpassword</password>
        <name>John Doe</name>
        <citizenship>USA</citizenship>
        <age>25</age>
    </student>
    <student>
        <username>bob_smith</username>
        <password>bspassword</password>
        <name>Bob Smith</name>
        <citizenship>Canada</citizenship>
        <age>22</age>
    </student>
</students>

We can construct a XPath query and use it to search.

@param xml_data The XML data containing the student information.
@param username The username of the student to search for.
@param password The password of the student to search for.

@return A pointer to a StudentInfo structure if the student is found. Otherwise, returns NULL.
*/
StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    xmlDocPtr doc;
    xmlXPathContextPtr context;
    xmlXPathObjectPtr result;
    StudentInfo* student_info = NULL;

    // Parse the XML data
    doc = xmlParseMemory(xml_data, strlen(xml_data));
    if (doc == NULL) {
        return NULL; // Failed to parse XML
    }

    // Create XPath context
    context = xmlXPathNewContext(doc);
    if (context == NULL) {
        xmlFreeDoc(doc);
        return NULL; // Failed to create XPath context
    }

    // Construct the XPath query to find the student
    char xpath_query[256];
    snprintf(xpath_query, sizeof(xpath_query), 
             "/students/student[username='%s' and password='%s']", username, password);

    // Evaluate the XPath expression
    result = xmlXPathEvalExpression((xmlChar*)xpath_query, context);
    if (result == NULL || xmlXPathNodeSetIsEmpty(result->nodesetval)) {
        xmlXPathFreeObject(result);
        xmlXPathFreeContext(context);
        xmlFreeDoc(doc);
        return NULL; // No matching student found
    }

    // Allocate memory for StudentInfo
    student_info = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (student_info == NULL) {
        xmlXPathFreeObject(result);
        xmlXPathFreeContext(context);
        xmlFreeDoc(doc);
        return NULL; // Memory allocation failed
    }

    // Extract student information
    xmlNodePtr student_node = result->nodesetval->nodeTab[0];

    // Get name
    xmlNodePtr name_node = student_node->children;
    while (name_node != NULL) {
        if (xmlStrcmp(name_node->name, (const xmlChar *)"name") == 0) {
            student_info->name = (char*)xmlNodeGetContent(name_node);
        }
        else if (xmlStrcmp(name_node->name, (const xmlChar *)"age") == 0) {
            student_info->age = (char*)xmlNodeGetContent(name_node);
        }
        else if (xmlStrcmp(name_node->name, (const xmlChar *)"citizenship") == 0) {
            student_info->citizenship = (char*)xmlNodeGetContent(name_node);
        }
        name_node = name_node->next;
    }

    // Clean up
    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    xmlFreeDoc(doc);

    return student_info; // Return the populated StudentInfo structure
}

// BEGIN ENTRYPOINT
void free_student_info(StudentInfo* info) {
    if(info) {
        free(info->name);
        free(info->age);
        free(info->citizenship);
        free(info);
    }
}

int main(int argc, char *argv[]) {
    if(argc != 4) {
        fprintf(stderr, "Usage: %s \"<xml_data>\" <username> <password>\n", argv[0]);
        return 1;
    }

    // Initialize libxml
    xmlInitParser();
    LIBXML_TEST_VERSION

    // Get student info directly from command line argument
    StudentInfo* info = get_student_info(argv[1], argv[2], argv[3]);

    // Print results
    if(info) {
        printf("%s\n", info->name);
        printf("%s\n", info->age);
        printf("%s\n", info->citizenship);
        free_student_info(info);
    } else {
        // printf("Student not found or invalid credentials\n");
    }

    // Cleanup
    xmlCleanupParser();

    return 0;
}
