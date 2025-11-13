# Nisa Workspace Fix Guide

This guide provides permanent solutions for fixing workspace issues in ERPNext custom apps.

## The Problem

When you modify workspace JSON files, the changes don't automatically sync to the database. This causes `AttributeError` and other issues when loading the workspace.

**Common Error:**
```
AttributeError: 'Workspace' object has no attribute 'onboarding_list'
```

## Permanent Solution - 3 Methods

### Method 1: Automatic Sync (Recommended)

We've added automatic workspace syncing to the app. After pulling the latest code:

```bash
cd /path/to/frappe-bench

# Pull latest changes
cd apps/nisa
git pull

# Go back to bench root
cd ../..

# Run these commands in order
bench --site your-site.local migrate
bench --site your-site.local clear-cache
bench build
bench restart
```

The `after_install` hook and fixtures configuration will automatically sync the workspace.

---

### Method 2: Manual Sync via Bench Console

If automatic sync doesn't work, use this manual method:

```bash
cd /path/to/frappe-bench

# Open bench console
bench --site your-site.local console

# In the console, run:
from nisa.utils import sync_workspace
sync_workspace()
exit()

# Clear cache and rebuild
bench --site your-site.local clear-cache
bench build
bench restart
```

This will:
1. Delete the old workspace from database
2. Create a new workspace from the JSON file
3. Commit the changes

---

### Method 3: Manual Database Deletion

If both above methods fail, manually delete and recreate:

```bash
cd /path/to/frappe-bench

# Open bench console
bench --site your-site.local console

# In the console, run:
import frappe
frappe.delete_doc('Workspace', 'Nisa', force=True)
frappe.db.commit()
exit()

# Now migrate to recreate
bench --site your-site.local migrate
bench --site your-site.local clear-cache
bench build
bench restart
```

---

## Verification

After applying any of the above methods, verify the workspace works:

1. Open ERPNext in your browser
2. Clear browser cache (Ctrl + F5)
3. Look for "Nisa" in the sidebar
4. Click it - it should load without errors
5. You should see:
   - 4 colored shortcuts at top
   - 4 cards: Production Tracking, Reports, Quick Access, Masters & Setup
   - All links working

---

## For Future Workspace Changes

Whenever you modify the workspace JSON file (`nisa/nisa/workspace/nisa/nisa.json`), follow these steps:

### Option A: Quick Sync Script
```bash
cd /path/to/frappe-bench

# Create a quick sync script
cat > sync_nisa_workspace.sh << 'EOF'
#!/bin/bash
bench --site your-site.local console << 'PYTHON'
from nisa.utils import sync_workspace
sync_workspace()
PYTHON
bench --site your-site.local clear-cache
bench build
echo "✓ Nisa workspace synced!"
EOF

chmod +x sync_nisa_workspace.sh

# Run it anytime you change the workspace
./sync_nisa_workspace.sh
```

### Option B: Manual Steps
```bash
# After editing nisa.json
bench --site your-site.local console
# Run: from nisa.utils import sync_workspace; sync_workspace()

bench --site your-site.local clear-cache
bench build
```

---

## Understanding the Issue

### Why This Happens

1. **JSON files are templates** - They define the structure but don't directly create database records
2. **Migration creates records** - During migration, Frappe reads JSON files and creates/updates database records
3. **Cache can be stale** - ERPNext caches workspace data, so changes need cache clearing

### Required Fields for Workspace

All workspace JSON files must have these fields:
```json
{
  "doctype": "Workspace",
  "name": "Your Workspace Name",
  "onboarding": "",
  "onboarding_list": [],
  "custom_blocks": [],
  "cards": [],
  "shortcuts": [],
  ...
}
```

Missing any of these causes AttributeError.

---

## Troubleshooting

### Issue: Workspace still shows old data

**Solution:**
```bash
# Clear all caches
bench --site your-site.local clear-cache
bench --site your-site.local clear-website-cache

# Hard reload in browser (Ctrl + Shift + R)
```

### Issue: "Workspace does not exist" error

**Solution:**
```bash
# Check if workspace exists
bench --site your-site.local console
# Run: frappe.db.exists('Workspace', 'Nisa')

# If False, run migration
bench --site your-site.local migrate
```

### Issue: Changes not reflecting after migrate

**Solution:**
```bash
# Delete and recreate
bench --site your-site.local console
# Run:
# from nisa.utils import delete_workspace, sync_workspace
# delete_workspace()
# sync_workspace()
```

### Issue: Multiple workspace entries

**Solution:**
```bash
bench --site your-site.local console

# In console:
import frappe
workspaces = frappe.get_all('Workspace', filters={'name': 'Nisa'})
print(f"Found {len(workspaces)} workspace(s)")

# Delete all and recreate
for ws in workspaces:
    frappe.delete_doc('Workspace', ws.name, force=True)
frappe.db.commit()

# Now sync
from nisa.utils import sync_workspace
sync_workspace()
```

---

## Prevention Tips

1. **Always test in dev first** - Test workspace changes in development before production
2. **Use sync utility** - Don't manually edit workspace in UI and JSON file
3. **Clear cache after changes** - Always clear cache after workspace modifications
4. **Version control** - Commit workspace JSON changes to git
5. **Document changes** - Keep notes of what you changed in workspace

---

## Quick Reference Commands

```bash
# Full reset (nuclear option)
bench --site your-site.local console << 'PYTHON'
import frappe
try:
    frappe.delete_doc('Workspace', 'Nisa', force=True)
    frappe.db.commit()
except:
    pass
from nisa.utils import sync_workspace
sync_workspace()
PYTHON
bench --site your-site.local clear-cache
bench build
bench restart

# Verify workspace exists
bench --site your-site.local console << 'PYTHON'
import frappe
print(frappe.db.exists('Workspace', 'Nisa'))
PYTHON

# List all workspaces
bench --site your-site.local console << 'PYTHON'
import frappe
workspaces = frappe.get_all('Workspace', fields=['name', 'label'])
for ws in workspaces:
    print(f"{ws.name} - {ws.label}")
PYTHON
```

---

## Need Help?

If you're still experiencing issues:

1. Check ERPNext logs: `bench --site your-site.local logs`
2. Check browser console for JavaScript errors
3. Verify file permissions: `ls -la apps/nisa/nisa/nisa/workspace/`
4. Check Frappe version compatibility
5. Try in a new private/incognito browser window

---

## Summary

**Quick Fix Command (Run this first):**
```bash
cd /path/to/frappe-bench
bench --site your-site.local console << 'PYTHON'
from nisa.utils import sync_workspace
sync_workspace()
PYTHON
bench --site your-site.local clear-cache
bench build
```

This should resolve 95% of workspace issues!
