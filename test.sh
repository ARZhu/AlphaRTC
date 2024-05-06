#!/bin/bash

source .venv/bin/activate \
&& python3 test.py \
&& python3 plot.py \
&& python3 my_loss.py \
&& python3 my_throughput.py \
&& deactivate


# && sudo docker run -d --rm -v `pwd`/examples/peerconnection/serverless/corpus:/app -w /app --name alphartc alphartc peerconnection_serverless receiver.json \
# && sudo docker exec alphartc peerconnection_serverless sender.json \


# cd ./AlphaRTC/rundir/runtime && ../../out/Default/peerconnection_serverless ./receiver.json & \
# cd ./AlphaRTC/rundir/runtime && ../../out/Default/peerconnection_serverless ./sender.json &

# wait

# cd .


# ./python/vmaf/script/run_vmaf.py 

