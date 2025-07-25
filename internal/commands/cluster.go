package commands

import (
	"fmt"

	"github.com/spf13/cobra"
)

// ClusterCmd creates the cluster command
func ClusterCmd() *cobra.Command {
	clusterCmd := &cobra.Command{
		Use:   "cluster",
		Short: "Manage Kubernetes clusters",
		Long: `Manage Kubernetes clusters and their configurations.

Examples:
  upid cluster list                    # List all clusters
  upid cluster get my-cluster          # Get cluster details
  upid cluster add my-cluster          # Add a new cluster
  upid cluster status my-cluster       # Get cluster health status`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return listClusters(cmd, args)
		},
	}

	// Add subcommands
	clusterCmd.AddCommand(listClustersCmd())
	clusterCmd.AddCommand(getClusterCmd())
	clusterCmd.AddCommand(addClusterCmd())
	clusterCmd.AddCommand(updateClusterCmd())
	clusterCmd.AddCommand(deleteClusterCmd())
	clusterCmd.AddCommand(clusterStatusCmd())

	return clusterCmd
}

// listClustersCmd creates the list clusters command
func listClustersCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "list",
		Short: "List all clusters",
		Long:  "List all clusters accessible to the current user",
		RunE: func(cmd *cobra.Command, args []string) error {
			return listClusters(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("status", "s", "", "filter by status (active, inactive, error)")
	cmd.Flags().StringP("organization", "o", "", "filter by organization")
	cmd.Flags().BoolP("detailed", "d", false, "detailed output")

	return cmd
}

// getClusterCmd creates the get cluster command
func getClusterCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "get [cluster-id]",
		Short: "Get cluster details",
		Long:  "Get detailed information about a specific cluster",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return getCluster(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("include-metrics", "m", false, "include cluster metrics")
	cmd.Flags().BoolP("include-costs", "c", false, "include cost information")

	return cmd
}

// addClusterCmd creates the add cluster command
func addClusterCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "add [cluster-name]",
		Short: "Add a new cluster",
		Long:  "Add a new Kubernetes cluster to UPID",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return addCluster(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("kubeconfig", "k", "", "path to kubeconfig file")
	cmd.Flags().StringP("context", "x", "", "kubernetes context to use")
	cmd.Flags().StringP("namespace", "n", "default", "default namespace")
	cmd.Flags().StringP("description", "d", "", "cluster description")
	cmd.Flags().StringP("organization", "o", "", "organization ID")
	cmd.Flags().BoolP("auto-monitor", "m", true, "enable automatic monitoring")

	return cmd
}

// updateClusterCmd creates the update cluster command
func updateClusterCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "update [cluster-id]",
		Short: "Update cluster configuration",
		Long:  "Update cluster configuration and settings",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return updateCluster(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("name", "n", "", "new cluster name")
	cmd.Flags().StringP("description", "d", "", "cluster description")
	cmd.Flags().StringP("kubeconfig", "k", "", "path to kubeconfig file")
	cmd.Flags().StringP("context", "x", "", "kubernetes context")
	cmd.Flags().BoolP("auto-monitor", "m", false, "enable/disable automatic monitoring")

	return cmd
}

// deleteClusterCmd creates the delete cluster command
func deleteClusterCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "delete [cluster-id]",
		Short: "Delete a cluster",
		Long:  "Delete a cluster from UPID (does not affect the actual cluster)",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return deleteCluster(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("force", "f", false, "force deletion without confirmation")
	cmd.Flags().BoolP("cleanup-data", "c", false, "cleanup all associated data")

	return cmd
}

// clusterStatusCmd creates the cluster status command
func clusterStatusCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "status [cluster-id]",
		Short: "Get cluster health status",
		Long:  "Get detailed health status and metrics for a cluster",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return clusterStatus(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("detailed", "d", false, "detailed status information")
	cmd.Flags().StringP("time-range", "t", "1h", "time range for metrics")

	return cmd
}

// Implementation functions
func listClusters(cmd *cobra.Command, args []string) error {
	// Get flags
	status, _ := cmd.Flags().GetString("status")
	organization, _ := cmd.Flags().GetString("organization")
	detailed, _ := cmd.Flags().GetBool("detailed")

	// Build arguments
	cmdArgs := []string{"clusters", "list"}
	if status != "" {
		cmdArgs = append(cmdArgs, "--status", status)
	}
	if organization != "" {
		cmdArgs = append(cmdArgs, "--organization", organization)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}

	return executePythonCommand("clusters", cmdArgs)
}

func getCluster(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	includeMetrics, _ := cmd.Flags().GetBool("include-metrics")
	includeCosts, _ := cmd.Flags().GetBool("include-costs")

	// Build arguments
	cmdArgs := []string{"clusters", "get", clusterID}
	if includeMetrics {
		cmdArgs = append(cmdArgs, "--include-metrics")
	}
	if includeCosts {
		cmdArgs = append(cmdArgs, "--include-costs")
	}

	return executePythonCommand("clusters", cmdArgs)
}

func addCluster(cmd *cobra.Command, args []string) error {
	clusterName := args[0]
	kubeconfig, _ := cmd.Flags().GetString("kubeconfig")
	context, _ := cmd.Flags().GetString("context")
	namespace, _ := cmd.Flags().GetString("namespace")
	description, _ := cmd.Flags().GetString("description")
	organization, _ := cmd.Flags().GetString("organization")
	autoMonitor, _ := cmd.Flags().GetBool("auto-monitor")

	// Build arguments
	cmdArgs := []string{"clusters", "add", clusterName}
	if kubeconfig != "" {
		cmdArgs = append(cmdArgs, "--kubeconfig", kubeconfig)
	}
	if context != "" {
		cmdArgs = append(cmdArgs, "--context", context)
	}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if description != "" {
		cmdArgs = append(cmdArgs, "--description", description)
	}
	if organization != "" {
		cmdArgs = append(cmdArgs, "--organization", organization)
	}
	if !autoMonitor {
		cmdArgs = append(cmdArgs, "--no-auto-monitor")
	}

	return executePythonCommand("clusters", cmdArgs)
}

func updateCluster(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	name, _ := cmd.Flags().GetString("name")
	description, _ := cmd.Flags().GetString("description")
	kubeconfig, _ := cmd.Flags().GetString("kubeconfig")
	context, _ := cmd.Flags().GetString("context")
	autoMonitor, _ := cmd.Flags().GetBool("auto-monitor")

	// Build arguments
	cmdArgs := []string{"clusters", "update", clusterID}
	if name != "" {
		cmdArgs = append(cmdArgs, "--name", name)
	}
	if description != "" {
		cmdArgs = append(cmdArgs, "--description", description)
	}
	if kubeconfig != "" {
		cmdArgs = append(cmdArgs, "--kubeconfig", kubeconfig)
	}
	if context != "" {
		cmdArgs = append(cmdArgs, "--context", context)
	}
	cmdArgs = append(cmdArgs, "--auto-monitor", fmt.Sprintf("%t", autoMonitor))

	return executePythonCommand("clusters", cmdArgs)
}

func deleteCluster(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	force, _ := cmd.Flags().GetBool("force")
	cleanupData, _ := cmd.Flags().GetBool("cleanup-data")

	// Build arguments
	cmdArgs := []string{"clusters", "delete", clusterID}
	if force {
		cmdArgs = append(cmdArgs, "--force")
	}
	if cleanupData {
		cmdArgs = append(cmdArgs, "--cleanup-data")
	}

	return executePythonCommand("clusters", cmdArgs)
}

func clusterStatus(cmd *cobra.Command, args []string) error {
	clusterID := args[0]
	detailed, _ := cmd.Flags().GetBool("detailed")
	timeRange, _ := cmd.Flags().GetString("time-range")

	// Build arguments
	cmdArgs := []string{"clusters", "status", clusterID}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}

	return executePythonCommand("clusters", cmdArgs)
}

 