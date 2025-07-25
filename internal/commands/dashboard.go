package commands

import (
	"fmt"

	"github.com/spf13/cobra"
)

// DashboardCmd creates the dashboard command
func DashboardCmd() *cobra.Command {
	dashboardCmd := &cobra.Command{
		Use:   "dashboard",
		Short: "Interactive dashboard and visualization",
		Long: `Interactive dashboard and visualization for UPID CLI.

Examples:
  upid dashboard start                    # Start interactive dashboard
  upid dashboard metrics                  # View dashboard metrics
  upid dashboard export                   # Export dashboard data`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return dashboardStart(cmd, args)
		},
	}

	// Add subcommands
	dashboardCmd.AddCommand(dashboardStartCmd())
	dashboardCmd.AddCommand(dashboardMetricsCmd())
	dashboardCmd.AddCommand(dashboardExportCmd())
	dashboardCmd.AddCommand(dashboardConfigCmd())

	return dashboardCmd
}

// dashboardStartCmd creates the dashboard start command
func dashboardStartCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "start",
		Short: "Start interactive dashboard",
		Long:  "Start the interactive UPID dashboard in your browser",
		RunE: func(cmd *cobra.Command, args []string) error {
			return dashboardStart(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("port", "p", "8080", "port to run dashboard on")
	cmd.Flags().StringP("host", "h", "localhost", "host to bind dashboard to")
	cmd.Flags().BoolP("open-browser", "o", true, "automatically open browser")
	cmd.Flags().StringP("cluster", "c", "", "default cluster to show")

	return cmd
}

// dashboardMetricsCmd creates the dashboard metrics command
func dashboardMetricsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "metrics",
		Short: "View dashboard metrics",
		Long:  "View dashboard metrics and key performance indicators",
		RunE: func(cmd *cobra.Command, args []string) error {
			return dashboardMetrics(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("cluster", "c", "", "cluster to get metrics for")
	cmd.Flags().StringP("time-range", "t", "24h", "time range for metrics")
	cmd.Flags().StringP("format", "f", "table", "output format (table, json, yaml)")

	return cmd
}

// dashboardExportCmd creates the dashboard export command
func dashboardExportCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "export",
		Short: "Export dashboard data",
		Long:  "Export dashboard data and reports",
		RunE: func(cmd *cobra.Command, args []string) error {
			return dashboardExport(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("cluster", "c", "", "cluster to export data for")
	cmd.Flags().StringP("format", "f", "json", "export format (json, csv, pdf)")
	cmd.Flags().StringP("output", "o", "", "output file path")
	cmd.Flags().StringP("time-range", "t", "30d", "time range for export")

	return cmd
}

// dashboardConfigCmd creates the dashboard config command
func dashboardConfigCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "config",
		Short: "Configure dashboard settings",
		Long:  "Configure dashboard settings and preferences",
		RunE: func(cmd *cobra.Command, args []string) error {
			return dashboardConfig(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("theme", "", "dark", "dashboard theme (light, dark, auto)")
	cmd.Flags().BoolP("auto-refresh", "r", true, "enable auto-refresh")
	cmd.Flags().StringP("refresh-interval", "i", "30s", "refresh interval")
	cmd.Flags().BoolP("show-costs", "c", true, "show cost information")
	cmd.Flags().BoolP("show-alerts", "a", true, "show alerts")

	return cmd
}

// Implementation functions
func dashboardStart(cmd *cobra.Command, args []string) error {
	// Get flags
	port, _ := cmd.Flags().GetString("port")
	host, _ := cmd.Flags().GetString("host")
	openBrowser, _ := cmd.Flags().GetBool("open-browser")
	cluster, _ := cmd.Flags().GetString("cluster")

	// Build arguments
	cmdArgs := []string{"dashboard", "start"}
	if port != "" {
		cmdArgs = append(cmdArgs, "--port", port)
	}
	if host != "" {
		cmdArgs = append(cmdArgs, "--host", host)
	}
	if !openBrowser {
		cmdArgs = append(cmdArgs, "--no-open-browser")
	}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}

	return executePythonCommand("dashboard", cmdArgs)
}

func dashboardMetrics(cmd *cobra.Command, args []string) error {
	// Get flags
	cluster, _ := cmd.Flags().GetString("cluster")
	timeRange, _ := cmd.Flags().GetString("time-range")
	format, _ := cmd.Flags().GetString("format")

	// Build arguments
	cmdArgs := []string{"dashboard", "metrics"}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if format != "" {
		cmdArgs = append(cmdArgs, "--format", format)
	}

	return executePythonCommand("dashboard", cmdArgs)
}

func dashboardExport(cmd *cobra.Command, args []string) error {
	// Get flags
	cluster, _ := cmd.Flags().GetString("cluster")
	format, _ := cmd.Flags().GetString("format")
	output, _ := cmd.Flags().GetString("output")
	timeRange, _ := cmd.Flags().GetString("time-range")

	// Build arguments
	cmdArgs := []string{"dashboard", "export"}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}
	if format != "" {
		cmdArgs = append(cmdArgs, "--format", format)
	}
	if output != "" {
		cmdArgs = append(cmdArgs, "--output", output)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}

	return executePythonCommand("dashboard", cmdArgs)
}

func dashboardConfig(cmd *cobra.Command, args []string) error {
	// Get flags
	theme, _ := cmd.Flags().GetString("theme")
	autoRefresh, _ := cmd.Flags().GetBool("auto-refresh")
	refreshInterval, _ := cmd.Flags().GetString("refresh-interval")
	showCosts, _ := cmd.Flags().GetBool("show-costs")
	showAlerts, _ := cmd.Flags().GetBool("show-alerts")

	// Build arguments
	cmdArgs := []string{"dashboard", "config"}
	if theme != "" {
		cmdArgs = append(cmdArgs, "--theme", theme)
	}
	cmdArgs = append(cmdArgs, "--auto-refresh", fmt.Sprintf("%t", autoRefresh))
	if refreshInterval != "" {
		cmdArgs = append(cmdArgs, "--refresh-interval", refreshInterval)
	}
	cmdArgs = append(cmdArgs, "--show-costs", fmt.Sprintf("%t", showCosts))
	cmdArgs = append(cmdArgs, "--show-alerts", fmt.Sprintf("%t", showAlerts))

	return executePythonCommand("dashboard", cmdArgs)
}

 