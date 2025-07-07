# 🚀 UPID CLI - Quick Reference Card

## 📱 **Think of UPID like a Smart Phone Manager for Your Clusters!**

---

## 🎯 **Most Common Commands (Start Here!)**

| Command | What It Does | Like This |
|---------|-------------|-----------|
| `upid --help` | Shows all commands | 📋 Menu |
| `upid status` | Checks if UPID is working | 🔋 Battery check |
| `upid demo` | Shows UPID in action | 🎬 Demo video |

---

## 🔐 **Login & Setup**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid auth login` | Log into your account | Like logging into email |
| `upid auth status` | Check if you're logged in | Like checking if you're still logged in |
| `upid auth logout` | Log out | Like clicking logout |

---

## 🏗️ **Manage Your Clusters**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid cluster list` | See all your clusters | Like seeing all your devices |
| `upid cluster get cluster-123` | Get details about one cluster | Like checking phone specs |
| `upid cluster create --name my-cluster` | Create a new cluster | Like buying a new phone |

---

## 📊 **Understand Your Clusters**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid analyze resources cluster-123` | See resource usage | Like checking phone storage |
| `upid analyze cost cluster-123` | See how much it costs | Like checking your phone bill |
| `upid analyze performance cluster-123` | See how well it's working | Like checking phone speed |

---

## 🎯 **Make Things Better (Optimization)**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid optimize resources cluster-123 --dry-run` | See suggestions (safe) | Like getting tips |
| `upid optimize resources cluster-123` | Apply suggestions | Like following the tips |
| `upid optimize costs cluster-123 --dry-run` | See how to save money | Like getting bill tips |
| `upid optimize zero-pod cluster-123` | Turn off unused apps | Like closing unused apps |

---

## 🚀 **Manage Your Apps**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid deploy list cluster-123` | See all your apps | Like seeing all installed apps |
| `upid deploy create cluster-123 --name my-app` | Install a new app | Like installing a new app |
| `upid deploy scale cluster-123 my-app --replicas 5` | Make more copies of an app | Like allowing more users |
| `upid deploy delete cluster-123 my-app` | Remove an app | Like uninstalling an app |

---

## 📈 **Get Reports**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid report summary cluster-123` | Get a complete report | Like getting a report card |
| `upid report cost cluster-123` | Get cost report | Like getting a detailed bill |
| `upid report performance cluster-123` | Get performance report | Like getting a speed test |

---

## 🌍 **Universal Commands (Works with Any Cluster)**

| Command | What It Does | Example |
|---------|-------------|---------|
| `upid universal status` | Check if cluster is healthy | Like checking if phone works |
| `upid universal analyze` | Analyze any cluster | Like checking any phone |
| `upid universal optimize` | Get tips for any cluster | Like getting tips for any phone |
| `upid universal report` | Get report for any cluster | Like getting report for any device |

---

## 🔧 **Output Options**

| Format | Command | What You Get |
|--------|---------|-------------|
| **Table** | `upid cluster list` | Nice colored tables |
| **JSON** | `upid cluster list --format json` | Data for computers |
| **YAML** | `upid cluster list --format yaml` | Configuration data |
| **HTML** | `upid report summary --format html` | Web page |

---

## 🚨 **Safety Flags**

| Flag | What It Does | When to Use |
|------|-------------|-------------|
| `--dry-run` | Shows what would happen (doesn't actually do it) | Always use first! |
| `--force` | "Yes, I'm sure" | When you're absolutely sure |
| `--local` | Works without login (testing only) | For testing |

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

## 💡 **Pro Tips**

1. **Always use `--dry-run` first** - See what will happen before doing it
2. **Use `--help` after any command** - Get help for that specific command
3. **Start with `upid demo`** - See UPID in action
4. **Use `--local` for testing** - Try things without logging in

---

## 🎉 **You're Ready!**

**Start with these 3 commands:**
1. `upid --help` (see everything)
2. `upid status` (check if working)
3. `upid demo` (see it in action)

**Remember**: UPID is your smart assistant for managing Kubernetes clusters! 🚀 