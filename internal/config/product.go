package config

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// ProductInfo represents UPID product information
type ProductInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Version     string `json:"version"`
	Author      string `json:"author"`
	AuthorEmail string `json:"author_email"`
	Homepage    string `json:"homepage"`
	Repository  string `json:"repository"`
	License     string `json:"license"`
}

// UPIDConfig represents the centralized UPID configuration
type UPIDConfig struct {
	Product ProductInfo `json:"product"`
}

var (
	// Global product configuration (separate from main Config)
	productConfig *UPIDConfig
	
	// Default values as fallbacks
	defaultVersion     = "2.0.0"
	defaultName        = "UPID CLI"
	defaultDescription = "Universal Pod Intelligence Director - Enterprise-grade Kubernetes cost optimization platform"
	defaultAuthor      = "UPID Development Team"
	defaultAuthorEmail = "dev@upid.io"
	defaultHomepage    = "https://upid.io"
	defaultRepository  = "https://github.com/upid/upid-cli"
	defaultLicense     = "MIT"
)

// LoadProductInfo loads product information from centralized configuration
func LoadProductInfo() (*ProductInfo, error) {
	if productConfig != nil {
		return &productConfig.Product, nil
	}

	// Try to load from Python configuration system
	config, err := loadFromPythonConfig()
	if err == nil {
		productConfig = config
		return &productConfig.Product, nil
	}

	// Fall back to default values
	return &ProductInfo{
		Name:        defaultName,
		Description: defaultDescription,
		Version:     defaultVersion,
		Author:      defaultAuthor,
		AuthorEmail: defaultAuthorEmail,
		Homepage:    defaultHomepage,
		Repository:  defaultRepository,
		License:     defaultLicense,
	}, nil
}

// loadFromPythonConfig attempts to load configuration using the Python config system
func loadFromPythonConfig() (*UPIDConfig, error) {
	// Get the project root directory
	projectRoot, err := getProjectRoot()
	if err != nil {
		return nil, fmt.Errorf("failed to find project root: %w", err)
	}

	// Try to execute Python script to get configuration
	pythonScript := fmt.Sprintf(`
import sys
import os
sys.path.insert(0, '%s')
try:
    from upid_config import get_config
    config = get_config()
    import json
    print(json.dumps({
        "product": {
            "name": config.product.name,
            "description": config.product.description,
            "version": config.product.version,
            "author": config.product.author,
            "author_email": config.product.author_email,
            "homepage": config.product.homepage,
            "repository": config.product.repository,
            "license": config.product.license
        }
    }))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    exit(1)
`, projectRoot)

	// Execute Python script
	cmd := exec.Command("python3", "-c", pythonScript)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to execute Python config script: %w", err)
	}

	// Parse JSON output
	var config UPIDConfig
	if err := json.Unmarshal(output, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config JSON: %w", err)
	}

	return &config, nil
}

// getProjectRoot finds the project root directory by looking for key files
func getProjectRoot() (string, error) {
	// Start from current directory and walk up
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}

	for {
		// Check for key files that indicate project root
		for _, marker := range []string{"upid_config.py", "go.mod", "setup.py", ".git"} {
			if _, err := os.Stat(filepath.Join(dir, marker)); err == nil {
				return dir, nil
			}
		}

		// Move up one directory
		parent := filepath.Dir(dir)
		if parent == dir {
			// Reached filesystem root
			break
		}
		dir = parent
	}

	return "", fmt.Errorf("project root not found")
}

// GetVersion returns the current UPID version
func GetVersion() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultVersion
	}
	return info.Version
}

// GetName returns the product name
func GetName() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultName
	}
	return info.Name
}

// GetDescription returns the product description
func GetDescription() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultDescription
	}
	return info.Description
}

// GetAuthor returns the product author
func GetAuthor() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultAuthor
	}
	return info.Author
}

// GetAuthorEmail returns the author email
func GetAuthorEmail() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultAuthorEmail
	}
	return info.AuthorEmail
}

// GetHomepage returns the product homepage
func GetHomepage() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultHomepage
	}
	return info.Homepage
}

// GetRepository returns the product repository URL
func GetRepository() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultRepository
	}
	return info.Repository
}

// GetLicense returns the product license
func GetLicense() string {
	info, err := LoadProductInfo()
	if err != nil {
		return defaultLicense
	}
	return info.License
}

// GetFullVersion returns a formatted version string
func GetFullVersion(commit, date string) string {
	version := GetVersion()
	name := GetName()
	
	if commit == "" {
		commit = "development"
	}
	if date == "" {
		date = "unknown"
	}
	
	return fmt.Sprintf("%s %s (commit: %s, date: %s)", name, version, commit, date)
}

// GetShortDescription returns a short description for CLI usage
func GetShortDescription() string {
	parts := strings.Split(GetDescription(), " - ")
	if len(parts) > 0 {
		return parts[0]
	}
	return GetDescription()
}