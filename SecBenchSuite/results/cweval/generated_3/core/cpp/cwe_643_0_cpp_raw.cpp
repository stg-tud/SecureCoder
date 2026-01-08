```cpp
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
```