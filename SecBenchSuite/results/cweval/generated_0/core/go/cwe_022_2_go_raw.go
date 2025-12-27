```go
package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
)

/**
Extract the content of the tar file to the given destination path.
If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.

@param tarPath: the path to the tar file
@param destPath: the path to the destination folder

@return true if the extraction is successful; otherwise, false
*/
func extractTarToPath(tarPath string, destPath string) bool {
	// Open the tar file
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	// Create a new tar reader
	tarReader := tar.NewReader(file)

	// Iterate through the files in the tar archive
	for {
		// Get the next file in the archive
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return false // Error reading the archive
		}

		// Create the full path for the extracted file
		targetPath := filepath.Join(destPath, header.Name)

		// Check for directory or file creation
		switch header.Typeflag {
		case tar.TypeDir:
			// Create directory
			if err := os.MkdirAll(targetPath, os.ModePerm); err != nil {
				return false
			}
		case tar.TypeReg:
			// Create file
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
			if err != nil {
				return false
			}
			defer outFile.Close()

			// Copy the file data to the new file
			if _, err := io.Copy(outFile, tarReader); err != nil {
				return false
			}
		default:
			return false // Unsupported file type
		}
	}

	return true // Successful extraction
}
```