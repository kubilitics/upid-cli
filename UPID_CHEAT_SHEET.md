# 🚀 UPID CLI - Super Simple Cheat Sheet

## 🎯 **Start Here (3 Most Important Commands)**

```bash
upid --help     # See all commands (like a menu)
upid status     # Check if UPID is working
upid demo       # See UPID in action
```

---

## 📱 **Think of UPID like Managing Your Phone**

| What You Want to Do | UPID Command | Like This |
|---------------------|--------------|-----------|
| **See all your devices** | `upid cluster list` | Like seeing all your phones/tablets |
| **Check if device is working** | `upid universal status` | Like checking if phone has battery |
| **See how much storage used** | `upid analyze resources cluster-123` | Like checking phone storage |
| **See how much it costs** | `upid analyze cost cluster-123` | Like checking phone bill |
| **Get tips to save money** | `upid optimize costs cluster-123 --dry-run` | Like getting bill-saving tips |
| **Actually save money** | `upid optimize costs cluster-123` | Like switching to cheaper plan |
| **Get a report** | `upid report summary cluster-123` | Like getting a report card |

---

## 🔐 **Login Commands**

```bash
upid auth login --email your-email@example.com    # Log in
upid auth status                                  # Check if logged in
upid auth logout                                  # Log out
```

---

## 🏗️ **Cluster Commands**

```bash
upid cluster list                                # See all clusters
upid cluster get cluster-123                     # Get details about one cluster
upid cluster create --name my-cluster            # Create new cluster
upid cluster delete cluster-123 --force          # Delete cluster
```

---

## 📊 **Analysis Commands**

```bash
upid analyze resources cluster-123               # See resource usage
upid analyze resources cluster-123 --detailed    # Get detailed info
upid analyze cost cluster-123 --period 30d      # See costs for 30 days
upid analyze performance cluster-123             # See performance
```

---

## 🎯 **Optimization Commands**

```bash
# SAFE - See suggestions first
upid optimize resources cluster-123 --dry-run     # See what would happen
upid optimize costs cluster-123 --dry-run        # See money-saving tips

# ACTUAL - Apply the changes
upid optimize resources cluster-123               # Apply resource changes
upid optimize costs cluster-123                  # Apply cost savings
upid optimize zero-pod cluster-123               # Turn off unused apps
```

---

## 🚀 **Deployment Commands**

```bash
upid deploy list cluster-123                     # See all apps
upid deploy create cluster-123 --name my-app     # Install new app
upid deploy scale cluster-123 my-app --replicas 5 # Make more copies
upid deploy delete cluster-123 my-app            # Remove app
```

---

## 📈 **Report Commands**

```bash
upid report summary cluster-123 --period 30d     # Get monthly report
upid report cost cluster-123 --format html       # Get cost report for browser
upid report performance cluster-123 --format json # Get performance data
```

---

## 🌍 **Universal Commands (Works with Any Cluster)**

```bash
upid universal status                            # Check if cluster is healthy
upid universal analyze                           # Analyze any cluster
upid universal optimize                          # Get tips for any cluster
upid universal report                            # Get report for any cluster
```

---

## 🔧 **Output Formats**

```bash
upid cluster list                                # Nice table (default)
upid cluster list --format json                  # Data for computers
upid cluster list --format yaml                  # Configuration format
upid report summary --format html --output report.html  # Web page
```

---

## 🚨 **Safety Flags (IMPORTANT!)**

```bash
--dry-run    # Show what would happen (DON'T actually do it)
--force       # "Yes, I'm sure" (be careful!)
--local       # Work without login (for testing)
```

---

## 💡 **Pro Tips**

1. **Always use `--dry-run` first** - See what will happen before doing it
2. **Use `--help` after any command** - Get help for that command
3. **Start with `upid demo`** - See UPID in action
4. **Use `--local` for testing** - Try things without logging in

---

## 🎯 **Real Examples**

### **Daily Check**
```bash
upid status                    # Is everything working?
upid cluster list              # What clusters do I have?
upid analyze resources cluster-123  # How are they doing?
```

### **Save Money**
```bash
upid analyze cost cluster-123 --period 30d    # How much did I spend?
upid optimize costs cluster-123 --dry-run      # How can I save money?
upid optimize costs cluster-123                # Actually save money
```

### **Get Reports**
```bash
upid report summary cluster-123 --period 30d  # Monthly report
upid report cost cluster-123 --format html     # Cost report for browser
```

---

## 🎉 **You're Ready!**

**Start with these 3 commands:**
1. `upid --help` (see everything)
2. `upid status` (check if working)
3. `upid demo` (see it in action)

**Remember**: UPID is your smart assistant for managing Kubernetes clusters! 🚀 