#!/usr/bin/env python3
"""
need.py - Priority-based context management for Taskwarrior
Part of tw-priority-hook project

Usage:
    need              - Show priority report and current context
    need auto         - Set dynamic context based on lowest priority
    need <N>          - Manually set context to show up to priority N
    need off          - Clear priority context
    need span <N>     - Set priority span (how many levels to show)
"""

import sys
import os
import re
import subprocess
import json
from datetime import datetime

# Configuration
HOOK_DIR = os.path.expanduser("~/.task/hooks/priority")
CONFIG_FILE = os.path.join(HOOK_DIR, "need.rc")
CONTEXT_NAME = "need"

# Priority level descriptions
PRIORITY_LABELS = {
    '1': 'Physiological; Air, Water, Food & Shelter',
    '2': 'Personal safety, security, health, financial',
    '3': 'Love & Belonging, Friends & Family',
    '4': 'Esteem, Respect & Recognition',
    '5': 'Self Actualization',
    '6': 'Higher Goals'
}

def get_config_value(key, default=None):
    """Read configuration value from need.rc"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(key + '='):
                    return line.split('=', 1)[1]
    except:
        pass
    return default

def set_config_value(key, value):
    """Set configuration value in need.rc"""
    lines = []
    found = False
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            lines = f.readlines()
        
        # Update existing or add new
        with open(CONFIG_FILE, 'w') as f:
            for line in lines:
                if line.strip().startswith(key + '='):
                    f.write(f"{key}={value}\n")
                    found = True
                else:
                    f.write(line)
            
            if not found:
                f.write(f"\n{key}={value}\n")
        
        return True
    except Exception as e:
        print(f"Error updating config: {e}", file=sys.stderr)
        return False

def get_task_counts():
    """Get count of tasks at each priority level"""
    counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
    
    try:
        # Query for pending tasks grouped by priority
        for level in ['1', '2', '3', '4', '5', '6']:
            result = subprocess.run(
                ['task', f'pri:{level}', 'status:pending', 'count'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                counts[level] = int(result.stdout.strip() or 0)
    except Exception as e:
        print(f"Error getting task counts: {e}", file=sys.stderr)
    
    return counts

def get_lowest_priority():
    """Find the lowest priority level with pending tasks"""
    counts = get_task_counts()
    for level in ['1', '2', '3', '4', '5', '6']:
        if counts[level] > 0:
            return level
    return None

def build_context_filter(min_priority, span, lookahead):
    """
    Build context filter expression
    Shows: min_priority through (min_priority + span - 1)
           plus any tasks due/scheduled within lookahead days
    """
    min_pri = int(min_priority)
    max_pri = min(min_pri + span - 1, 6)
    
    # Build priority filter
    pri_filters = [f"pri:{p}" for p in range(min_pri, max_pri + 1)]
    pri_expr = " or ".join(pri_filters)
    
    # Add due/scheduled lookahead
    due_expr = f"due.before:today+{lookahead}d"
    sched_expr = f"scheduled.before:today+{lookahead}d"
    
    full_filter = f"( {pri_expr} or {due_expr} or {sched_expr} )"
    
    return full_filter

def set_context(filter_expr):
    """Set the 'need' context with given filter"""
    try:
        # Define context (overwrites if exists)
        subprocess.run(
            ['task', 'context', 'define', CONTEXT_NAME, filter_expr],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error defining context: {e}", file=sys.stderr)
        return False

def activate_context():
    """Activate the 'need' context - user runs 'task context need'"""
    print(f"\nContext '{CONTEXT_NAME}' has been defined.")
    print(f"To activate: task context {CONTEXT_NAME}")
    print(f"To deactivate: task context none")

def clear_context():
    """Delete the 'need' context definition"""
    try:
        # Delete context definition
        subprocess.run(
            ['task', 'context', 'delete', CONTEXT_NAME],
            check=True,
            capture_output=True
        )
        print(f"Context '{CONTEXT_NAME}' deleted")
        print("If active, run: task context none")
        return True
    except subprocess.CalledProcessError:
        # Context doesn't exist, that's fine
        return True

def get_current_context():
    """Get currently active context filter"""
    try:
        result = subprocess.run(
            ['task', '_get', f'rc.context.{CONTEXT_NAME}'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    return None

def show_report():
    """Display priority pyramid report"""
    counts = get_task_counts()
    current_filter = get_current_context()
    
    print("\nPriority Hierarchy Status")
    print("=" * 70)
    print()
    
    # Determine which level is active
    active_level = None
    if current_filter:
        for level in ['1', '2', '3', '4', '5', '6']:
            if f'pri:{level}' in current_filter:
                active_level = level
                break
    
    # Draw pyramid
    pyramid = [
        ('6', 'Higher Goals', 50),
        ('5', 'Self Actualization', 45),
        ('4', 'Esteem, Respect & Recognition', 38),
        ('3', 'Love & Belonging, Friends & Family', 32),
        ('2', 'Personal safety, security, health, financial', 20),
        ('1', 'Physiological; Air, Water, Food & Shelter', 8)
    ]
    
    for level, label, indent in pyramid:
        prefix = ' -->' if level == active_level else '    '
        count_str = f"({counts[level]})"
        padding = ' ' * indent
        print(f"{prefix}{level}  {padding}{label:<45} {count_str:>5}")
    
    print()
    
    # Show current context status
    if current_filter:
        print(f"Active context: {CONTEXT_NAME}")
        print(f"Filter: {current_filter}")
    else:
        print("No priority context active")
    
    print()

def cmd_auto():
    """Set automatic context based on lowest priority"""
    span = int(get_config_value('priority.span', '2'))
    lookahead = int(get_config_value('priority.lookahead', '2'))
    
    lowest = get_lowest_priority()
    if not lowest:
        print("No pending tasks found")
        clear_context()
        return 0
    
    filter_expr = build_context_filter(lowest, span, lookahead)
    
    if set_context(filter_expr):
        print(f"Context defined: priority {lowest}-{int(lowest) + span - 1} + lookahead")
        print(f"Filter: {filter_expr}")
        activate_context()
        return 0
    else:
        return 1

def cmd_manual(level):
    """Set manual context up to specified priority level"""
    if level not in ['1', '2', '3', '4', '5', '6']:
        print(f"Invalid priority level: {level}", file=sys.stderr)
        return 1
    
    lookahead = int(get_config_value('priority.lookahead', '2'))
    
    # Manual mode: show from 1 to specified level
    filter_expr = build_context_filter('1', int(level), lookahead)
    
    if set_context(filter_expr):
        print(f"Context defined: priority 1-{level} + lookahead")
        print(f"Filter: {filter_expr}")
        activate_context()
        return 0
    else:
        return 1

def cmd_off():
    """Clear priority context"""
    if clear_context():
        return 0
    else:
        return 1

def cmd_span(new_span):
    """Set priority span value"""
    try:
        span = int(new_span)
        if span < 1 or span > 6:
            raise ValueError
        
        if set_config_value('priority.span', str(span)):
            print(f"Priority span set to {span}")
            print("Run 'need auto' to apply changes")
            return 0
        else:
            return 1
    except ValueError:
        print(f"Invalid span value: {new_span}", file=sys.stderr)
        return 1

def main():
    """Main entry point"""
    args = sys.argv[1:]
    
    # No arguments: show report
    if not args:
        show_report()
        return 0
    
    # Parse command
    cmd = args[0].lower()
    
    if cmd == 'auto':
        return cmd_auto()
    elif cmd == 'off':
        return cmd_off()
    elif cmd == 'span':
        if len(args) < 2:
            print("Usage: need span <N>", file=sys.stderr)
            return 1
        return cmd_span(args[1])
    elif cmd in ['1', '2', '3', '4', '5', '6']:
        return cmd_manual(cmd)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        return 1

if __name__ == '__main__':
    sys.exit(main())
