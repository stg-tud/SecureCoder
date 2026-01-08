#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <iostream>
#include <string>
#include <map>
#include <tinyxml2.h>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;
    tinyxml2::XMLDocument doc;
    
    // Parse the XML data
    if (doc.Parse(xml_data.c_str()) != tinyxml2::XML_SUCCESS) {
        return student_info; // Return empty map on parse error
    }
    
    // Find the root element
    tinyxml2::XMLElement* root = doc.FirstChildElement("students");
    if (!root) {
        return student_info; // Return empty map if root element is not found
    }

    // Iterate over the student elements
    for (tinyxml2::XMLElement* student = root->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        const char* db_username = student->FirstChildElement("username")->GetText();
        const char* db_password = student->FirstChildElement("password")->GetText();
        
        // Check if the username and password match
        if (db_username && db_password && username == db_username && password == db_password) {
            // Extract student information
            const char* name = student->FirstChildElement("name")->GetText();
            const char* citizenship = student->FirstChildElement("citizenship")->GetText();
            const char* age = student->FirstChildElement("age")->GetText();
            
            if (name) student_info["name"] = name;
            if (citizenship) student_info["citizenship"] = citizenship;
            if (age) student_info["age"] = age;
            break; // Found the student, exit the loop
        }
    }
    
    return student_info; // Return the found student information or empty map
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if(argc != 4) {
        std::cerr << "Usage: " << argv[0] << " \"<xml_data>\" <username> <password>\n";
        return 1;
    }

    // Initialize libxml
    xmlInitParser();
    LIBXML_TEST_VERSION

    // Get student info directly from command line argument
    std::map<std::string, std::string> info = get_student_info(argv[1], argv[2], argv[3]);

    // Print results
    if(!info.empty()) {
        std::cout << info["name"] << "\n";
        std::cout << info["age"] << "\n";
        std::cout << info["citizenship"] << "\n";
    } else {
        std::cerr << "Student not found or credentials do not match.\n";
    }

    // Cleanup
    xmlCleanupParser();

    return 0;
}
