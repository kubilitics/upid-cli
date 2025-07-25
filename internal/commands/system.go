package commands

import (
	"github.com/spf13/cobra"
)

// SystemCmd creates the system command
func SystemCmd() *cobra.Command {
	systemCmd := &cobra.Command{
		Use:   "system",
		Short: "System management and diagnostics",
		Long: `System management and diagnostics for UPID CLI.

Examples:
  upid system health                    # Check system health
  upid system metrics                   # Get system metrics
  upid system version                   # Get version information
  upid system diagnostics               # Run system diagnostics`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemHealth(cmd, args)
		},
	}

	// Add subcommands
	systemCmd.AddCommand(systemHealthCmd())
	systemCmd.AddCommand(systemMetricsCmd())
	systemCmd.AddCommand(systemVersionCmd())
	systemCmd.AddCommand(systemDiagnosticsCmd())
	systemCmd.AddCommand(systemConfigCmd())
	systemCmd.AddCommand(systemLogsCmd())

	return systemCmd
}

// systemHealthCmd creates the system health command
func systemHealthCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "health",
		Short: "Check system health",
		Long:  "Check the health status of UPID system and components",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemHealth(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("detailed", "d", false, "detailed health information")
	cmd.Flags().BoolP("include-dependencies", "i", false, "include dependency health")

	return cmd
}

// systemMetricsCmd creates the system metrics command
func systemMetricsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "metrics",
		Short: "Get system metrics",
		Long:  "Get system performance metrics and statistics",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemMetrics(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "1h", "time range for metrics")
	cmd.Flags().BoolP("detailed", "d", false, "detailed metrics")
	cmd.Flags().StringP("format", "f", "table", "output format (table, json, yaml)")

	return cmd
}

// systemVersionCmd creates the system version command
func systemVersionCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "version",
		Short: "Get version information",
		Long:  "Get version information for UPID CLI and components",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemVersion(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("detailed", "d", false, "detailed version information")
	cmd.Flags().BoolP("check-updates", "c", false, "check for available updates")

	return cmd
}

// systemDiagnosticsCmd creates the system diagnostics command
func systemDiagnosticsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "diagnostics",
		Short: "Run system diagnostics",
		Long:  "Run comprehensive system diagnostics and troubleshooting",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemDiagnostics(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("verbose", "v", false, "verbose output")
	cmd.Flags().BoolP("fix-issues", "f", false, "attempt to fix detected issues")
	cmd.Flags().StringP("output", "o", "", "output file for diagnostics report")

	return cmd
}

// systemConfigCmd creates the system config command
func systemConfigCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "config",
		Short: "Manage system configuration",
		Long:  "View and manage system configuration settings",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemConfig(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("show-secrets", "s", false, "show sensitive configuration values")
	cmd.Flags().BoolP("validate", "v", false, "validate configuration")
	cmd.Flags().StringP("export", "e", "", "export configuration to file")

	return cmd
}

// systemLogsCmd creates the system logs command
func systemLogsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "logs",
		Short: "View system logs",
		Long:  "View and manage system logs",
		RunE: func(cmd *cobra.Command, args []string) error {
			return systemLogs(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("level", "l", "info", "log level (debug, info, warn, error)")
	cmd.Flags().StringP("time-range", "t", "1h", "time range for logs")
	cmd.Flags().BoolP("follow", "f", false, "follow log output")
	cmd.Flags().StringP("filter", "", "", "filter logs by text")

	return cmd
}

// Implementation functions
func systemHealth(cmd *cobra.Command, args []string) error {
	// Get flags
	detailed, _ := cmd.Flags().GetBool("detailed")
	includeDependencies, _ := cmd.Flags().GetBool("include-dependencies")

	// Build arguments
	cmdArgs := []string{"system", "health"}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if includeDependencies {
		cmdArgs = append(cmdArgs, "--include-dependencies")
	}

	return executePythonCommand("system", cmdArgs)
}

func systemMetrics(cmd *cobra.Command, args []string) error {
	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")
	format, _ := cmd.Flags().GetString("format")

	// Build arguments
	cmdArgs := []string{"system", "metrics"}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if format != "" {
		cmdArgs = append(cmdArgs, "--format", format)
	}

	return executePythonCommand("system", cmdArgs)
}

func systemVersion(cmd *cobra.Command, args []string) error {
	// Get flags
	detailed, _ := cmd.Flags().GetBool("detailed")
	checkUpdates, _ := cmd.Flags().GetBool("check-updates")

	// Build arguments
	cmdArgs := []string{"system", "version"}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if checkUpdates {
		cmdArgs = append(cmdArgs, "--check-updates")
	}

	return executePythonCommand("system", cmdArgs)
}

func systemDiagnostics(cmd *cobra.Command, args []string) error {
	// Get flags
	verbose, _ := cmd.Flags().GetBool("verbose")
	fixIssues, _ := cmd.Flags().GetBool("fix-issues")
	output, _ := cmd.Flags().GetString("output")

	// Build arguments
	cmdArgs := []string{"system", "diagnostics"}
	if verbose {
		cmdArgs = append(cmdArgs, "--verbose")
	}
	if fixIssues {
		cmdArgs = append(cmdArgs, "--fix-issues")
	}
	if output != "" {
		cmdArgs = append(cmdArgs, "--output", output)
	}

	return executePythonCommand("system", cmdArgs)
}

func systemConfig(cmd *cobra.Command, args []string) error {
	// Get flags
	showSecrets, _ := cmd.Flags().GetBool("show-secrets")
	validate, _ := cmd.Flags().GetBool("validate")
	export, _ := cmd.Flags().GetString("export")

	// Build arguments
	cmdArgs := []string{"system", "config"}
	if showSecrets {
		cmdArgs = append(cmdArgs, "--show-secrets")
	}
	if validate {
		cmdArgs = append(cmdArgs, "--validate")
	}
	if export != "" {
		cmdArgs = append(cmdArgs, "--export", export)
	}

	return executePythonCommand("system", cmdArgs)
}

func systemLogs(cmd *cobra.Command, args []string) error {
	// Get flags
	level, _ := cmd.Flags().GetString("level")
	timeRange, _ := cmd.Flags().GetString("time-range")
	follow, _ := cmd.Flags().GetBool("follow")
	filter, _ := cmd.Flags().GetString("filter")

	// Build arguments
	cmdArgs := []string{"system", "logs"}
	if level != "" {
		cmdArgs = append(cmdArgs, "--level", level)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if follow {
		cmdArgs = append(cmdArgs, "--follow")
	}
	if filter != "" {
		cmdArgs = append(cmdArgs, "--filter", filter)
	}

	return executePythonCommand("system", cmdArgs)
}

 