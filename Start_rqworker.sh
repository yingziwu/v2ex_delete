#!/bin/bash

rqworker node1 &> log/node1_rqworker.log &
rqworker node2 &> log/node2_rqworker.log &
rqworker node3 &> log/node3_rqworker.log &
rqworker node4 &> log/node4_rqworker.log &
rqworker node5 &> log/node5_rqworker.log &
rqworker topic &> log/topic_rqworker.log &
rqworker tester &> log/tester_rqworker.log &
rqworker failed &> log/failed1_rqworker.log &
rqworker failed &> log/failed2_rqworker.log &
rqworker failed &> log/failed3_rqworker.log &
rqworker failed &> log/failed4_rqworker.log &
rqworker failed &> log/failed5_rqworker.log &
rqworker failed &> log/failed6_rqworker.log &
echo "Start rqworker,Finished!"
