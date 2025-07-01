#!/bin/bash

protos=("speech" "health")

proto_src_dir="grpc_server/proto"

output_dir="grpc_server/pb"

rm -rf grpc_server/pb

mkdir -p grpc_server/pb

# Create __init__.py file
echo "# Generated protobuf files" > grpc_server/pb/__init__.py

for proto_file in "${protos[@]}"; do
    echo "Processing $proto_file..."
    poetry run python -m grpc_tools.protoc -I"$proto_src_dir" --python_out="$output_dir" --pyi_out="$output_dir" --grpc_python_out="$output_dir" "$proto_src_dir/$proto_file.proto"
    
    # Fix imports in generated _grpc.py files to use relative imports
    sed -i "s/import ${proto_file}_pb2 as ${proto_file}__pb2/from . import ${proto_file}_pb2 as ${proto_file}__pb2/g" "$output_dir/${proto_file}_pb2_grpc.py"
done

echo "All .proto files have been processed."