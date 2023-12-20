# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC route guide client."""

from __future__ import print_function
import logging
import sys
import argparse
import grpc
from utils import image_pb2_grpc, image_pb2
from pathlib import Path
from utils.helpers import is_port_valid, is_valid_ip



def run(host, port, input, output, rotate, mean):
    with grpc.insecure_channel(f"{host}:{port}") as channel:
        stub = image_pb2_grpc.NLImageServiceStub(channel)

        # Create an NLImage object to pass to the server
        try:
            with open(input, 'rb') as image_file:
                image_data = image_file.read()
        except FileNotFoundError:
            logging.error(f"Error: File not found at path: {input}")
            sys.exit(1)

        nl_image = image_pb2.NLImage(data=image_data)

        # Rotate Image
        rotate_request = image_pb2.NLImageRotateRequest(rotation=rotate, image=nl_image)
        nl_image = stub.RotateImage(rotate_request)
        logging.info("Rotated Image ", rotate, " degrees")

        # Mean Filter Image
        if mean:
            nl_image_request = image_pb2.NLImage(data=nl_image.data)
            nl_image = stub.MeanFilter(nl_image_request)
            logging.info("Filtered Image")

        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as file:
            file.write(nl_image.data)
            logging.info("Outputted file at path: ", output)

def get_rotate(rotate):

    rotation_enum_mapping = {
        "NONE": 0,
        "NINETY_DEG": 90,
        "ONE_EIGHTY_DEG": 180,
        "TWO_SEVENTY_DEG": 270,
    }

    if (rotate is not None) and (rotate not in rotation_enum_mapping):
        logging.error(f"Error: Invalid rotation '{rotate}'."
                      f" Valid rotations are: NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG")
        sys.exit(1)

    # Example: RotateImage RPC with user-specified rotation
    return rotation_enum_mapping.get(rotate, 0)

if __name__ == "__main__":

    # optional inputs
    parser = argparse.ArgumentParser(description="NLImage gRPC Client")
    parser.add_argument("--rotate", type=str, default=None, help='Rotation in string format (NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG)')
    parser.add_argument("--mean", default=False, action='store_true', help='Apply mean filter')
    parser.add_argument("--port", type=int, default=50051, help="Port to bind to (default is 50051)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server to bind to (default is 127.0.0.1)")
    parser.add_argument("--input", type=str, required=True, help="path to inputted image")
    parser.add_argument("--output", type=str, required=True, help="path for outputted image")
    args = parser.parse_args()

    # required inputs
    port = args.port
    host = args.host
    input = args.input
    output = args.output
    is_valid_ip(host)
    is_port_valid(port)

    rotate = get_rotate(args.rotate)
    mean = args.mean

    run(host, port, input, output, rotate, mean)