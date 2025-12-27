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

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    // Ensure the count does not exceed the size of usernames and passwords
    if (count > usernames.size() || count > passwords.size()) {
        return hashed_passwords; // Return empty vector if count is invalid
    }

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];
        
        // Generate a random salt of length equal to the hash output
        std::vector<unsigned char> salt(EVP_MAX_MD_SIZE);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            ERR_print_errors_fp(stderr);
            return hashed_passwords; // Return empty if salt generation fails
        }

        // Prepare to hash the password
        std::vector<unsigned char> hashed_password(EVP_MD_size(EVP_sha256()));
        if (!PKCS5_PBKDF2_HMAC(password.c_str(), password.length(), salt.data(), salt.size(), 10000, EVP_sha256(), hashed_password.size(), hashed_password.data())) {
            ERR_print_errors_fp(stderr);
            return hashed_passwords; // Return empty if hashing fails
        }

        // Store the hashed password and the corresponding salt
        hashed_passwords.emplace_back(std::make_pair(hashed_password, salt));
    }

    return hashed_passwords;
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
