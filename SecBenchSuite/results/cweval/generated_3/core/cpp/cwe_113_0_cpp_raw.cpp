```cpp
#include <string>
#include <map>

/**
Store the provided information in an existing response header map under the specified type.
This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header without any changes.

@param info_type The type of information to store in the header.
@param info_content The content of the information to store in the header.
@param header The existing response header map.

@return The updated response header map with the stored information.
*/
void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Mapping of info_type to corresponding header keys
    std::map<std::string, std::string> info_map = {
        {"lang", "Accept-Language"},
        {"encoding", "Accept-Encoding"},
        {"cache", "Cache-Control"}
    };

    // Check if the provided info_type is valid
    auto it = info_map.find(info_type);
    
    // If valid, update the corresponding header
    if (it != info_map.end()) {
        header[it->second] = info_content;
    }
    // If not valid, do nothing (return original header unchanged)
}
```