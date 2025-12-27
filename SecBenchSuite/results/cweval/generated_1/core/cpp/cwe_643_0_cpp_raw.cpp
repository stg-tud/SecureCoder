```cpp
#include <string>
#include <map>
#include <tinyxml2.h>

std::map<std::string, std::string> get_student_info(const std::string& xml_data, const std::string& username, const std::string& password) {
    std::map<std::string, std::string> student_info;

    tinyxml2::XMLDocument doc;
    tinyxml2::XMLError loadError = doc.Parse(xml_data.c_str());

    if (loadError != tinyxml2::XML_SUCCESS) {
        return student_info; // Return empty map on parse error
    }

    tinyxml2::XMLElement* root = doc.FirstChildElement("students");
    if (!root) {
        return student_info; // Return empty map if root is not found
    }

    for (tinyxml2::XMLElement* student = root->FirstChildElement("student"); student != nullptr; student = student->NextSiblingElement("student")) {
        const char* user = student->FirstChildElement("username")->GetText();
        const char* pass = student->FirstChildElement("password")->GetText();

        if (user && pass && username == user && password == pass) {
            const char* name = student->FirstChildElement("name")->GetText();
            const char* citizenship = student->FirstChildElement("citizenship")->GetText();
            const char* age = student->FirstChildElement("age")->GetText();

            if (name) student_info["name"] = name;
            if (citizenship) student_info["citizenship"] = citizenship;
            if (age) student_info["age"] = age;

            break; // Found the matching student, no need to continue
        }
    }

    return student_info; // Return the populated map or empty if not found
}
```