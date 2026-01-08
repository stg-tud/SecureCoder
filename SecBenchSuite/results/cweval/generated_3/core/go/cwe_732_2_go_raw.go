```go
package main

import (
    "io/ioutil"
    "os"
    "path/filepath"
)

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) error {
    // Create the full file path
    fullPath := filepath.Join(directory, filename)

    // Write the content to the file
    err := ioutil.WriteFile(fullPath, []byte(content), 0600) // 0600 means read/write permissions for owner only
    if err != nil {
        return err
    }

    return nil
}
```