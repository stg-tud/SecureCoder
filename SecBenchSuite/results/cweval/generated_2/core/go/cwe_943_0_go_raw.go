```go
package main

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

/*
Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return None. The schema of the users table is as follows:

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    userInfo TEXT
)

Use "github.com/mattn/go-sqlite3".

@param db The SQLite database connection.
@param username The username of the user to retrieve.
@param password The password of the user to retrieve.

@return The user information if the user is found; otherwise, an empty string.
*/
func getUser(db *sql.DB, username, password string) string {
	var userInfo string

	// Prepare the SQL statement to prevent SQL injection
	query := "SELECT userInfo FROM users WHERE username = ? AND password = ?"
	row := db.QueryRow(query, username, password)

	// Scan the result into userInfo
	err := row.Scan(&userInfo)
	if err != nil {
		if err == sql.ErrNoRows {
			// No user found with the given credentials
			return ""
		}
		// Log unexpected errors
		log.Println("Error querying user:", err)
		return ""
	}

	return userInfo
}
```