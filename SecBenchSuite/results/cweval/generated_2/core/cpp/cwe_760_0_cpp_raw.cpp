```cpp
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <string>
#include <utility>
#include <iostream>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    // Ensure count does not exceed the number of provided passwords
    if (count > passwords.size()) {
        count = passwords.size();
    }

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];
        std::vector<unsigned char> salt(EVP_MD_size(EVP_sha256())); // Salt size same as hash output size
        std::vector<unsigned char> hash(EVP_MD_size(EVP_sha256())); // Hash output buffer

        // Generate random salt
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            // Handle error
            std::cerr << "Error generating random salt." << std::endl;
            continue;
        }

        // Hash the password with the generated salt
        if (PKCS5_PBKDF2_HMAC(password.c_str(), password.length(),
                              salt.data(), salt.size(),
                              10000, // Number of iterations
                              EVP_MD_size(EVP_sha256()), // Length of the derived key
                              hash.data()) == 0) {
            // Handle error
            std::cerr << "Error hashing password." << std::endl;
            continue;
        }

        // Store the hashed password and salt
        hashed_passwords.emplace_back(hash, salt);
    }

    return hashed_passwords;
}
```