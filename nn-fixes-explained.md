# nn-fixed - Changes Summary

## What Was Fixed

### 1. Correct Configuration Paths
**BEFORE (nn-before, lines 30-31):**
```python
CONFIG_DIR = os.path.expanduser("~/.task/config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "need.rc")
```

**AFTER (nn-after, lines 105-106) - WRONG:**
```python
HOOK_DIR = os.path.expanduser("~/.task/hooks")
CONFIG_FILE = os.path.join(HOOK_DIR, "need.rc")
```

**FIXED (nn-fixed, lines 29-30) - CORRECT:**
```python
CONFIG_DIR = os.path.expanduser("~/.task/config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "need.rc")
```

**Why this matters:** Config files belong in `~/.task/config/`, not in `~/.task/hooks/`. 
The make-awesome.sh --debug routine was incorrectly changing paths.

---

### 2. Import Block Organization
**BEFORE (nn-before, lines 24-27):**
```python
import sys
import os
import subprocess
import json
```
**All imports together at the top - GOOD**

**AFTER (nn-after) - BROKEN:**
```python
# Lines 28-31: Some imports
import os
import sys
from pathlib import Path
from datetime import datetime

# Lines 33-94: 65 lines of debug boilerplate code

# Lines 96-97: Rest of imports
import subprocess
import json
```
**Import block split by 65 lines of code - BAD**

**FIXED (nn-fixed, lines 24-27) - CORRECT:**
```python
import sys
import os
import subprocess
import json
```
**All imports together at the top - GOOD**

**Why this matters:** Python best practice is to keep all imports at the top of the file.
The debug boilerplate should come AFTER all imports are declared.

---

### 3. Debug Infrastructure
**BEFORE (nn-before, lines 33-39):**
```python
# Debug mode - set to 1 to enable debug output
DEBUG = 1

def debug_print(msg):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(f"DEBUG: {msg}")
```
**Simple, working debug system - GOOD**

**AFTER (nn-after) - BROKEN:**
```python
# Lines 34-94: New debug infrastructure with debug_log()
DEBUG_MODE = 0  # Set to 1 to enable debug output
# ... 60 lines of new boilerplate ...

# Lines 108-114: Original debug system (now disabled)
DEBUG = 0  # Changed from 1 to 0!

def debug_print(msg):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(f"DEBUG: {msg}")
```
**Two debug systems, original one disabled - BAD**

**FIXED (nn-fixed, lines 32-38) - CORRECT:**
```python
# Debug mode - set to 1 to enable debug output
DEBUG = 1

def debug_print(msg):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(f"DEBUG: {msg}")
```
**Original working debug system preserved - GOOD**

**Why this matters:** The file already had a working debug system. The --debug routine
should have enhanced it, not disabled it. Now there's confusing duplication.

---

## Summary of Issues with make-awesome.sh --debug

The current --debug routine has these problems:

1. **Path Mutation**: Changes existing path variables it shouldn't touch
2. **Import Splitting**: Inserts code between import statements
3. **Debug Duplication**: Adds new debug code without recognizing existing patterns
4. **Disables Existing Debug**: Sets existing DEBUG variables to 0

## Recommended Fix Strategy

The improved make-awesome.sh --debug should:

1. **Detect existing debug patterns** (DEBUG variables, debug functions)
2. **If found**: Enhance rather than replace
   - Keep existing function names
   - Add TW_DEBUG support
   - Add file logging capability
   - Keep original DEBUG value
3. **If not found**: Add full boilerplate
4. **Never modify** existing path constants
5. **Keep all imports together** at the top

This will be implemented in the improved make-awesome.sh.
