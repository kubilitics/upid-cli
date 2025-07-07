# 🚀 UPID CLI - Complete Commands Guide

**Think of UPID as your smart assistant for managing Kubernetes clusters!** 🎯

---

## 📋 **Quick Start - Your First Commands**

### **1. Check if UPID is working**
```bash
upid --help
```
**What it does**: Shows you all available commands (like a menu)
**Example**: Just like asking "What can you do?" to a friend

### **2. See UPID's status**
```bash
upid status
```
**What it does**: Shows if UPID is connected and ready to work
**Example**: Like checking if your phone has battery and signal

---

## 🔐 **Authentication Commands (Login/Logout)**

### **Login to your account**
```bash
upid auth login --email your-email@example.com
```
**What it does**: Logs you into your UPID account (like logging into your email)
**Example**: 
- You'll be asked for your password
- UPID will remember you're logged in
- You can now use all features

### **Check if you're logged in**
```bash
upid auth status
```
**What it does**: Shows if you're currently logged in
**Example**: Like checking if you're still logged into your email

### **Logout**
```bash
upid auth logout
```
**What it does**: Logs you out of your account
**Example**: Like clicking "Logout" on a website

---

## 🏗️ **Cluster Management Commands**

### **See all your clusters**
```bash
upid cluster list
```
**What it does**: Shows all your Kubernetes clusters (like a list of your computers)
**Example**: Like seeing all your phones, tablets, and computers

### **Get details about one cluster**
```bash
upid cluster get cluster-123
```
**What it does**: Shows detailed information about a specific cluster
**Example**: Like checking the specs of your phone (RAM, storage, etc.)

### **Create a new cluster**
```bash
upid cluster create --name my-cluster --region us-west-2 --platform aws
```
**What it does**: Creates a new Kubernetes cluster (like setting up a new computer)
**Example**: Like buying and setting up a new phone

### **Delete a cluster**
```bash
upid cluster delete cluster-123 --force
```
**What it does**: Removes a cluster (like selling your old phone)
**Example**: The `--force` means "Yes, I'm sure I want to delete this"

---

## 📊 **Analysis Commands (Understanding Your Clusters)**

### **Analyze cluster resources**
```bash
upid analyze resources cluster-123
```
**What it does**: Shows how much CPU, memory, and storage your cluster is using
**Example**: Like checking how much battery, storage, and RAM your phone is using

### **Get detailed resource analysis**
```bash
upid analyze resources cluster-123 --detailed
```
**What it does**: Shows very detailed information about resource usage
**Example**: Like getting a detailed health report for your phone

### **Analyze costs**
```bash
upid analyze cost cluster-123 --period 30d
```
**What it does**: Shows how much money your cluster is costing you
**Example**: Like checking your phone bill to see how much you spent

### **Analyze performance**
```bash
upid analyze performance cluster-123
```
**What it does**: Shows how well your cluster is performing
**Example**: Like checking if your phone is running fast or slow

---

## 🎯 **Optimization Commands (Making Things Better)**

### **Get resource optimization suggestions**
```bash
upid optimize resources cluster-123 --dry-run
```
**What it does**: Shows suggestions to make your cluster use resources better
**Example**: Like getting tips to make your phone battery last longer
**Note**: `--dry-run` means "just show me what you would do, don't actually do it"

### **Apply resource optimization**
```bash
upid optimize resources cluster-123
```
**What it does**: Actually applies the optimization suggestions
**Example**: Like actually following the tips to save battery

### **Get cost optimization suggestions**
```bash
upid optimize costs cluster-123 --dry-run
```
**What it does**: Shows how to save money on your cluster
**Example**: Like getting tips to reduce your phone bill

### **Apply cost optimization**
```bash
upid optimize costs cluster-123
```
**What it does**: Actually applies the cost-saving changes
**Example**: Like actually switching to a cheaper phone plan

### **Scale down idle pods (Zero-pod scaling)**
```bash
upid optimize zero-pod cluster-123 --namespace default
```
**What it does**: Turns off apps that aren't being used (saves money)
**Example**: Like turning off apps on your phone when you're not using them

### **Set up automatic optimization**
```bash
upid optimize auto cluster-123 --schedule '0 2 * * *'
```
**What it does**: Makes UPID automatically optimize your cluster every day at 2 AM
**Example**: Like setting your phone to automatically close unused apps every night

---

## 🚀 **Deployment Commands (Managing Your Apps)**

### **Create a new app deployment**
```bash
upid deploy create cluster-123 --name my-app --image nginx:latest --replicas 3
```
**What it does**: Deploys a new app to your cluster
**Example**: Like installing a new app on your phone

### **See all your app deployments**
```bash
upid deploy list cluster-123
```
**What it does**: Shows all apps running on your cluster
**Example**: Like seeing all apps installed on your phone

### **Scale an app (make more or fewer copies)**
```bash
upid deploy scale cluster-123 my-app --replicas 5
```
**What it does**: Changes how many copies of an app are running
**Example**: Like deciding how many people can use an app at the same time

### **Delete an app deployment**
```bash
upid deploy delete cluster-123 my-app
```
**What it does**: Removes an app from your cluster
**Example**: Like uninstalling an app from your phone

---

## 📈 **Reporting Commands (Getting Information)**

### **Get a summary report**
```bash
upid report summary cluster-123 --period 30d
```
**What it does**: Shows a summary of everything about your cluster
**Example**: Like getting a report card for your cluster

### **Get a cost report**
```bash
upid report cost cluster-123 --format json --output cost-report.json
```
**What it does**: Creates a detailed report about costs
**Example**: Like getting a detailed phone bill

### **Get a performance report**
```bash
upid report performance cluster-123 --format html --output perf-report.html
```
**What it does**: Creates a report about how well your cluster is performing
**Example**: Like getting a performance report for your phone

---

## 🌍 **Universal Commands (Works with Any Cluster)**

### **Check cluster status**
```bash
upid universal status
```
**What it does**: Shows if your cluster is healthy and working
**Example**: Like checking if your phone is working properly

### **Analyze any cluster**
```bash
upid universal analyze
```
**What it does**: Analyzes any Kubernetes cluster (no setup needed)
**Example**: Like being able to check any phone's health

### **Get optimization recommendations**
```bash
upid universal optimize
```
**What it does**: Gives suggestions to improve any cluster
**Example**: Like getting tips for any phone to work better

### **Generate a comprehensive report**
```bash
upid universal report
```
**What it does**: Creates a complete report for any cluster
**Example**: Like getting a complete health check for any device

---

## 🎬 **Demo Commands (See UPID in Action)**

### **Run the demo**
```bash
upid demo
```
**What it does**: Shows you a demonstration of UPID's features
**Example**: Like watching a tutorial video

---

## ⚙️ **Configuration Commands**

### **Initialize UPID**
```bash
upid init
```
**What it does**: Sets up UPID for the first time
**Example**: Like setting up a new phone for the first time

---

## 📝 **Output Formats**

UPID can show information in different ways:

### **Table format (default)**
```bash
upid cluster list
```
**What it shows**: Nice tables with colors and borders

### **JSON format (for computers)**
```bash
upid cluster list --format json
```
**What it shows**: Data that other programs can read

### **YAML format (for configuration)**
```bash
upid cluster list --format yaml
```
**What it shows**: Data in a readable configuration format

### **HTML format (for web browsers)**
```bash
upid report summary cluster-123 --format html --output report.html
```
**What it shows**: A web page you can open in your browser

---

## 🔧 **Advanced Options**

### **Use a specific config file**
```bash
upid --config my-config.yaml cluster list
```
**What it does**: Uses a specific configuration file
**Example**: Like using a specific settings file

### **Enable local mode (no login needed)**
```bash
upid --local cluster list
```
**What it does**: Works without logging in (for testing)
**Example**: Like using your phone in airplane mode

### **Enable verbose output (more details)**
```bash
upid --verbose cluster list
```
**What it does**: Shows more detailed information
**Example**: Like getting more detailed information about your phone

---

## 🎯 **Real-World Examples**

### **Scenario 1: New User Setup**
```bash
# 1. Check if UPID is working
upid --help

# 2. Set up UPID
upid init

# 3. Login to your account
upid auth login --email your-email@example.com

# 4. See your clusters
upid cluster list

# 5. Get a quick overview
upid status
```

### **Scenario 2: Daily Cluster Check**
```bash
# 1. Check cluster health
upid universal status

# 2. See resource usage
upid analyze resources cluster-123

# 3. Check costs
upid analyze cost cluster-123 --period 7d

# 4. Get optimization suggestions
upid optimize resources cluster-123 --dry-run
```

### **Scenario 3: Monthly Review**
```bash
# 1. Get comprehensive report
upid report summary cluster-123 --period 30d

# 2. Generate cost report
upid report cost cluster-123 --format html --output monthly-cost.html

# 3. Check performance
upid report performance cluster-123 --format json --output performance.json
```

---

## 🚨 **Important Notes**

### **Safety First**
- Always use `--dry-run` first to see what changes will be made
- The `--force` flag means "I'm sure, don't ask again"
- Local mode (`--local`) is for testing only

### **Getting Help**
- Use `--help` after any command to see its options
- Example: `upid cluster --help`
- Example: `upid optimize --help`

### **Common Patterns**
- Most commands follow: `upid [command] [subcommand] [options]`
- Use `--format` to change how data is displayed
- Use `--output` to save results to a file

---

## 🎉 **You're Ready!**

Now you know how to use UPID CLI! Start with:
1. `upid --help` (see all commands)
2. `upid status` (check if everything is working)
3. `upid demo` (see a demonstration)

**Remember**: UPID is here to help you manage your Kubernetes clusters easily and efficiently! 🚀 