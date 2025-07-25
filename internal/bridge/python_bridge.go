package bridge

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"
)

// PythonBridge handles communication between Go CLI and Python core
type PythonBridge struct {
	pythonPath string
	scriptPath  string
	debug       bool
}

// NewPythonBridge creates a new Python bridge instance
func NewPythonBridge(pythonPath, scriptPath string, debug bool) *PythonBridge {
	return &PythonBridge{
		pythonPath: pythonPath,
		scriptPath:  scriptPath,
		debug:       debug,
	}
}

// ExecuteCommand executes a Python command and returns the result
func (pb *PythonBridge) ExecuteCommand(cmd string, args []string) ([]byte, error) {
	// Use the runtime bootstrap script instead of module
	runtimeScript := "runtime/upid_runtime.py"
	cmdArgs := append([]string{runtimeScript, cmd}, args...)
	
	if pb.debug {
		fmt.Printf("Executing Python runtime: %s %s\n", pb.pythonPath, strings.Join(cmdArgs, " "))
	}

	// Execute Python runtime command
	output, err := exec.Command(pb.pythonPath, cmdArgs...).Output()
	if err != nil {
		return nil, fmt.Errorf("Python command failed: %v", err)
	}

	return output, nil
}

// ExecuteCommandWithJSON executes a Python command and parses JSON response
func (pb *PythonBridge) ExecuteCommandWithJSON(cmd string, args []string) (map[string]interface{}, error) {
	output, err := pb.ExecuteCommand(cmd, args)
	if err != nil {
		return nil, err
	}

	// Parse JSON response
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, fmt.Errorf("Failed to parse JSON response: %v", err)
	}

	return result, nil
}

// ExecuteCommandWithTable executes a Python command and formats as table
func (pb *PythonBridge) ExecuteCommandWithTable(cmd string, args []string) (string, error) {
	output, err := pb.ExecuteCommand(cmd, append(args, "--format", "table"))
	if err != nil {
		return "", err
	}

	return string(output), nil
}

// HealthCheck verifies Python bridge is working
func (pb *PythonBridge) HealthCheck() error {
	_, err := pb.ExecuteCommand("health", []string{"--check"})
	return err
}

// GetVersion gets the Python core version
func (pb *PythonBridge) GetVersion() (string, error) {
	output, err := pb.ExecuteCommand("version", []string{})
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(output)), nil
} 