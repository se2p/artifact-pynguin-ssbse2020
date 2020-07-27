#!/usr/bin/env bash

PID=$$
ITERATIONS=30

function sig_handler {
  echo "Killing ${0} including its children..."
  pkill -TERM -P ${PID}

  echo -e "Terminated: ${0}\n"
}
trap sig_handler INT TERM HUP QUIT

function echo_blue {
  BLUE="\033[0;34m"
  NC="\033[0m"
  echo -e "${BLUE}${1}${NC}\n"
}

function setup_for_project() {
  python3 generate_slurm_job_scripts.py

  chmod +x array_job.sh
  chmod +x run_cluster_job.sh
  chmod +x run_execution-*.sh
}

function cleanup_shell_scripts {
  rm -rf array_job.sh
  rm -rf run_cluster_job.sh
  rm -rf run_execution-*.sh
  rm -rf *.out
}

function run_slurm_execution {
  ./run_cluster_job.sh
}

function merge_statistics_csv {
  # first parameter: project_name, second parameter: iteration number
  python3 merge_statistics_csv.py ${1} ${2}
}

function main {
  setup_for_project
  for ((i=1;i<=${ITERATIONS};i++))
  do
    mkdir -p ../pynguin-results
    echo_blue "Run SLURM iteration ${i}"
    run_slurm_execution
    echo_blue "Merge Statistics CSVs"
    for project in ./projects/*/
    do
      dir=${project%*/}
      project_name=${dir##*/}
      echo_blue "Merge for project ${project_name}"
      merge_statistics_csv ${project_name} ${i}
    done
    rm -rf ../pynguin-results
  done
  echo_blue "Cleanup"
  cleanup_shell_scripts
}

main
