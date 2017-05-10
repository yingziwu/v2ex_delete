#!/bin/bash

rqworker node1 &> /dev/null &
rqworker node2 &> /dev/null &
rqworker node3 &> /dev/null &
rqworker node4 &> /dev/null &
rqworker node5 &> /dev/null & 
echo "Start rqworker,Finished!"
