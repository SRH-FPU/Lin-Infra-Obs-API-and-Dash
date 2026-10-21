#!/bin/bash
# Enable firewall if disables
authorizedIP="23.128.112.34"
authorizeGoogle="35.235.240.0/20"
sudo iptables -F INPUT
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A INPUT -s "$authorizedIP" -j ACCEPT
sudo iptables -A INPUT -s "$authorizeGoogle" -j ACCEPT
sudo iptables -A INPUT -j DROP

# Sets interval of CPU and Network utilization
calculationInterval=0.1

# Calculates average cpu over the calculation interval.
function getRealCPU(){
  read -r cpu_label user nice system idle iowait irq softirq steal guest guest_nice < <(grep '^cpu ' /proc/stat)
  local prev_idle=$((idle + iowait))
  local prev_total=$((${user:-0} + ${nice:-0} + ${system:-0} + ${idle:-0} + ${iowait:-0} + ${irq:-0} + ${softirq:-0} + ${steal:-0}))
  
  sleep $calculationInterval

  read -r cpu_label user nice system idle iowait irq softirq steal guest guest_nice < <(grep '^cpu ' /proc/stat)
  local now_idle=$((idle + iowait))
  local now_total=$((${user:-0} + ${nice:-0} + ${system:-0} + ${idle:-0} + ${iowait:-0} + ${irq:-0} + ${softirq:-0} + ${steal:-0}))


  local diff_idle=$((now_idle - prev_idle))
  local diff_total=$((now_total - prev_total))
  
  if [ "$diff_total" -eq 0 ]; then
    echo 0
  else
    echo $((100 * (diff_total - diff_idle) / diff_total))
  fi
}

# Calculates % memory used.
function getRealMemory(){
  local availableMemory=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  local totalMemory=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)

  echo $((100*(totalMemory-availableMemory)/totalMemory))
}

# Returns % disk space used.
function getRealDisk(){
  echo $(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
}

# Returns download and upload bandwitdh usage in KB/s 
function getRealNewtork(){
  interface="eth0"
  if [ ! -d "/sys/class/net/$interface" ]; then
    interface=$(ip route show | awk '/default/ {print $5}' | head -n1)
  fi
  
  rec1=$(cat /sys/class/net/$interface/statistics/rx_bytes)
  trn1=$(cat /sys/class/net/$interface/statistics/tx_bytes)

  sleep $calculationInterval

  rec2=$(cat /sys/class/net/$interface/statistics/rx_bytes)
  trn2=$(cat /sys/class/net/$interface/statistics/tx_bytes)

  usageDown=$((10*(rec2 - rec1)/1024))
  usageUp=$((10*(trn2 - trn1)/1024))

  echo "${usageDown} ${usageUp}"
}

# Execute
while true; do
  cpu_real=$(getRealCPU)
  mem_real=$(getRealMemory)
  disk_real=$(getRealDisk)
  read -r net_down net_up <<< "$(getRealNewtork)"

  # Output to json.
  printf '{"cpu": "%s", "mem": "%s", "disk": "%s", "netDown": "%s", "netUp": "%s"}\n' "$cpu_real" "$mem_real" "$disk_real" "$net_down" "$net_up" > observationAPI.json

  sleep 1
done
