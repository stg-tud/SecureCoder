```c
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
```