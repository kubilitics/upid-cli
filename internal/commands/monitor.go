package commands

import (
	"github.com/spf13/cobra"
)

// MonitorCmd creates the monitor command
func MonitorCmd() *cobra.Command {
	monitorCmd := &cobra.Command{
		Use:   "monitor",
		Short: "Real-time monitoring and alerts",
		Long:  "Monitor Kubernetes clusters in real-time with alerts and notifications",
		RunE: func(cmd *cobra.Command, args []string) error {
			return monitorStart(cmd, args)
		},
	}

	// Add subcommands
	monitorCmd.AddCommand(monitorStartCmd())
	monitorCmd.AddCommand(monitorStopCmd())
	monitorCmd.AddCommand(monitorStatusCmd())
	monitorCmd.AddCommand(monitorAlertsCmd())

	return monitorCmd
}

// monitorStartCmd creates the start monitoring command
func monitorStartCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "start [cluster-name]",
		Short: "Start real-time monitoring",
		Long:  "Start real-time monitoring of a Kubernetes cluster",
		RunE: func(cmd *cobra.Command, args []string) error {
			return monitorStart(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to monitor")
	cmd.Flags().BoolP("daemon", "d", false, "run as daemon")
	cmd.Flags().StringP("interval", "i", "30s", "monitoring interval")

	return cmd
}

// monitorStopCmd creates the stop monitoring command
func monitorStopCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "stop [cluster-name]",
		Short: "Stop real-time monitoring",
		Long:  "Stop real-time monitoring of a Kubernetes cluster",
		RunE: func(cmd *cobra.Command, args []string) error {
			return monitorStop(cmd, args)
		},
	}

	return cmd
}

// monitorStatusCmd creates the status command
func monitorStatusCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "status [cluster-name]",
		Short: "Check monitoring status",
		Long:  "Check the status of real-time monitoring",
		RunE: func(cmd *cobra.Command, args []string) error {
			return monitorStatus(cmd, args)
		},
	}

	return cmd
}

// monitorAlertsCmd creates the alerts command
func monitorAlertsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "alerts [cluster-name]",
		Short: "View monitoring alerts",
		Long:  "View current and historical monitoring alerts",
		RunE: func(cmd *cobra.Command, args []string) error {
			return monitorAlerts(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "24h", "time range for alerts")
	cmd.Flags().StringP("severity", "s", "", "filter by severity")

	return cmd
}

// Implementation functions
func monitorStart(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	namespace, _ := cmd.Flags().GetString("namespace")
	daemon, _ := cmd.Flags().GetBool("daemon")
	interval, _ := cmd.Flags().GetString("interval")

	// Build arguments
	cmdArgs := []string{"start", clusterName}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if daemon {
		cmdArgs = append(cmdArgs, "--daemon")
	}
	if interval != "" {
		cmdArgs = append(cmdArgs, "--interval", interval)
	}

	return executePythonCommand("monitor", cmdArgs)
}

func monitorStop(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	return executePythonCommand("monitor", []string{"stop", clusterName})
}

func monitorStatus(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	return executePythonCommand("monitor", []string{"status", clusterName})
}

func monitorAlerts(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	severity, _ := cmd.Flags().GetString("severity")

	// Build arguments
	cmdArgs := []string{"alerts", clusterName}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if severity != "" {
		cmdArgs = append(cmdArgs, "--severity", severity)
	}

	return executePythonCommand("monitor", cmdArgs)
} 