sudo docker run --mount type=volume,dst=/mnt/ml-nba,volume-opt=type=nfs,volume-opt=device=:/ml-nba,volume-opt=o=addr=10.0.0.161 modeling:v1