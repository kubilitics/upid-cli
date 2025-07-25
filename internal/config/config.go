package config

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/viper"
)

// Config holds the application configuration
type Config struct {
	Debug     bool   `mapstructure:"debug"`
	Verbose   bool   `mapstructure:"verbose"`
	LogLevel  string `mapstructure:"log_level"`
	LogFile   string `mapstructure:"log_file"`
	PythonPath string `mapstructure:"python_path"`
	ScriptPath  string `mapstructure:"script_path"`
	OutputFormat string `mapstructure:"output_format"`
	ConfigFile   string `mapstructure:"config_file"`
}

var (
	// Global config instance
	globalConfig *Config
)

// Init initializes the configuration system
func Init() error {
	// Set default values
	viper.SetDefault("debug", false)
	viper.SetDefault("verbose", false)
	viper.SetDefault("log_level", "info")
	viper.SetDefault("output_format", "table")
	viper.SetDefault("python_path", "python3")
	viper.SetDefault("script_path", "./upid_python/cli.py")

	// Environment variables
	viper.SetEnvPrefix("UPID")
	viper.AutomaticEnv()

	// Config file
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	
	// Search for config file in multiple locations
	home, err := os.UserHomeDir()
	if err == nil {
		viper.AddConfigPath(filepath.Join(home, ".upid"))
	}
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")

	// Read config file if it exists
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return fmt.Errorf("failed to read config file: %v", err)
		}
	}

	// Parse into struct
	globalConfig = &Config{}
	if err := viper.Unmarshal(globalConfig); err != nil {
		return fmt.Errorf("failed to unmarshal config: %v", err)
	}

	return nil
}

// GetConfig returns the global configuration
func GetConfig() *Config {
	return globalConfig
}

// SetupLogging configures logging based on configuration
func SetupLogging() {
	// Set log level based on debug/verbose flags
	if globalConfig.Debug {
		globalConfig.LogLevel = "debug"
	} else if globalConfig.Verbose {
		globalConfig.LogLevel = "verbose"
	}

	// Configure logging output
	if globalConfig.LogFile != "" {
		// TODO: Implement file logging
	}
}

// GetPythonPath returns the Python executable path
func GetPythonPath() string {
	return globalConfig.PythonPath
}

// GetScriptPath returns the Python script path
func GetScriptPath() string {
	return globalConfig.ScriptPath
}

// GetOutputFormat returns the output format
func GetOutputFormat() string {
	return globalConfig.OutputFormat
}

// IsDebug returns true if debug mode is enabled
func IsDebug() bool {
	return globalConfig.Debug
}

// IsVerbose returns true if verbose mode is enabled
func IsVerbose() bool {
	return globalConfig.Verbose
} 