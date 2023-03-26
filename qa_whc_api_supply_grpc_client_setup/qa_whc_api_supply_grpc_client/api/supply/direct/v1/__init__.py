from ozwhc.grpc_clients import BaseGrpc
from qa_whc_api_supply_grpc_client.api.supply.direct.v1 import direct_pb2, direct_pb2_grpc
from google.protobuf.empty_pb2 import Empty


class OzonWhcApiSupplyDirectV1DirectSupply(BaseGrpc):
    grpc_stub = direct_pb2_grpc.DirectSupplyStub

    def v1_get_unload_rejection_reasons(self, request: direct_pb2.V1GetUnloadRejectionReasonsRequest, **kwargs) -> direct_pb2.V1GetUnloadRejectionReasonsResponse:
        return self._grpc_request(request=request, request_method=self.stub.V1GetUnloadRejectionReasons, **kwargs)
        
    def v1_get_unload_rejection_reason(self, request: direct_pb2.V1GetUnloadRejectionReasonRequest, **kwargs) -> direct_pb2.V1GetUnloadRejectionReasonResponse:
        return self._grpc_request(request=request, request_method=self.stub.V1GetUnloadRejectionReason, **kwargs)
        
    def v1_get_unload_cargo_comments(self, request: direct_pb2.V1GetUnloadCargoCommentsRequest, **kwargs) -> direct_pb2.V1GetUnloadCargoCommentsResponse:
        return self._grpc_request(request=request, request_method=self.stub.V1GetUnloadCargoComments, **kwargs)
        
    def v1_get_unload_cargo_comment(self, request: direct_pb2.V1GetUnloadCargoCommentRequest, **kwargs) -> direct_pb2.V1GetUnloadCargoCommentResponse:
        return self._grpc_request(request=request, request_method=self.stub.V1GetUnloadCargoComment, **kwargs)
        