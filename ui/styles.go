package ui

import "github.com/charmbracelet/lipgloss"

var (
	accentColour = lipgloss.AdaptiveColor{Light: "#5A3FD6", Dark: "#B7A6FF"}
	textColour   = lipgloss.AdaptiveColor{Light: "#3A3A3A", Dark: "#DDDDDD"}
	mutedColour  = lipgloss.AdaptiveColor{Light: "#8A8A8A", Dark: "#7A7A7A"}
)

var (
	titleStyle = lipgloss.NewStyle().Bold(true).Foreground(accentColour)
	textStyle  = lipgloss.NewStyle().Foreground(textColour)
	hintStyle  = lipgloss.NewStyle().Foreground(mutedColour)

	borderStyle = lipgloss.NewStyle().BorderStyle(lipgloss.RoundedBorder()).Margin(1, 2)
)
