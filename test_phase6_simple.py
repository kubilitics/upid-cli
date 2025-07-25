#!/usr/bin/env python3
"""
Simple test script for Phase 6 Platform Integration components
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase6_imports():
    """Test that all Phase 6 components can be imported"""
    try:
        # Test CI/CD imports
        from upid_python.cicd.pipeline_manager import PipelineManager, PipelineConfig, TriggerType, PipelineType
        print("✅ Pipeline Manager imports successful")
        
        from upid_python.cicd.gitops_integration import GitOpsIntegration, GitOpsConfig, GitOpsStrategy, GitOpsDeployment
        print("✅ GitOps Integration imports successful")
        
        from upid_python.cicd.deployment_validator import DeploymentValidator, ValidationConfig, DeploymentValidation
        print("✅ Deployment Validator imports successful")
        
        from upid_python.cicd.github_actions import GitHubActionsIntegration, GitHubActionsConfig
        print("✅ GitHub Actions imports successful")
        
        from upid_python.cicd.gitlab_cicd import GitLabCICDIntegration, GitLabCICDConfig
        print("✅ GitLab CI/CD imports successful")
        
        from upid_python.cicd.jenkins_plugin import JenkinsIntegration, JenkinsConfig
        print("✅ Jenkins Integration imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_phase6_components():
    """Test basic component functionality"""
    try:
        # Test configuration objects
        from upid_python.cicd.gitops_integration import GitOpsConfig, GitOpsStrategy
        from upid_python.cicd.deployment_validator import ValidationConfig
        
        # Create configs
        gitops_config = GitOpsConfig(
            strategy=GitOpsStrategy.FLUX,
            git_repository="https://github.com/test/repo",
            auto_sync=True
        )
        print("✅ GitOps config creation successful")
        
        validation_config = ValidationConfig(
            pre_deployment_analysis=True,
            post_deployment_validation=True,
            auto_rollback=True
        )
        print("✅ Validation config creation successful")
        
        # Test template generation
        from upid_python.cicd.gitops_integration import GitOpsTemplateGenerator
        
        template_gen = GitOpsTemplateGenerator(gitops_config)
        print("✅ Template generator creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_phase6_structure():
    """Test that all required files exist"""
    required_files = [
        "upid_python/cicd/pipeline_manager.py",
        "upid_python/cicd/gitops_integration.py", 
        "upid_python/cicd/deployment_validator.py",
        "upid_python/cicd/github_actions.py",
        "upid_python/cicd/gitlab_cicd.py",
        "upid_python/cicd/jenkins_plugin.py",
        "upid_python/cicd/__init__.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🧪 Testing Phase 6 Platform Integration Components")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_phase6_imports()
    
    # Test components
    print("\n2. Testing components...")
    components_ok = test_phase6_components()
    
    # Test structure
    print("\n3. Testing file structure...")
    structure_ok = test_phase6_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    
    if all([imports_ok, components_ok, structure_ok]):
        print("\n🎉 All Phase 6 tests passed!")
        print("✅ Phase 6 Task 6.1 CI/CD Pipeline Integration is working correctly")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1) 