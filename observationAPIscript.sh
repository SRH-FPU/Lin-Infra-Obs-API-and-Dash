#!/bin/bash
# Setup

# Enable firewall if disables
if "inactive"=(sudo ufw status | awk 'print $2'); then
  sudo ufw enable
  sudo ufw allow from IPaddress to any port 9070 proto tcp
fi
23.128.112.34
calculationInterval=0.1

# Calculates average cpu over the calculation interval.
function getRealCPU(){
  read -r _ user nice system idle iowait irq softirq steal < /proc/stat
  local prev_idle=$((idle + iowait))
  local prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))
  
  sleep $(calculationInterval)

  read -r _ user nice system idle iowait irq softirq steal < /proc/stat
  local now_idle=$((idle + iowait))
  local now_total=$((user + nice + system + idle + iowait + irq + softirq + steal))


  local diff_idle=$((now_idle - prev_idle))
  local diff_total=$((now_total - prev_total))
  echo $((100 * (diff_total - diff_idle) / diff_total))
}

# Calculates % memory used.
function getRealMemory(){
  local availableMemory=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  local totalMemory=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

  echo $(((100*availableMemory)/totalMemory))
}

# Returns % disk space used.
function getRealDisk(){
  echo $((df -h / | awk 'NR==2 {print $5}'))
}

# Returns download and upload bandwitdh usage in KB/s 
function getRealNewtork(){
  rec1=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
  trn1=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)

  sleep $(calculationInterval)

  rec2=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
  trn2=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)

  usageDown=$(((rec2 - rec1)/1024))
  usageUp=$(((trn2 - trn1)/1024))

  echo '${usageDown} ${usageUp}'
}

# Execute
while true; do
  cpu_real=$(getRealCPU)
  mem_real=$(getRealMemory)
  disk_real=$(getRealDisk)
  read -r net_down net_up <<< "$(getRealNewtork)"

  # Output to json.
  printf '{"cpu": "%d", "mem": "%d"", "disk": "%s"", "netDown": "%d"", "netUp": "%d"}\n' "$cpu_real" "$mem_real" "$disk_real" "$net_down" "$net_up" > observationAPI.json
done
