#!/usr/bin/env python3
"""
UPID CLI Command Discovery Tool
Comprehensive script to extract all available commands from UPID CLI
"""

import subprocess
import sys
import re
import json
from typing import List, Dict, Set
from pathlib import Path

class UPIDCommandDiscovery:
    def __init__(self):
        self.commands = set()
        self.command_tree = {}
        self.errors = []
        
    def check_upid_available(self) -> bool:
        """Check if UPID CLI is available in PATH"""
        try:
            result = subprocess.run(['upid', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 or result.stderr:
                print(f"✓ UPID CLI found")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("✗ UPID CLI not found in PATH")
        print("Please ensure UPID CLI is installed and accessible")
        return False
    
    def run_command(self, cmd_args: List[str]) -> tuple:
        """Safely run a command and return stdout, stderr, returncode"""
        try:
            result = subprocess.run(cmd_args, capture_output=True, 
                                  text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            self.errors.append(f"Timeout for command: {' '.join(cmd_args)}")
            return "", "", 1
        except Exception as e:
            self.errors.append(f"Error running {' '.join(cmd_args)}: {str(e)}")
            return "", "", 1
    
    def extract_commands_from_help(self, help_text: str) -> List[str]:
        """Extract command names from help output"""
        commands = []
        
        # Look for Commands: section
        lines = help_text.split('\n')
        in_commands_section = False
        
        for line in lines:
            if re.match(r'^\s*Commands:', line, re.IGNORECASE):
                in_commands_section = True
                continue
            
            if in_commands_section:
                # Stop at empty line or next section
                if line.strip() == '' or re.match(r'^\w+:', line):
                    break
                
                # Extract command name (first word after whitespace)
                match = re.match(r'^\s+([a-zA-Z][a-zA-Z0-9_-]*)', line)
                if match:
                    commands.append(match.group(1))
        
        return commands
    
    def discover_top_level_commands(self) -> List[str]:
        """Get top-level commands from main help"""
        print("\n🔍 Discovering top-level commands...")
        
        stdout, stderr, returncode = self.run_command(['upid', '--help'])
        
        if returncode != 0 and not stdout and not stderr:
            print("✗ Failed to get help output")
            return []
        
        # Sometimes help goes to stderr
        help_text = stdout or stderr
        commands = self.extract_commands_from_help(help_text)
        
        print(f"✓ Found {len(commands)} top-level commands: {', '.join(commands)}")
        return commands
    
    def discover_subcommands(self, parent_cmd: str, parent_path: List[str] = None) -> Dict:
        """Recursively discover subcommands for a given command"""
        if parent_path is None:
            parent_path = ['upid']
        
        full_path = parent_path + [parent_cmd]
        cmd_path_str = ' '.join(full_path)
        
        print(f"  🔍 Checking: {cmd_path_str}")
        
        stdout, stderr, returncode = self.run_command(full_path + ['--help'])
        
        if returncode != 0 and not stdout and not stderr:
            return {}
        
        help_text = stdout or stderr
        subcommands = self.extract_commands_from_help(help_text)
        
        result = {
            'full_command': cmd_path_str,
            'subcommands': {}
        }
        
        # Add to our global command list
        self.commands.add(cmd_path_str)
        
        # Recursively get subcommands (but limit depth to avoid infinite loops)
        if len(full_path) < 4:  # Limit depth
            for subcmd in subcommands:
                subcmd_result = self.discover_subcommands(subcmd, full_path)
                if subcmd_result:
                    result['subcommands'][subcmd] = subcmd_result
        
        return result
    
    def discover_all_commands(self) -> Dict:
        """Main discovery method"""
        print("🚀 Starting UPID CLI command discovery...")
        
        if not self.check_upid_available():
            return {}
        
        # Get top-level commands
        top_level_commands = self.discover_top_level_commands()
        
        # Known command groups from PRD
        known_groups = ['auth', 'cluster', 'analyze', 'optimize', 'report', 'deploy', 'universal']
        
        # Combine discovered and known commands
        all_groups = list(set(top_level_commands + known_groups))
        
        print(f"\n🔍 Discovering subcommands for {len(all_groups)} groups...")
        
        command_tree = {}
        for group in all_groups:
            print(f"\n📁 Group: {group}")
            tree = self.discover_subcommands(group)
            if tree:
                command_tree[group] = tree
        
        return command_tree
    
    def try_direct_commands(self):
        """Try known commands from PRD that might not show in help"""
        prd_commands = [
            ['upid', 'auth', 'login'],
            ['upid', 'auth', 'logout'],
            ['upid', 'auth', 'status'],
            ['upid', 'auth', 'refresh'],
            ['upid', 'auth', 'configure-cluster'],
            ['upid', 'auth', 'list-clusters'],
            ['upid', 'cluster', 'list'],
            ['upid', 'cluster', 'get'],
            ['upid', 'cluster', 'create'],
            ['upid', 'cluster', 'delete'],
            ['upid', 'analyze', 'resources'],
            ['upid', 'analyze', 'cost'],
            ['upid', 'analyze', 'performance'],
            ['upid', 'optimize', 'resources'],
            ['upid', 'optimize', 'costs'],
            ['upid', 'optimize', 'zero-pod'],
            ['upid', 'optimize', 'auto'],
            ['upid', 'report', 'summary'],
            ['upid', 'report', 'cost'],
            ['upid', 'report', 'performance'],
            ['upid', 'deploy', 'create'],
            ['upid', 'deploy', 'list'],
            ['upid', 'deploy', 'get'],
            ['upid', 'deploy', 'scale'],
            ['upid', 'deploy', 'rollback'],
            ['upid', 'deploy', 'status'],
            ['upid', 'deploy', 'delete'],
            ['upid', 'universal', 'status'],
            ['upid', 'universal', 'analyze'],
            ['upid', 'universal', 'optimize'],
            ['upid', 'universal', 'report'],
            ['upid', 'universal', 'get'],
            ['upid', 'universal', 'apply'],
        ]
        
        print("\n🎯 Verifying PRD-documented commands...")
        
        verified_commands = []
        for cmd in prd_commands:
            cmd_str = ' '.join(cmd)
            stdout, stderr, returncode = self.run_command(cmd + ['--help'])
            
            # Consider command valid if help doesn't explicitly say it's unknown
            if returncode == 0 or ("unknown command" not in stderr.lower() and "command not found" not in stderr.lower()):
                verified_commands.append(cmd_str)
                self.commands.add(cmd_str)
                print(f"  ✓ {cmd_str}")
            else:
                print(f"  ✗ {cmd_str}")
        
        print(f"\n✓ Verified {len(verified_commands)} commands from PRD")
        return verified_commands
    
    def generate_report(self):
        """Generate comprehensive command report"""
        print("\n" + "="*60)
        print("📊 UPID CLI COMMAND INVENTORY REPORT")
        print("="*60)
        
        # Sort commands by length (shorter commands first)
        sorted_commands = sorted(self.commands, key=lambda x: (len(x.split()), x))
        
        print(f"\n🔢 Total Commands Found: {len(sorted_commands)}")
        print(f"🔢 Total Errors: {len(self.errors)}")
        
        # Group by command type
        groups = {}
        for cmd in sorted_commands:
            parts = cmd.split()
            if len(parts) >= 2:
                group = parts[1]  # Second part after 'upid'
                if group not in groups:
                    groups[group] = []
                groups[group].append(cmd)
            else:
                if 'main' not in groups:
                    groups['main'] = []
                groups['main'].append(cmd)
        
        print(f"\n📁 Command Groups: {len(groups)}")
        for group, cmds in sorted(groups.items()):
            print(f"  📁 {group}: {len(cmds)} commands")
            for cmd in sorted(cmds):
                print(f"    • {cmd}")
        
        # Save to files
        self.save_results(sorted_commands, groups)
        
        if self.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in self.errors:
                print(f"    • {error}")
    
    def save_results(self, commands: List[str], groups: Dict):
        """Save results to files"""
        # Save simple command list
        with open('upid_commands.txt', 'w') as f:
            f.write("UPID CLI Commands\n")
            f.write("="*50 + "\n\n")
            for cmd in commands:
                f.write(f"{cmd}\n")
        
        # Save grouped commands
        with open('upid_commands_grouped.txt', 'w') as f:
            f.write("UPID CLI Commands (Grouped)\n")
            f.write("="*50 + "\n\n")
            for group, cmds in sorted(groups.items()):
                f.write(f"{group.upper()} ({len(cmds)} commands)\n")
                f.write("-" * (len(group) + 20) + "\n")
                for cmd in sorted(cmds):
                    f.write(f"  {cmd}\n")
                f.write("\n")
        
        # Save as JSON
        with open('upid_commands.json', 'w') as f:
            json.dump({
                'total_commands': len(commands),
                'groups': groups,
                'all_commands': commands,
                'errors': self.errors
            }, f, indent=2)
        
        print(f"\n💾 Results saved to:")
        print(f"    • upid_commands.txt")
        print(f"    • upid_commands_grouped.txt") 
        print(f"    • upid_commands.json")

def main():
    """Main function"""
    discovery = UPIDCommandDiscovery()
    
    # Discover all commands
    discovery.discover_all_commands()
    
    # Verify PRD commands
    discovery.try_direct_commands()
    
    # Generate report
    discovery.generate_report()

if __name__ == "__main__":
    main()
