#!/usr/bin/env python3
"""
Simple script to generate visual architecture diagrams for UPID CLI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from architecture_visualizer import ArchitectureVisualizer

def main():
    """Generate visual architecture diagrams"""
    print("🎨 UPID CLI Architecture Visualizer")
    print("=" * 50)
    
    visualizer = ArchitectureVisualizer()
    
    # Update README with visual diagrams
    print("\n📝 Updating README.md with visual diagrams...")
    visualizer.update_readme_with_visuals()
    
    # Create comprehensive visual architecture file
    print("\n📄 Creating comprehensive visual architecture file...")
    visualizer.create_visual_architecture_file("ARCHITECTURE_VISUAL.md")
    
    print("\n✅ Successfully generated visual architecture diagrams!")
    print("\n📁 Files created/updated:")
    print("   - README.md (updated with Mermaid diagrams)")
    print("   - ARCHITECTURE_VISUAL.md (comprehensive visual guide)")
    print("\n🌐 View the diagrams:")
    print("   - GitHub will automatically render Mermaid diagrams")
    print("   - Open README.md in GitHub to see the visual architecture")
    print("   - Check ARCHITECTURE_VISUAL.md for detailed diagrams")

if __name__ == "__main__":
    main() 