#!/bin/bash

rqworker node1 &> log/node1.log &
rqworker node2 &> log/node2.log &
rqworker node3 &> log/node3.log &
rqworker node4 &> log/node4.log &
rqworker node5 &> log/node5.log &
rqworker failed &> log/failed.log &
rqworker topic &> log/topic.log &
rqworker tester &> log/tester.log &
echo "Start rqworker,Finished!"
