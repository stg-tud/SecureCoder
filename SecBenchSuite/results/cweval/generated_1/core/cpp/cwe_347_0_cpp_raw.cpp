```cpp
#include <jwt.h>
#include <string>
#include <stdexcept>
#include <json/json.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt::decode decoded_token;
    try {
        decoded_token = jwt::decode(token, jwt::params::algorithms({"HS256"}), jwt::params::secret(key));
        Json::Value claims_json;

        for (const auto& claim : decoded_token.get_payload()) {
            claims_json[claim.first] = claim.second;
        }

        Json::StreamWriterBuilder writer;
        return Json::writeString(writer, claims_json);
    } catch (const std::exception& e) {
        return "{}"; // Return an empty JSON object string on failure
    }
}
```