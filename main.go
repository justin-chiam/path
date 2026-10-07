package main

import (
	"os"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/log"
	"github.com/justin-chiam/path/ui"
)

func main() {
	// // configure logging to file
	f, err := os.OpenFile("trip.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		panic(err)
	}
	log.SetOutput(f)
	log.SetLevel(log.DebugLevel)
	log.SetReportCaller(true)

	p := tea.NewProgram(ui.InitialiseRootModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		log.Fatal("TUI error:", err)
	}
}
