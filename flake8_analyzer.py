#!/usr/bin/env python3

# Analyzer that wrapps the flake8 metalinter for Python

from concurrent.futures import ThreadPoolExecutor

import shutil
import grpc
import os
import tempfile
import time

from lookout.sdk import service_analyzer_pb2_grpc
from lookout.sdk import service_analyzer_pb2
from lookout.sdk import service_data_pb2_grpc
from lookout.sdk import service_data_pb2
from flake8.main import application

host_to_bind = os.getenv('FLAKE8_HOST', "0.0.0.0")
port_to_listen = os.getenv('FLAKE8_PORT', 2022)
data_srv_addr = os.getenv('FLAKE8_DATA_SERVICE_URL', "localhost:10301")
log_level = os.getenv('FLAKE8_LOG_LEVEL', "info")

version = "alpha"
# TODO: configure errors and warnings
grpc_max_msg_size = 100 * 1024 * 1024  #100mb


class Analyzer(service_analyzer_pb2_grpc.AnalyzerServicer):
    def NotifyReviewEvent(self, request, context):
        print("got review request {}".format(request))

        # client connection to DataServe
        channel = grpc.insecure_channel(data_srv_addr, options=[
                ("grpc.max_send_message_length", grpc_max_msg_size),
                ("grpc.max_receive_message_length", grpc_max_msg_size),
            ])
        stub = service_data_pb2_grpc.DataStub(channel)
        changes = stub.GetChanges(
            service_data_pb2.ChangesRequest(
                head=request.commit_revision.head,
                base=request.commit_revision.base,
                want_language=True,
                want_contents=True,
                want_uast=False,
                exclude_vendored=True))
        comments = []

        temp_dir = tempfile.mkdtemp()
        app = application.Application()
        n = 0

        try:
            app.initialize([])

            # FIXME: probably will need the full repo to give good results
            for change in changes:
                if change.head.language.lower() != "python":
                    continue

                file_path = os.path.join(temp_dir, change.head.path)

                try:
                    with open(file_path, "wb") as test_file:
                        test_file.write(change.head.content)
                        test_file.flush()
                        app.file_checker_manager.start([file_path])

                        for checker in app.file_checker_manager.checkers:
                            _, results, _ = checker.run_checks()

                            for r in results:
                                c = service_analyzer_pb2.Comment(
                                            file=change.head.path,
                                            line=r[1],
                                            text="{}: {}".format(r[0], r[3]))
                                if c:
                                    comments.append(c)
                                    n += 1
                finally:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
        finally:
            shutil.rmtree(temp_dir)

        print("{} comments produced".format(n))
        return service_analyzer_pb2.EventResponse(
            analyzer_version=version, comments=comments)

    def NotifyPushEvent(self, request, context):
        pass


def serve():
    server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
    service_analyzer_pb2_grpc.add_AnalyzerServicer_to_server(Analyzer(), server)
    server.add_insecure_port("{}:{}".format(host_to_bind, port_to_listen))
    server.start()

    one_day_sec = 60*60*24
    try:
        while True:
            time.sleep(one_day_sec)
    except KeyboardInterrupt:
        server.stop(0)


def main():
    print("starting gRPC Analyzer server at port {}".format(port_to_listen))
    serve()


if __name__ == "__main__":
    main()
