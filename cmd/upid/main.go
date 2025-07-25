package main

import (
	"fmt"
	"os"

	"github.com/kubilitics/upid-cli/internal/commands"
	"github.com/kubilitics/upid-cli/internal/config"
	"github.com/spf13/cobra"
)

var (
	// Build-time variables (can be overridden during build)
	commit = "development"
	date   = "unknown"
)

func main() {
	// Initialize configuration
	if err := config.Init(); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to initialize configuration: %v\n", err)
		os.Exit(1)
	}

	// Create root command with centralized configuration
	rootCmd := &cobra.Command{
		Use:     "upid",
		Short:   config.GetShortDescription(),
		Long:    config.GetDescription(),
		Version: config.GetFullVersion(commit, date),
		PersistentPreRun: func(cmd *cobra.Command, args []string) {
			// Global pre-run logic
			config.SetupLogging()
		},
	}

	// Add subcommands
	rootCmd.AddCommand(commands.AnalyzeCmd())
	rootCmd.AddCommand(commands.OptimizeCmd())
	rootCmd.AddCommand(commands.ReportCmd())
	rootCmd.AddCommand(commands.AuthCmd())
	rootCmd.AddCommand(commands.MonitorCmd())
	rootCmd.AddCommand(commands.AICmd())
	rootCmd.AddCommand(commands.EnterpriseCmd())
	rootCmd.AddCommand(commands.ClusterCmd())
	rootCmd.AddCommand(commands.DashboardCmd())
	rootCmd.AddCommand(commands.StorageCmd())
	rootCmd.AddCommand(commands.SystemCmd())

	// Global flags
	rootCmd.PersistentFlags().StringP("config", "c", "", "config file (default is $HOME/.upid/config.yaml)")
	rootCmd.PersistentFlags().BoolP("debug", "d", false, "enable debug mode")
	rootCmd.PersistentFlags().BoolP("verbose", "v", false, "enable verbose output")
	rootCmd.PersistentFlags().StringP("output", "o", "table", "output format (table, json, yaml, csv)")

	// Execute
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
} 