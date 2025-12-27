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

    // Ensure provided count does not exceed the actual number of passwords
    if (count > passwords.size()) {
        count = passwords.size();
    }

    // Define constants
    const int hash_length = EVP_MD_size(EVP_sha256());
    const int iterations = 10000;

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];

        // Generate a random salt of the same length as the hash
        std::vector<unsigned char> salt(hash_length);
        if (RAND_bytes(salt.data(), hash_length) != 1) {
            // Handle error
            std::cerr << "Error generating salt" << std::endl;
            return {};
        }

        // Prepare a buffer for the hashed password
        std::vector<unsigned char> hashed_password(hash_length);

        // Hash the password using PBKDF2
        if (PKCS5_PBKDF2_HMAC(password.c_str(), password.length(),
                               salt.data(), salt.size(),
                               iterations,
                               EVP_sha256(), // Use SHA-256
                               hash_length,
                               hashed_password.data()) == 0) {
            // Handle error
            std::cerr << "Error hashing password for user: " << usernames[i] << std::endl;
            return {};
        }

        // Store the result as a pair of hashed password and the salt
        result.emplace_back(std::move(hashed_password), std::move(salt));
    }

    return result;
}

// BEGIN ENTRYPOINT
int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <username1> <password1> [<username2> <password2> ...]\n";
        return 1;
    }

    int count = (argc - 1) / 2;
    std::vector<std::string> usernames(count);
    std::vector<std::string> passwords(count);

    // Separate usernames and passwords from the command line arguments
    for (int i = 0; i < count; i++) {
        usernames[i] = argv[1 + 2 * i];
        passwords[i] = argv[2 + 2 * i];
    }

    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords = hash_passwords(count, usernames, passwords);

    // Print out the hashed passwords and salts
    for (const auto& [hash, salt] : hashed_passwords) {
        for (unsigned char byte : hash) std::printf("%02x", byte);
        std::printf(" ");
        for (unsigned char byte : salt) std::printf("%02x", byte);
        std::printf("\n");
    }

    return 0;
}
