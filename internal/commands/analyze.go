package commands

import (
	"fmt"

	"github.com/spf13/cobra"
)

// AnalyzeCmd creates the analyze command
func AnalyzeCmd() *cobra.Command {
	analyzeCmd := &cobra.Command{
		Use:   "analyze",
		Short: "Analyze Kubernetes clusters and resources",
		Long: `Analyze Kubernetes clusters and resources for optimization opportunities.
		
Examples:
  upid analyze cluster                    # Analyze entire cluster
  upid analyze pod my-pod --namespace default  # Analyze specific pod
  upid analyze idle --confidence 0.85    # Find idle workloads
  upid analyze resources --time-range 24h # Analyze resource usage`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzeCluster(cmd, args)
		},
	}

	// Add subcommands
	analyzeCmd.AddCommand(analyzeClusterCmd())
	analyzeCmd.AddCommand(analyzePodCmd())
	analyzeCmd.AddCommand(analyzeIdleCmd())
	analyzeCmd.AddCommand(analyzeResourcesCmd())
	analyzeCmd.AddCommand(analyzeCostCmd())
	analyzeCmd.AddCommand(analyzePerformanceCmd())

	return analyzeCmd
}

// analyzeClusterCmd creates the cluster analysis command
func analyzeClusterCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "cluster [cluster-name]",
		Short: "Analyze Kubernetes cluster",
		Long:  "Perform comprehensive analysis of a Kubernetes cluster",
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzeCluster(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace to analyze")
	cmd.Flags().StringP("time-range", "t", "24h", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed analysis")
	cmd.Flags().BoolP("include-costs", "c", false, "include cost analysis")

	return cmd
}

// analyzePodCmd creates the pod analysis command
func analyzePodCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "pod [pod-name]",
		Short: "Analyze specific pod",
		Long:  "Analyze resource usage and performance of a specific pod",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzePod(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "default", "namespace of the pod")
	cmd.Flags().StringP("time-range", "t", "24h", "time range for analysis")

	return cmd
}

// analyzeIdleCmd creates the idle analysis command
func analyzeIdleCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "idle [namespace]",
		Short: "Find idle workloads",
		Long:  "Identify idle workloads using ML-powered analysis",
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzeIdle(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().Float64P("confidence", "c", 0.85, "confidence threshold")
	cmd.Flags().StringP("time-range", "t", "7d", "time range for analysis")
	cmd.Flags().BoolP("include-health-checks", "h", true, "include health check filtering")

	return cmd
}

// analyzeResourcesCmd creates the resource analysis command
func analyzeResourcesCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "resources [resource-type]",
		Short: "Analyze resource usage",
		Long:  "Analyze CPU, memory, and network usage patterns",
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzeResources(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "24h", "time range for analysis")
	cmd.Flags().StringP("namespace", "n", "", "namespace to analyze")

	return cmd
}

// analyzeCostCmd creates the cost analysis command
func analyzeCostCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "cost [cluster-name]",
		Short: "Analyze cluster costs",
		Long:  "Analyze cost breakdown and optimization opportunities",
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzeCost(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "30d", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed cost breakdown")

	return cmd
}

// analyzePerformanceCmd creates the performance analysis command
func analyzePerformanceCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "performance [cluster-name]",
		Short: "Analyze cluster performance",
		Long:  "Analyze performance metrics and bottlenecks",
		RunE: func(cmd *cobra.Command, args []string) error {
			return analyzePerformance(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "24h", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed performance analysis")

	return cmd
}

// Implementation functions
func analyzeCluster(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	namespace, _ := cmd.Flags().GetString("namespace")
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")
	includeCosts, _ := cmd.Flags().GetBool("include-costs")

	// Build arguments
	args = []string{"cluster", clusterName}
	if namespace != "" {
		args = append(args, "--namespace", namespace)
	}
	if timeRange != "" {
		args = append(args, "--time-range", timeRange)
	}
	if detailed {
		args = append(args, "--detailed")
	}
	if includeCosts {
		args = append(args, "--include-costs")
	}

	return executePythonCommand("analyze", args)
}

func analyzePod(cmd *cobra.Command, args []string) error {
	podName := args[0]
	namespace, _ := cmd.Flags().GetString("namespace")
	timeRange, _ := cmd.Flags().GetString("time-range")

	// Build arguments
	cmdArgs := []string{"pod", podName}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}

	return executePythonCommand("analyze", cmdArgs)
}

func analyzeIdle(cmd *cobra.Command, args []string) error {
	namespace := "default"
	if len(args) > 0 {
		namespace = args[0]
	}

	// Get flags
	confidence, _ := cmd.Flags().GetFloat64("confidence")
	timeRange, _ := cmd.Flags().GetString("time-range")
	includeHealthChecks, _ := cmd.Flags().GetBool("include-health-checks")

	// Build arguments
	cmdArgs := []string{"idle", namespace}
	cmdArgs = append(cmdArgs, "--confidence", fmt.Sprintf("%.2f", confidence))
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if !includeHealthChecks {
		cmdArgs = append(cmdArgs, "--no-health-check-filtering")
	}

	return executePythonCommand("analyze", cmdArgs)
}

func analyzeResources(cmd *cobra.Command, args []string) error {
	resourceType := "all"
	if len(args) > 0 {
		resourceType = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	namespace, _ := cmd.Flags().GetString("namespace")

	// Build arguments
	cmdArgs := []string{"resources", resourceType}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}

	return executePythonCommand("analyze", cmdArgs)
}

func analyzeCost(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")

	// Build arguments
	cmdArgs := []string{"cost", clusterName}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}

	return executePythonCommand("analyze", cmdArgs)
}

func analyzePerformance(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")

	// Build arguments
	cmdArgs := []string{"performance", clusterName}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}

	return executePythonCommand("analyze", cmdArgs)
}

 