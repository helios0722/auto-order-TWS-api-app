from logging import error
from ibapi.order_condition import ExecutionCondition
from ibapi.utils import iswrapper
from ibapi.common import *
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class IBapiApp(EWrapper, EClient):
    app = None

    def __init__(self, errorHandler=None):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)

        self.errorHandler = errorHandler
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}

        # handlers
        self.openOrderEndHandler = None

    @iswrapper
    def connectAck(self):
        if self.asynchronous:
            self.startApi()

    @iswrapper
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        self.start()

    def start(self):
        if self.started:
            return
        self.started = True

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    @iswrapper
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        msg = "Error.Id: %d Code %d Msg: %s" % (reqId, errorCode, errorString)
        print(msg) if not self.errorHandler else self.errorHandler(msg)

    @iswrapper
    def winError(self, text: str, lastError: int):
        super().winError(text, lastError)

    @iswrapper
    def currentTime(self, time: int):
        super().currentTime(time)

    @iswrapper
    def openOrder(
        self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState
    ):
        super().openOrder(orderId, contract, order, orderState)
        order.contract = contract
        self.permId2ord[order.permId] = order

    @iswrapper
    def openOrderEnd(self):
        super().openOrderEnd()
        self.openOrderEndHandler() if self.openOrderEndHandler else print(
            "Received %d openOrders", len(self.permId2ord)
        )

    @iswrapper
    def orderStatus(
        self,
        orderId: OrderId,
        status: str,
        filled: float,
        remaining: float,
        avgFillPrice: float,
        permId: int,
        parentId: int,
        lastFillPrice: float,
        clientId: int,
        whyHeld: str,
        mktCapPrice: float,
    ):
        super().orderStatus(
            orderId,
            status,
            filled,
            remaining,
            avgFillPrice,
            permId,
            parentId,
            lastFillPrice,
            clientId,
            whyHeld,
            mktCapPrice,
        )

    @iswrapper
    def execDetails(
        self, reqId: int, contract: Contract, execution: ExecutionCondition
    ):
        super().execDetails(reqId, contract, execution)

    @iswrapper
    def orderBound(self, orderId: int, apiClientId: int, apiOrderId: int):
        super().orderBound(orderId, apiClientId, apiOrderId)