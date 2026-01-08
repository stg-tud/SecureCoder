```cpp
#include <jwt.h>
#include <string>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt::verify verifier = jwt::verify().allow_algorithm(jwt::algorithm::hs256{key});
    
    try {
        auto decoded_token = jwt::decode(token);
        verifier.verify(decoded_token);
        
        // Extract claims
        json claims = json::object();
        for (const auto& e : decoded_token.get_payload_claims()) {
            claims[e.first] = e.second.to_json();
        }
        
        return claims.dump(); // Return the claims as a JSON string
    } catch (const std::exception& e) {
        // Return an empty JSON object string on error
        return "{}";
    }
}
```