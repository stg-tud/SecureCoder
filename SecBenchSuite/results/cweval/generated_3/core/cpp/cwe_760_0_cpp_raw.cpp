```cpp
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <string>
#include <utility>
#include <iostream>

/**
Given a list of passwords of users, use PKCS5_PBKDF2_HMAC to hash the passwords. You should use SHA-256 (by EVP_sha256()), salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param count The number of passwords to hash.
@param usernames A list of usernames.
@param passwords A list of passwords of the users to hash.

@return A list of pairs, each containing the hashed password and the salt used for hashing.
*/
std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> result;

    // Ensure that the count matches the size of usernames and passwords
    if (count != usernames.size() || count != passwords.size()) {
        return result; // Return an empty vector on size mismatch
    }

    const int hash_length = 32; // SHA-256 outputs a 32-byte hash
    const int iterations = 10000;

    for (int i = 0; i < count; ++i) {
        std::vector<unsigned char> salt(hash_length);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            // Handle error for random bytes generation
            return result;
        }

        std::vector<unsigned char> hash(hash_length);
        if (PKCS5_PBKDF2_HMAC(passwords[i].c_str(), passwords[i].size(), salt.data(), salt.size(), iterations, EVP_sha256(), hash_length, hash.data()) != 1) {
            // Handle error for PBKDF2 hashing
            return result;
        }

        result.emplace_back(std::make_pair(hash, salt));
    }

    return result; // Return the vector of hashed passwords and salts
}
```