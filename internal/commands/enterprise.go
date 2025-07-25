package commands

import (
	"github.com/spf13/cobra"
)

// EnterpriseCmd creates the enterprise command
func EnterpriseCmd() *cobra.Command {
	enterpriseCmd := &cobra.Command{
		Use:   "enterprise",
		Short: "Enterprise features and management",
		Long:  "Manage enterprise features, multi-cluster operations, and advanced configurations",
		RunE: func(cmd *cobra.Command, args []string) error {
			return enterpriseStatus(cmd, args)
		},
	}

	// Add subcommands
	enterpriseCmd.AddCommand(enterpriseStatusCmd())
	enterpriseCmd.AddCommand(enterpriseConfigureCmd())
	enterpriseCmd.AddCommand(enterpriseSyncCmd())

	return enterpriseCmd
}

// enterpriseStatusCmd creates the status command
func enterpriseStatusCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "status",
		Short: "Check enterprise status",
		Long:  "Check enterprise features and configuration status",
		RunE: func(cmd *cobra.Command, args []string) error {
			return enterpriseStatus(cmd, args)
		},
	}

	return cmd
}

// enterpriseConfigureCmd creates the configure command
func enterpriseConfigureCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "configure [feature]",
		Short: "Configure enterprise features",
		Long:  "Configure enterprise features and settings",
		RunE: func(cmd *cobra.Command, args []string) error {
			return enterpriseConfigure(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("endpoint", "e", "", "enterprise endpoint")
	cmd.Flags().StringP("token", "t", "", "enterprise token")

	return cmd
}

// enterpriseSyncCmd creates the sync command
func enterpriseSyncCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "sync [cluster-name]",
		Short: "Sync with enterprise",
		Long:  "Sync cluster data with enterprise platform",
		RunE: func(cmd *cobra.Command, args []string) error {
			return enterpriseSync(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().BoolP("force", "f", false, "force sync")
	cmd.Flags().StringP("time-range", "t", "24h", "time range to sync")

	return cmd
}

// Implementation functions
func enterpriseStatus(cmd *cobra.Command, args []string) error {
	return executePythonCommand("enterprise", []string{"status"})
}

func enterpriseConfigure(cmd *cobra.Command, args []string) error {
	feature := "all"
	if len(args) > 0 {
		feature = args[0]
	}

	// Get flags
	endpoint, _ := cmd.Flags().GetString("endpoint")
	token, _ := cmd.Flags().GetString("token")

	// Build arguments
	cmdArgs := []string{"configure", feature}
	if endpoint != "" {
		cmdArgs = append(cmdArgs, "--endpoint", endpoint)
	}
	if token != "" {
		cmdArgs = append(cmdArgs, "--token", token)
	}

	return executePythonCommand("enterprise", cmdArgs)
}

func enterpriseSync(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	force, _ := cmd.Flags().GetBool("force")
	timeRange, _ := cmd.Flags().GetString("time-range")

	// Build arguments
	cmdArgs := []string{"sync", clusterName}
	if force {
		cmdArgs = append(cmdArgs, "--force")
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}

	return executePythonCommand("enterprise", cmdArgs)
} 