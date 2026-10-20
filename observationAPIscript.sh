#!/bin/bash
# Outputs: Real-time cpu, memory, disk, and network usage. 

# Calculates average cpu in the last 0.1 seconds
function getRealCPU(){
  read -r _ user nice system idle iowait irq softirq steal < /proc/stat
  local prev_idle=$((idle + iowait))
  local prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))
  
  sleep 0.1

  read -r _ user nice system idle iowait irq softirq steal < /proc/stat
  local now_idle=$((idle + iowait))
  local now_total=$((user + nice + system + idle + iowait + irq + softirq + steal))


  local diff_idle=$((now_idle - prev_idle))
  local diff_total=$((now_total - prev_total))
  echo $((100 * (diff_total - diff_idle) / diff_total))
}

function getRealMemory(){
  local availableMemory=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  local totalMemory=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

  echo $(((100*availableMemory)/totalMemory))
}

function getRealDisk(){

}

function getRealNewtork(){

}

cpu_real=$(getRealCPU)
mem_real=$(getRealMemory)
disk_real=$(getRealDisk)
net_real=$(getRealNewtork)
