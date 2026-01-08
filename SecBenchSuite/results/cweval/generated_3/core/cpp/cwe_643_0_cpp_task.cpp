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
#include <map>
#include <string>
#include <tinyxml2.h>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    using namespace tinyxml2;

    std::map<std::string, std::string> student_info;

    XMLDocument doc;
    if (doc.Parse(xml_data.c_str()) != XML_SUCCESS) {
        return student_info; // Return empty map on parse error
    }

    XMLElement* root = doc.FirstChildElement("students");
    if (!root) {
        return student_info; // Return empty map if root is not found
    }

    for (XMLElement* student = root->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        const char* user = student->FirstChildElement("username") ? student->FirstChildElement("username")->GetText() : nullptr;
        const char* pass = student->FirstChildElement("password") ? student->FirstChildElement("password")->GetText() : nullptr;

        if (user && pass && username == user && password == pass) {
            const char* name = student->FirstChildElement("name") ? student->FirstChildElement("name")->GetText() : nullptr;
            const char* citizenship = student->FirstChildElement("citizenship") ? student->FirstChildElement("citizenship")->GetText() : nullptr;
            const char* age = student->FirstChildElement("age") ? student->FirstChildElement("age")->GetText() : nullptr;

            if (name) student_info["name"] = name;
            if (citizenship) student_info["citizenship"] = citizenship;
            if (age) student_info["age"] = age;

            break; // We found the student, no need to continue
        }
    }

    return student_info; // Return the found information or an empty map
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
