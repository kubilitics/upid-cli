package commands

import (
	"fmt"
	"github.com/kubilitics/upid-cli/internal/bridge"
	"github.com/kubilitics/upid-cli/internal/config"
)

// executePythonCommand executes a Python command through the bridge
func executePythonCommand(command string, args []string) error {
	// Create Python bridge
	pythonPath := config.GetPythonPath()
	scriptPath := config.GetScriptPath()
	debug := config.IsDebug()

	bridge := bridge.NewPythonBridge(pythonPath, scriptPath, debug)

	// Execute command
	output, err := bridge.ExecuteCommandWithTable(command, args)
	if err != nil {
		return fmt.Errorf("failed to execute %s command: %v", command, err)
	}

	// Print output
	fmt.Print(output)
	return nil
} 