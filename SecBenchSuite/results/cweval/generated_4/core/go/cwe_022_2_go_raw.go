```go
package main

import (
	"archive/tar"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// extractTarToPath extracts the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, if any error occurs during the extraction process
// (e.g. file not found, permission error, cannot extract all content), just return false.
func extractTarToPath(tarPath string, destPath string) bool {
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	tarReader := tar.NewReader(file)

	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			break // end of tar archive
		}
		if err != nil {
			return false
		}

		target := filepath.Join(destPath, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, os.ModePerm); err != nil {
				return false
			}
		case tar.TypeReg:
			targetFile, err := os.OpenFile(target, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
			if err != nil {
				return false
			}
			if _, err := io.Copy(targetFile, tarReader); err != nil {
				targetFile.Close()
				return false
			}
			targetFile.Close()
		default:
			return false
		}
	}

	return true
}
```