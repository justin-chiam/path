package data

import (
	_ "embed"
	"encoding/json"
)

//go:embed courses.json
var coursesJSON []byte

type Course struct {
	Code  string   `json:"code"`
	Title string   `json:"title"`
	UOC   int      `json:"uoc"`
	Terms []string `json:"terms"`
}

func LoadCourses() (map[string]Course, error) {
	var list []Course
	if err := json.Unmarshal(coursesJSON, &list); err != nil {
		return nil, err
	}
	courses := make(map[string]Course, len(list))
	for _, c := range list {
		courses[c.Code] = c
	}
	return courses, nil
}