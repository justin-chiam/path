package ui

// viewID identifies a top-level view managed by RootModel.
//
// To add a view:
//  1. Add an ID below.
//  2. Create the view's model in its own file (see welcome.go).
//  3. Register it in InitialiseRootModel.
//  4. Switch to it from another view by returning a switchViewMsg.
type viewID int

const (
	welcomeView viewID = iota
)

// switchViewMsg asks RootModel to make another view active.
type switchViewMsg struct {
	to viewID
}
