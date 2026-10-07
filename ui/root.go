package ui

import (
	tea "github.com/charmbracelet/bubbletea"
)

// Top level model
type RootModel struct {
	views  map[viewID]tea.Model
	active viewID
}

func InitialiseRootModel() RootModel {
	return RootModel{
		views: map[viewID]tea.Model{
			welcomeView: newWelcomeModel(),
		},
		active: welcomeView,
	}
}

func (m RootModel) Init() tea.Cmd {
	return m.views[m.active].Init()
}

func (m RootModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "ctrl+c" {
			return m, tea.Quit
		}

	case tea.WindowSizeMsg:
		cmds := make([]tea.Cmd, 0, len(m.views))
		for id, view := range m.views {
			var cmd tea.Cmd
			m.views[id], cmd = view.Update(msg)
			cmds = append(cmds, cmd)
		}
		return m, tea.Batch(cmds...)

	case switchViewMsg:
		m.active = msg.to
		return m, m.views[m.active].Init()
	}

	var cmd tea.Cmd
	m.views[m.active], cmd = m.views[m.active].Update(msg)
	return m, cmd
}

func (m RootModel) View() string {
	return m.views[m.active].View()
}
