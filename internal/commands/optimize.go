package commands

import (
	"fmt"

	"github.com/spf13/cobra"
)

// OptimizeCmd creates the optimize command
func OptimizeCmd() *cobra.Command {
	optimizeCmd := &cobra.Command{
		Use:   "optimize",
		Short: "Optimize Kubernetes resources and costs",
		Long: `Optimize Kubernetes resources and costs using ML-powered recommendations.
		
Examples:
  upid optimize resources                    # Get resource optimization recommendations
  upid optimize zero-pod --dry-run         # Simulate zero-pod scaling
  upid optimize cost --time-range 30d      # Optimize costs
  upid optimize apply --recommendation-id 123 # Apply optimization`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeResources(cmd, args)
		},
	}

	// Add subcommands
	optimizeCmd.AddCommand(optimizeResourcesCmd())
	optimizeCmd.AddCommand(optimizeZeroPodCmd())
	optimizeCmd.AddCommand(optimizeCostCmd())
	optimizeCmd.AddCommand(optimizeApplyCmd())
	optimizeCmd.AddCommand(optimizePreviewCmd())
	optimizeCmd.AddCommand(optimizeScheduleCmd())

	return optimizeCmd
}

// optimizeResourcesCmd creates the resource optimization command
func optimizeResourcesCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "resources [cluster-name]",
		Short: "Get resource optimization recommendations",
		Long:  "Get ML-powered recommendations for resource optimization",
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeResources(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to optimize")
	cmd.Flags().BoolP("detailed", "d", false, "detailed recommendations")
	cmd.Flags().BoolP("include-costs", "c", false, "include cost analysis")

	return cmd
}

// optimizeZeroPodCmd creates the zero-pod optimization command
func optimizeZeroPodCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "zero-pod [namespace]",
		Short: "Zero-pod scaling optimization",
		Long:  "Scale idle pods to zero with safety guarantees",
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeZeroPod(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("dry-run", "d", true, "simulate optimization without applying")
	cmd.Flags().Float64P("confidence", "c", 0.90, "confidence threshold")
	cmd.Flags().BoolP("auto-rollback", "r", true, "enable automatic rollback")

	return cmd
}

// optimizeCostCmd creates the cost optimization command
func optimizeCostCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "cost [cluster-name]",
		Short: "Cost optimization recommendations",
		Long:  "Get cost optimization recommendations and savings analysis",
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeCost(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "30d", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed cost breakdown")
	cmd.Flags().BoolP("include-forecasts", "f", false, "include cost forecasts")

	return cmd
}

// optimizeApplyCmd creates the apply optimization command
func optimizeApplyCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "apply [recommendation-id]",
		Short: "Apply optimization recommendation",
		Long:  "Apply a specific optimization recommendation",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeApply(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("confirm", "y", false, "skip confirmation prompt")
	cmd.Flags().BoolP("dry-run", "d", false, "simulate application")

	return cmd
}

// optimizePreviewCmd creates the preview optimization command
func optimizePreviewCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "preview [cluster-name]",
		Short: "Preview optimization changes",
		Long:  "Preview what changes would be made by optimizations",
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizePreview(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to preview")
	cmd.Flags().BoolP("detailed", "d", false, "detailed preview")

	return cmd
}

// optimizeScheduleCmd creates the schedule optimization command
func optimizeScheduleCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "schedule [cron-expression]",
		Short: "Schedule automated optimizations",
		Long:  "Schedule automated optimization runs",
		RunE: func(cmd *cobra.Command, args []string) error {
			return optimizeSchedule(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("cluster", "c", "", "cluster to schedule for")
	cmd.Flags().BoolP("enabled", "e", true, "enable the schedule")

	return cmd
}

// Implementation functions
func optimizeResources(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	namespace, _ := cmd.Flags().GetString("namespace")
	detailed, _ := cmd.Flags().GetBool("detailed")
	includeCosts, _ := cmd.Flags().GetBool("include-costs")

	// Build arguments
	cmdArgs := []string{"resources", clusterName}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if includeCosts {
		cmdArgs = append(cmdArgs, "--include-costs")
	}

	return executePythonCommand("optimize", cmdArgs)
}

func optimizeZeroPod(cmd *cobra.Command, args []string) error {
	namespace := "default"
	if len(args) > 0 {
		namespace = args[0]
	}

	// Get flags
	dryRun, _ := cmd.Flags().GetBool("dry-run")
	confidence, _ := cmd.Flags().GetFloat64("confidence")
	autoRollback, _ := cmd.Flags().GetBool("auto-rollback")

	// Build arguments
	cmdArgs := []string{"zero-pod", namespace}
	if dryRun {
		cmdArgs = append(cmdArgs, "--dry-run")
	}
	cmdArgs = append(cmdArgs, "--confidence", fmt.Sprintf("%.2f", confidence))
	if autoRollback {
		cmdArgs = append(cmdArgs, "--auto-rollback")
	}

	return executePythonCommand("optimize", cmdArgs)
}

func optimizeCost(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")
	includeForecasts, _ := cmd.Flags().GetBool("include-forecasts")

	// Build arguments
	cmdArgs := []string{"cost", clusterName}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if includeForecasts {
		cmdArgs = append(cmdArgs, "--include-forecasts")
	}

	return executePythonCommand("optimize", cmdArgs)
}

func optimizeApply(cmd *cobra.Command, args []string) error {
	recommendationID := args[0]

	// Get flags
	confirm, _ := cmd.Flags().GetBool("confirm")
	dryRun, _ := cmd.Flags().GetBool("dry-run")

	// Build arguments
	cmdArgs := []string{"apply", recommendationID}
	if confirm {
		cmdArgs = append(cmdArgs, "--confirm")
	}
	if dryRun {
		cmdArgs = append(cmdArgs, "--dry-run")
	}

	return executePythonCommand("optimize", cmdArgs)
}

func optimizePreview(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	namespace, _ := cmd.Flags().GetString("namespace")
	detailed, _ := cmd.Flags().GetBool("detailed")

	// Build arguments
	cmdArgs := []string{"preview", clusterName}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}

	return executePythonCommand("optimize", cmdArgs)
}

func optimizeSchedule(cmd *cobra.Command, args []string) error {
	cronExpr := "0 2 * * *" // Default: daily at 2 AM
	if len(args) > 0 {
		cronExpr = args[0]
	}

	// Get flags
	cluster, _ := cmd.Flags().GetString("cluster")
	enabled, _ := cmd.Flags().GetBool("enabled")

	// Build arguments
	cmdArgs := []string{"schedule", cronExpr}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}
	if enabled {
		cmdArgs = append(cmdArgs, "--enabled")
	}

	return executePythonCommand("optimize", cmdArgs)
} 