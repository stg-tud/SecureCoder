```cpp
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

std::string generate_receive_log(const std::string &msg) {
    // Get current time
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    std::chrono::system_clock::time_point time_point_now(now_time_t);
    
    // Convert to ISO format
    std::ostringstream oss;
    auto time_tm = std::chrono::system_clock::to_time_t(time_point_now);
    oss << std::put_time(std::gmtime(&time_tm), "%Y-%m-%dT%H:%M:%S");

    // Create log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + msg;
    return log_entry;
}
```