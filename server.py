#!/usr/bin/env python

import grpc
import sys
from PIL import Image, ImageFilter
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse

import os
from utils import image_pb2_grpc, image_pb2
from pathlib import Path
from utils.helpers import process_image
from utils.process_functions import rotate_image, apply_mean_filter



class NLImageService(image_pb2_grpc.NLImageServiceServicer):
    def RotateImage(self, request, context):
        """
        rotate the nlimage given the image data and rotation degrees stored in request
        :param request: stores info about image
        :param context: stores info about errors, processing, etc.
        :return: nlimage
        """
        return process_image(request, context, rotate_image)

    def MeanFilter(self, request, context):
        """
        apply the mean filter to the nlimage given the image data  stored in request
        :param request: stores info about image
        :param context: stores info about errors, processing, etc.
        :return: nlimage
        """
        return process_image(request, context, apply_mean_filter)

def serve(port, host):
    """
    start the server at specified port and host
    :param port: (int) port to connect server to
    :param host: (string) ip address to connect server to
    """
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    image_pb2_grpc.add_NLImageServiceServicer_to_server(NLImageService(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    logging.info(f"started server at {host}:{port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("Server stopped due to keyboard interruption")
    logging.info("ended server")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NLImage gRPC Client")
    parser.add_argument("--port", type=int, default=50051, help="Port to bind to")
    parser.add_argument("--host", type=str, default="localhost", help="Server to bind to")
    args = parser.parse_args()
    port = args.port
    host = args.host
    serve(port, host)