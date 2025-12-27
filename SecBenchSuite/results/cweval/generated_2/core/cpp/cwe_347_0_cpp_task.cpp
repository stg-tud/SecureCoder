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
    jwt::decode decoded_token(token);
    try {
        // Verify the token using the specified key
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key})
            .with_issuer("your-issuer"); // You can replace "your-issuer" with your actual issuer

        verifier.verify(decoded_token);

        // Extract claims as a JSON object
        json claims = json::object();
        for (const auto& claim : decoded_token.get_payload_claims()) {
            claims[claim.first] = claim.second.to_json(); // Convert claims to JSON format
        }

        // Return the claims as a string
        return claims.dump();
    } catch (const std::exception& e) {
        // On failure, return an empty JSON object string
        return "{}";
    }
}

// BEGIN ENTRYPOINT
#include <cstdlib>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Usage: " << argv[0] << " <jwt_token> <key>" << std::endl;
        return 1;
    }

    std::string token = argv[1];
    std::string key = argv[2];

    std::string result = decode_json_web_token(token, key);
    std::cout << result;

    return 0;
}
