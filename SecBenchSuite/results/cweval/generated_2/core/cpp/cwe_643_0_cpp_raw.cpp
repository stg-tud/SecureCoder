```cpp
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
```