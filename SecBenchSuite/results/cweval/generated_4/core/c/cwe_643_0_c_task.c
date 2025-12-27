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

StudentInfo* get_student_info(const char* xml_data, const char* username, const char* password) {
    // Initialize the XML parser
    xmlDocPtr doc = xmlParseMemory(xml_data, strlen(xml_data));
    if (doc == NULL) {
        return NULL; // Failed to parse the XML
    }

    // Create an XPath context
    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
        xmlFreeDoc(doc);
        return NULL; // Failed to create XPath context
    }

    // Construct the XPath query to find the student node
    char xpath_query[256];
    snprintf(xpath_query, sizeof(xpath_query), 
             "/students/student[username='%s' and password='%s']", username, password);

    // Evaluate the XPath expression
    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((xmlChar*)xpath_query, xpathCtx);
    if (xpathObj == NULL || xpathObj->nodesetval->nodeNr == 0) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL; // No matching student found
    }

    // Retrieve the first matching student node
    xmlNodePtr studentNode = xpathObj->nodesetval->nodeTab[0];

    // Create a StudentInfo structure to hold the information
    StudentInfo* studentInfo = (StudentInfo*)malloc(sizeof(StudentInfo));
    if (studentInfo == NULL) {
        xmlXPathFreeObject(xpathObj);
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return NULL; // Memory allocation failed
    }

    // Helper function to get text content of a node
    char* get_text_content(xmlNodePtr node) {
        xmlNodePtr cur = node->children;
        while (cur != NULL) {
            if (cur->type == XML_TEXT_NODE) {
                return (char*)cur->content;
            }
            cur = cur->next;
        }
        return NULL;
    }

    // Populate the StudentInfo structure
    studentInfo->name = strdup(get_text_content(xmlXPathNodeSetItem(xpathObj->nodesetval, 0)->next)); // name node
    studentInfo->citizenship = strdup(get_text_content(xmlXPathNodeSetItem(xpathObj->nodesetval, 0)->next->next)); // citizenship node
    studentInfo->age = strdup(get_text_content(xmlXPathNodeSetItem(xpathObj->nodesetval, 0)->next->next->next)); // age node

    // Clean up
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return studentInfo; // Return the populated StudentInfo structure
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
