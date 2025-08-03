#!/usr/bin/env python3
"""
Test runner script for the White Label Chat SaaS application.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse

def run_command(command, description):
    """Run a command and handle the output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test runner for White Label Chat SaaS")
    parser.add_argument(
        'test_type',
        choices=['all', 'unit', 'integration', 'socket', 'coverage', 'quick'],
        nargs='?',
        default='all',
        help='Type of tests to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Run tests from specific file'
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        base_cmd.append('-v')
    
    # Define test commands
    commands = {
        'all': base_cmd + ['tests/', '--cov=app', '--cov=models', '--cov=services'],
        'unit': base_cmd + ['tests/', '-m', 'unit'],
        'integration': base_cmd + ['tests/', '-m', 'integration'],
        'socket': base_cmd + ['tests/test_socketio.py'],
        'coverage': base_cmd + ['tests/', '--cov=app', '--cov=models', '--cov=services', '--cov-report=html'],
        'quick': base_cmd + ['tests/', '-x', '--tb=short']
    }
    
    # Handle specific file
    if args.file:
        command = base_cmd + [f'tests/{args.file}']
        description = f"tests from {args.file}"
    else:
        command = commands.get(args.test_type, commands['all'])
        description = f"{args.test_type} tests"
    
    # Run the tests
    success = run_command(command, description)
    
    if args.test_type == 'coverage' and success:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    if not success:
        sys.exit(1)
    
    print(f"\n🎉 All {description} passed!")

if __name__ == '__main__':
    main()
