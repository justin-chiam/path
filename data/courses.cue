// Schema for data
package data

import "list"

#Course: {
	code!:  =~"^[A-Z]{4}[0-9]{4}$"
	title!: =~"^\\S(.*\\S)?$"
	uoc!:   int & >=0
	terms!: [...=~"^[A-Z0-9]+$"] & list.UniqueItems()
}

courses: [...#Course]
_count: len(courses) & >=3500

for i, c in courses if i > 0 {
	_sortedAfterPrevious: (c.code): true & courses[i-1].code < c.code
}
