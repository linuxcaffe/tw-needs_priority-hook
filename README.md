# tw-priority-hook

Priority-based task filtering for Taskwarrior based on Maslow's hierarchy of needs.

## Overview

Automatically assigns and filters tasks based on a 6-level priority hierarchy:

1. **Physiological** - Air, water, food, shelter, medical
2. **Safety** - Security, health, financial stability  
3. **Love & Belonging** - Friends, family, relationships
4. **Esteem** - Respect, recognition, achievements
5. **Self-Actualization** - Personal growth, creativity
6. **Higher Goals** - Life purpose, legacy

## Features

- **Auto-assignment**: Tasks automatically get priority based on tags/projects
- **Dynamic context**: Shows only most important tasks (configurable span)
- **Smart lookahead**: Always shows upcoming due/scheduled tasks
- **Visual report**: Pyramid display of task distribution
- **Urgency integration**: Higher priorities boost urgency scores

## Installation

### First-Time Setup

1. **Migrate existing priorities (if needed):**
   ```bash
   # Preview migration from H/M/L to numeric
   python3 ~/.task/hooks/priority/migrate_priority.py --dry-run
   
   # Perform migration (default: H->2, M->4, L->5)
   python3 ~/.task/hooks/priority/migrate_priority.py
   
   # Custom mapping if desired
   python3 ~/.task/hooks/priority/migrate_priority.py --mapping H:1,M:3,L:6
   ```

2. **Copy files:**
   ```bash
   # Project is in ~/.task/hooks/priority/
   ```

3. **Create symlinks:**
   ```bash
   ln -s ~/.task/hooks/priority/on-add_priority.py ~/.task/hooks/
   ln -s ~/.task/hooks/priority/on-modify_priority.py ~/.task/hooks/
   ln -s ~/.task/hooks/priority/need.py ~/.task/scripts/need
   ```

4. **Include configuration:**
   Add to `~/.taskrc`:
   ```
   include ~/.task/hooks/priority/need.rc
   ```

4. **Add scripts to PATH** (optional):
   ```bash
   export PATH="$PATH:$HOME/.task/scripts"
   ```

## Configuration

Edit `need.rc` to customize auto-assignment rules:

```
# Automatically assign pri:1 to tasks with these attributes
priority.1.auto=+meds,+oxygen,desc.has:hospital,proj:medical

# Adjust context span (how many levels to show above minimum)
priority.span=2

# Due/scheduled lookahead in days
priority.lookahead=2
```

### Auto-Assignment Rules

Rules are checked in priority order (1-6). First match wins.

Supported filters:
- `+tag` - Has tag
- `proj:name` - Exact project match
- `proj.has:name` - Project contains text
- `desc.has:text` - Description contains text

## Usage

### Context Activation

The `need` script defines the context filter, but you control activation:

```bash
# Define auto-context
need auto

# Activate the context
task context need

# Work with filtered tasks
task list

# Deactivate when you want to see everything
task context none
```

### Companion Script Commands

```bash
# Show priority report and current context
need

# Enable automatic context (shows lowest priority + span levels)
need auto

# Manually show tasks up to priority level N
need 3

# Disable priority filtering
need off

# Adjust span (how many levels above minimum to show)
need span 3
```

### How Auto-Context Works

With `priority.span=2` and `priority.lookahead=2`:

1. **You have pri:1 tasks:**
   - Filter: `pri:1 or pri:2 or due.before:today+2d or sched.before:today+2d`
   - Shows: Priority 1-2 tasks + anything due/scheduled soon

2. **All pri:1 tasks completed:**
   - Filter auto-adjusts to: `pri:2 or pri:3 or due.before:today+2d or sched.before:today+2d`
   - Shows: Priority 2-3 tasks + upcoming items

3. **Manual override:**
   ```bash
   need 4  # Show everything up to pri:4
   ```

### Example Workflow

```bash
# Add task with medical tag - auto-assigned pri:1
task add Get prescription refilled +meds

# Add task with bill tag - auto-assigned pri:2  
task add Pay electricity bill +bills

# Define auto-context based on lowest priority
need auto

# Activate the context
task context need

# View filtered list (only pri:1-2 + upcoming)
task list

# Check priority distribution and current filter
need

# Complete high-priority tasks, context auto-adjusts
task 1 done

# Redefine context to pick up new lowest priority
need auto

# Disable filtering to see everything
task context none

# Or just deactivate temporarily
task context none
task list   # See all tasks
task context need  # Back to filtered view
```

## Priority Report

```
Priority Hierarchy Status
======================================================================

    6              Higher Goals                          (2)
    5            Self Actualization                      (3)
    4       Esteem, Respect & Recognition               (15)
    3      Love & Belonging, Friends & Family           (24)
 -->2   Personal safety, security, health, financial    (8)
    1     Physiological; Air, Water, Food & Shelter     (2)

Active context: need
Filter: ( pri:1 or pri:2 or due.before:today+2d or scheduled.before:today+2d )
```

## Manual Priority Assignment

You can always manually set or override priority:

```bash
task add "Critical project deadline" pri:1
task 42 mod pri:3
```

## Integration with Urgency

Priority levels boost urgency scores (configured in `need.rc`):
- pri:1 = +10.0 urgency
- pri:2 = +8.0 urgency
- pri:3 = +6.0 urgency
- pri:4 = +4.0 urgency
- pri:5 = +2.0 urgency
- pri:6 = +0.0 urgency

## Files

```
~/.task/hooks/priority/
├── need.rc                # Configuration and auto-rules
├── need.py                # Companion script
├── on-add_priority.py     # Auto-assignment hook
├── on-modify_priority.py  # Validation/enforcement hook
├── migrate_priority.py    # Migration tool for H/M/L
├── logs/                  # Hook execution logs
│   ├── on-add.log
│   └── on-modify.log
├── CHANGES.txt            # Version history
├── README.md              # This file
└── VERSION                # Current version
```

## Philosophy

Based on the original [tw-needs-hook](https://github.com/linuxcaffe/tw-needs-hook) by linuxcaffe.

The priority hierarchy helps prevent distraction by higher-level tasks when lower-level needs aren't met. You can track everything, but only focus on what matters most right now.

**Key insight:** You won't achieve self-actualization if you're behind on bills. The system enforces this reality while still letting you plan for bigger goals.

## Compatibility

- Requires Taskwarrior 2.6.2
- Python 3.6+
- For Taskwarrior 3.x support, submit a pull request

## Version

Current version: 0.1.0

See `CHANGES.txt` for version history.
