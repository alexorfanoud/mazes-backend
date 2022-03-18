#!/bin/bash

while getopts ":S:a:p:i:n:" opt; do
  case $opt in
    S)
      suite=$OPTARG
      ;;
    a)
	  action=$OPTARG
      ;;
    p)
      packages=$OPTARG
      ;;
    i)
      input=$OPTARG
      ;;
    n)
      threads=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))


IFS=','
read -a packages_arr <<< "$packages"
for package in ${packages_arr[@]};do
	sleep 1m
	echo "Running $package"
	./run -p $package -S $suite -a $action -i $input -n $threads
done
