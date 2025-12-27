```cpp
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

std::string generate_receive_log(const std::string &msg) {
    // Get the current time as a time_point
    auto now = std::chrono::system_clock::now();
    
    // Convert to time_t for easy manipulation
    std::time_t now_c = std::chrono::system_clock::to_time_t(now);
    
    // Create a tm struct to format the time
    std::tm now_tm = *std::localtime(&now_c);
    
    // Create a stringstream to format the timestamp
    std::stringstream timestamp_stream;
    timestamp_stream << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");
    
    // Create the log entry
    std::string log_entry = "[" + timestamp_stream.str() + "] Received: " + msg;
    
    return log_entry;
}
```