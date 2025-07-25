package commands

import (
	"github.com/spf13/cobra"
)

// AICmd creates the AI command
func AICmd() *cobra.Command {
	aiCmd := &cobra.Command{
		Use:   "ai",
		Short: "AI-powered insights and recommendations",
		Long:  "Get AI-powered insights and recommendations for Kubernetes optimization",
		RunE: func(cmd *cobra.Command, args []string) error {
			return aiInsights(cmd, args)
		},
	}

	// Add subcommands
	aiCmd.AddCommand(aiInsightsCmd())
	aiCmd.AddCommand(aiRecommendationsCmd())
	aiCmd.AddCommand(aiPredictCmd())
	aiCmd.AddCommand(aiExplainCmd())

	return aiCmd
}

// aiInsightsCmd creates the insights command
func aiInsightsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "insights [cluster-name]",
		Short: "Get AI insights",
		Long:  "Get AI-powered insights about your Kubernetes cluster",
		RunE: func(cmd *cobra.Command, args []string) error {
			return aiInsights(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("time-range", "t", "30d", "time range for analysis")
	cmd.Flags().BoolP("detailed", "d", false, "detailed insights")

	return cmd
}

// aiRecommendationsCmd creates the recommendations command
func aiRecommendationsCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "recommendations [cluster-name]",
		Short: "Get AI recommendations",
		Long:  "Get AI-powered recommendations for optimization",
		RunE: func(cmd *cobra.Command, args []string) error {
			return aiRecommendations(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("category", "c", "", "recommendation category")
	cmd.Flags().BoolP("prioritized", "p", false, "prioritized recommendations")

	return cmd
}

// aiPredictCmd creates the predict command
func aiPredictCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "predict [metric]",
		Short: "Predict future metrics",
		Long:  "Predict future resource usage and costs",
		RunE: func(cmd *cobra.Command, args []string) error {
			return aiPredict(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("timeframe", "t", "30d", "prediction timeframe")
	cmd.Flags().StringP("cluster", "c", "", "cluster name")

	return cmd
}

// aiExplainCmd creates the explain command
func aiExplainCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "explain [resource]",
		Short: "Explain resource behavior",
		Long:  "Get AI explanation of resource behavior and anomalies",
		RunE: func(cmd *cobra.Command, args []string) error {
			return aiExplain(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("namespace", "n", "", "namespace")
	cmd.Flags().StringP("time-range", "t", "24h", "time range")

	return cmd
}

// Implementation functions
func aiInsights(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	timeRange, _ := cmd.Flags().GetString("time-range")
	detailed, _ := cmd.Flags().GetBool("detailed")

	// Build arguments
	cmdArgs := []string{"insights", clusterName}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}
	if detailed {
		cmdArgs = append(cmdArgs, "--detailed")
	}

	return executePythonCommand("ai", cmdArgs)
}

func aiRecommendations(cmd *cobra.Command, args []string) error {
	clusterName := "default"
	if len(args) > 0 {
		clusterName = args[0]
	}

	// Get flags
	category, _ := cmd.Flags().GetString("category")
	prioritized, _ := cmd.Flags().GetBool("prioritized")

	// Build arguments
	cmdArgs := []string{"recommendations", clusterName}
	if category != "" {
		cmdArgs = append(cmdArgs, "--category", category)
	}
	if prioritized {
		cmdArgs = append(cmdArgs, "--prioritized")
	}

	return executePythonCommand("ai", cmdArgs)
}

func aiPredict(cmd *cobra.Command, args []string) error {
	metric := "cost"
	if len(args) > 0 {
		metric = args[0]
	}

	// Get flags
	timeframe, _ := cmd.Flags().GetString("timeframe")
	cluster, _ := cmd.Flags().GetString("cluster")

	// Build arguments
	cmdArgs := []string{"predict", metric}
	if timeframe != "" {
		cmdArgs = append(cmdArgs, "--timeframe", timeframe)
	}
	if cluster != "" {
		cmdArgs = append(cmdArgs, "--cluster", cluster)
	}

	return executePythonCommand("ai", cmdArgs)
}

func aiExplain(cmd *cobra.Command, args []string) error {
	resource := "all"
	if len(args) > 0 {
		resource = args[0]
	}

	// Get flags
	namespace, _ := cmd.Flags().GetString("namespace")
	timeRange, _ := cmd.Flags().GetString("time-range")

	// Build arguments
	cmdArgs := []string{"explain", resource}
	if namespace != "" {
		cmdArgs = append(cmdArgs, "--namespace", namespace)
	}
	if timeRange != "" {
		cmdArgs = append(cmdArgs, "--time-range", timeRange)
	}

	return executePythonCommand("ai", cmdArgs)
} 