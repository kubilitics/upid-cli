package commands

import (
	"github.com/spf13/cobra"
)

// AuthCmd creates the auth command
func AuthCmd() *cobra.Command {
	authCmd := &cobra.Command{
		Use:   "auth",
		Short: "Authentication and authorization",
		Long:  "Manage authentication and authorization for UPID CLI",
		RunE: func(cmd *cobra.Command, args []string) error {
			return authStatus(cmd, args)
		},
	}

	// Add subcommands
	authCmd.AddCommand(authLoginCmd())
	authCmd.AddCommand(authLogoutCmd())
	authCmd.AddCommand(authStatusCmd())
	authCmd.AddCommand(authConfigureCmd())

	return authCmd
}

// authLoginCmd creates the login command
func authLoginCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "login [provider]",
		Short: "Login to UPID",
		Long:  "Authenticate with UPID using various providers",
		RunE: func(cmd *cobra.Command, args []string) error {
			return authLogin(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("username", "u", "", "username")
	cmd.Flags().StringP("password", "p", "", "password")
	cmd.Flags().StringP("token", "t", "", "access token")

	return cmd
}

// authLogoutCmd creates the logout command
func authLogoutCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "logout",
		Short: "Logout from UPID",
		Long:  "Logout and clear authentication tokens",
		RunE: func(cmd *cobra.Command, args []string) error {
			return authLogout(cmd, args)
		},
	}

	return cmd
}

// authStatusCmd creates the status command
func authStatusCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "status",
		Short: "Check authentication status",
		Long:  "Check current authentication status and token validity",
		RunE: func(cmd *cobra.Command, args []string) error {
			return authStatus(cmd, args)
		},
	}

	return cmd
}

// authConfigureCmd creates the configure command
func authConfigureCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "configure [provider]",
		Short: "Configure authentication",
		Long:  "Configure authentication settings for various providers",
		RunE: func(cmd *cobra.Command, args []string) error {
			return authConfigure(cmd, args)
		},
	}

	// Add flags
	cmd.Flags().StringP("endpoint", "e", "", "authentication endpoint")
	cmd.Flags().StringP("client-id", "c", "", "client ID")
	cmd.Flags().StringP("client-secret", "s", "", "client secret")

	return cmd
}

// Implementation functions
func authLogin(cmd *cobra.Command, args []string) error {
	provider := "default"
	if len(args) > 0 {
		provider = args[0]
	}

	// Get flags
	username, _ := cmd.Flags().GetString("username")
	password, _ := cmd.Flags().GetString("password")
	token, _ := cmd.Flags().GetString("token")

	// Build arguments
	cmdArgs := []string{"login", provider}
	if username != "" {
		cmdArgs = append(cmdArgs, "--username", username)
	}
	if password != "" {
		cmdArgs = append(cmdArgs, "--password", password)
	}
	if token != "" {
		cmdArgs = append(cmdArgs, "--token", token)
	}

	return executePythonCommand("auth", cmdArgs)
}

func authLogout(cmd *cobra.Command, args []string) error {
	return executePythonCommand("auth", []string{"logout"})
}

func authStatus(cmd *cobra.Command, args []string) error {
	return executePythonCommand("auth", []string{"status"})
}

func authConfigure(cmd *cobra.Command, args []string) error {
	provider := "default"
	if len(args) > 0 {
		provider = args[0]
	}

	// Get flags
	endpoint, _ := cmd.Flags().GetString("endpoint")
	clientID, _ := cmd.Flags().GetString("client-id")
	clientSecret, _ := cmd.Flags().GetString("client-secret")

	// Build arguments
	cmdArgs := []string{"configure", provider}
	if endpoint != "" {
		cmdArgs = append(cmdArgs, "--endpoint", endpoint)
	}
	if clientID != "" {
		cmdArgs = append(cmdArgs, "--client-id", clientID)
	}
	if clientSecret != "" {
		cmdArgs = append(cmdArgs, "--client-secret", clientSecret)
	}

	return executePythonCommand("auth", cmdArgs)
} 