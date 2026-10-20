#!/bin/bash
# Outputs: Average CPU usage since boot and real-time cpu, memory, disk, and network usage. 



function getRealCPU(){
  read -r _ user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
  local prev_idle=$((idle + iowait))
  local prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))
  
  sleep 0.1

  local idle=$((idle + iowait))
  local total=$((user + nice + system + idle + iowait + irq + softirq + steal))

# Compute the differences
  local diff_idle=$((idle - prev_idle))
  local diff_total=$((total - prev_total))

  echo $((100 * (diff_total - diff_idle) / diff_total))
}

cpu_real=$(getRealCPU)
