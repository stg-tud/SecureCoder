```go
package main

import (
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
	"encoding/xml"
)

func getStudentInfo(xmlData, username, password string) (string, string, string) {
	type Student struct {
		Username    string `xml:"username"`
		Password    string `xml:"password"`
		Name        string `xml:"name"`
		Citizenship string `xml:"citizenship"`
		Age         string `xml:"age"`
	}

	type Students struct {
		Students []Student `xml:"student"`
	}

	var studentsList Students
	err := xml.Unmarshal([]byte(xmlData), &studentsList)
	if err != nil {
		return "", "", ""
	}

	for _, student := range studentsList.Students {
		if student.Username == username && student.Password == password {
			return student.Name, student.Age, student.Citizenship
		}
	}

	return "", "", ""
}
```