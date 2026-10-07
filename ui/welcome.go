package ui

import (
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type welcomeModel struct {
	width  int
	height int
}

func newWelcomeModel() welcomeModel {
	return welcomeModel{}
}

func (m welcomeModel) Init() tea.Cmd {
	return nil
}

func (m welcomeModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height

	case tea.KeyMsg:
		if msg.String() == "q" {
			return m, tea.Quit
		}
	}

	return m, nil
}

func (m welcomeModel) View() string {
	content := lipgloss.JoinVertical(
		lipgloss.Center,
		titleStyle.Render("path"),
		textStyle.Render("Courses in your terminal."),
		"",
		"",
		hintStyle.Render("q quit"),
	)

	return lipgloss.Place(m.width, m.height, lipgloss.Center, lipgloss.Center, content)
}
