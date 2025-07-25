package commands

import (
	"github.com/spf13/cobra"
)

// ReportCmd creates the report command
func ReportCmd() *cobra.Command {
	reportCmd := &cobra.Command{
		Use:   "report",
		Short: "Generate reports and insights",
		Long:  "Generate comprehensive reports and insights for Kubernetes clusters",
		RunE: func(cmd *cobra.Command, args []string) error {
			return reportGenerate(cmd, args)
		},
	}

	// Add subcommands
	reportCmd.AddCommand(reportGenerateCmd())
	reportCmd.AddCommand(reportExportCmd())
	reportCmd.AddCommand(reportScheduleCmd())

	return reportCmd
}

// reportGenerateCmd creates the report generation command
func reportGenerateCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "generate [report-type]",
		Short: "Generate a report",
		Long:  "Generate various types of reports",
		RunE: func(cmd *cobra.Command, args []string) error {
			return reportGenerate(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("cluster", "c", "", "cluster name")
	cmd.Flags().StringP("time-range", "t", "30d", "time range")
	cmd.Flags().StringP("format", "f", "pdf", "output format")

	return cmd
}

// reportExportCmd creates the report export command
func reportExportCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "export [report-id]",
		Short: "Export a report",
		Long:  "Export a generated report",
		RunE: func(cmd *cobra.Command, args []string) error {
			return reportExport(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("format", "f", "pdf", "export format")
	cmd.Flags().StringP("output", "o", "", "output file")

	return cmd
}

// reportScheduleCmd creates the report scheduling command
func reportScheduleCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "schedule [cron-expression]",
		Short: "Schedule report generation",
		Long:  "Schedule automated report generation",
		RunE: func(cmd *cobra.Command, args []string) error {
			return reportSchedule(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("report-type", "r", "", "report type")
	cmd.Flags().StringP("cluster", "c", "", "cluster name")

	return cmd
}

// Implementation functions
func reportGenerate(cmd *cobra.Command, args []string) error {
	reportType := "summary"
	if len(args) > 0 {
		reportType = args[0]
	}

	// Get flags
	cluster, _ := cmd.Flags().GetString("cluster")
	timeRange, _ := cmd.Flags().GetString("time-range")
	format, _ := cmd.Flags().GetString("format")

	// Build arguments
	cmdArgs := []string{"generate", reportType}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if format != "" {
		cmdArgs = append(cmdArgs, "--format", format)
	}

	return executePythonCommand("report", cmdArgs)
}

func reportExport(cmd *cobra.Command, args []string) error {
	reportID := args[0]

	// Get flags
	format, _ := cmd.Flags().GetString("format")
	output, _ := cmd.Flags().GetString("output")

	// Build arguments
	cmdArgs := []string{"export", reportID}
	if format != "" {
		cmdArgs = append(cmdArgs, "--format", format)
	}
	if output != "" {
		cmdArgs = append(cmdArgs, "--output", output)
	}

	return executePythonCommand("report", cmdArgs)
}

func reportSchedule(cmd *cobra.Command, args []string) error {
	cronExpr := "0 6 * * 1" // Default: weekly on Monday at 6 AM
	if len(args) > 0 {
		cronExpr = args[0]
	}

	// Get flags
	reportType, _ := cmd.Flags().GetString("report-type")
	cluster, _ := cmd.Flags().GetString("cluster")

	// Build arguments
	cmdArgs := []string{"schedule", cronExpr}
	if reportType != "" {
		cmdArgs = append(cmdArgs, "--report-type", reportType)
	}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}

	return executePythonCommand("report", cmdArgs)
} 