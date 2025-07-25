package commands

import (
	"fmt"

	"github.com/spf13/cobra"
)

// StorageCmd creates the storage command
func StorageCmd() *cobra.Command {
	storageCmd := &cobra.Command{
		Use:   "storage",
		Short: "Storage analysis and optimization",
		Long: `Storage analysis and optimization for Kubernetes clusters.

Examples:
  upid storage analyze my-cluster          # Analyze storage usage
  upid storage volumes my-cluster          # List storage volumes
  upid storage optimize my-cluster         # Optimize storage costs`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageAnalyze(cmd, args)
		},
	}

	// Add subcommands
	storageCmd.AddCommand(storageAnalyzeCmd())
	storageCmd.AddCommand(storageVolumesCmd())
	storageCmd.AddCommand(storageOptimizeCmd())
	storageCmd.AddCommand(storageCostsCmd())
	storageCmd.AddCommand(storageRecommendationsCmd())

	return storageCmd
}

// storageAnalyzeCmd creates the storage analyze command
func storageAnalyzeCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "analyze [cluster-id]",
		Short: "Analyze storage usage",
		Long:  "Analyze storage usage patterns and identify optimization opportunities",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageAnalyze(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to analyze")
	cmd.Flags().StringP("time-range", "t", "7d", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed analysis")
	cmd.Flags().BoolP("include-costs", "c", false, "include cost analysis")

	return cmd
}

// storageVolumesCmd creates the storage volumes command
func storageVolumesCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "volumes [cluster-id]",
		Short: "List storage volumes",
		Long:  "List and analyze storage volumes in the cluster",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageVolumes(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to filter")
	cmd.Flags().StringP("type", "t", "", "storage type filter")
	cmd.Flags().BoolP("unused", "u", false, "show only unused volumes")
	cmd.Flags().BoolP("orphaned", "o", false, "show orphaned volumes")

	return cmd
}

// storageOptimizeCmd creates the storage optimize command
func storageOptimizeCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "optimize [cluster-id]",
		Short: "Optimize storage costs",
		Long:  "Optimize storage costs and usage patterns",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageOptimize(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("simulate", "s", false, "simulate optimization without applying")
	cmd.Flags().BoolP("aggressive", "a", false, "apply aggressive optimization")
	cmd.Flags().StringP("strategy", "", "balanced", "optimization strategy")
	cmd.Flags().BoolP("include-orphaned", "o", false, "include orphaned volumes")

	return cmd
}

// storageCostsCmd creates the storage costs command
func storageCostsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "costs [cluster-id]",
		Short: "Analyze storage costs",
		Long:  "Analyze storage costs and cost optimization opportunities",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageCosts(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "30d", "time range for cost analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed cost breakdown")
	cmd.Flags().StringP("group-by", "g", "namespace", "group costs by (namespace, type, class)")

	return cmd
}

// storageRecommendationsCmd creates the storage recommendations command
func storageRecommendationsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "recommendations [cluster-id]",
		Short: "Get storage recommendations",
		Long:  "Get AI-powered storage optimization recommendations",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return storageRecommendations(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("priority", "p", "medium", "recommendation priority (low, medium, high)")
	cmd.Flags().BoolP("include-costs", "c", true, "include cost impact analysis")
	cmd.Flags().BoolP("include-risks", "r", true, "include risk assessment")

	return cmd
}

// Implementation functions
func storageAnalyze(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	namespace, _ := cmd.Flags().GetString("namespace")
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")
	includeCosts, _ := cmd.Flags().GetBool("include-costs")

	// Build arguments
	cmdArgs := []string{"storage", "analyze", clusterID}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if includeCosts {
		cmdArgs = append(cmdArgs, "--include-costs")
	}

	return executePythonCommand("storage", cmdArgs)
}

func storageVolumes(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	namespace, _ := cmd.Flags().GetString("namespace")
	storageType, _ := cmd.Flags().GetString("type")
	unused, _ := cmd.Flags().GetBool("unused")
	orphaned, _ := cmd.Flags().GetBool("orphaned")

	// Build arguments
	cmdArgs := []string{"storage", "volumes", clusterID}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if storageType != "" {
		cmdArgs = append(cmdArgs, "--type", storageType)
	}
	if unused {
		cmdArgs = append(cmdArgs, "--unused")
	}
	if orphaned {
		cmdArgs = append(cmdArgs, "--orphaned")
	}

	return executePythonCommand("storage", cmdArgs)
}

func storageOptimize(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	simulate, _ := cmd.Flags().GetBool("simulate")
	aggressive, _ := cmd.Flags().GetBool("aggressive")
	strategy, _ := cmd.Flags().GetString("strategy")
	includeOrphaned, _ := cmd.Flags().GetBool("include-orphaned")

	// Build arguments
	cmdArgs := []string{"storage", "optimize", clusterID}
	if simulate {
		cmdArgs = append(cmdArgs, "--simulate")
	}
	if aggressive {
		cmdArgs = append(cmdArgs, "--aggressive")
	}
	if strategy != "" {
		cmdArgs = append(cmdArgs, "--strategy", strategy)
	}
	if includeOrphaned {
		cmdArgs = append(cmdArgs, "--include-orphaned")
	}

	return executePythonCommand("storage", cmdArgs)
}

func storageCosts(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")
	groupBy, _ := cmd.Flags().GetString("group-by")

	// Build arguments
	cmdArgs := []string{"storage", "costs", clusterID}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if groupBy != "" {
		cmdArgs = append(cmdArgs, "--group-by", groupBy)
	}

	return executePythonCommand("storage", cmdArgs)
}

func storageRecommendations(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	priority, _ := cmd.Flags().GetString("priority")
	includeCosts, _ := cmd.Flags().GetBool("include-costs")
	includeRisks, _ := cmd.Flags().GetBool("include-risks")

	// Build arguments
	cmdArgs := []string{"storage", "recommendations", clusterID}
	if priority != "" {
		cmdArgs = append(cmdArgs, "--priority", priority)
	}
	cmdArgs = append(cmdArgs, "--include-costs", fmt.Sprintf("%t", includeCosts))
	cmdArgs = append(cmdArgs, "--include-risks", fmt.Sprintf("%t", includeRisks))

	return executePythonCommand("storage", cmdArgs)
}

 