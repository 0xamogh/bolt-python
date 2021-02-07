import logging
from typing import Callable, Dict, Any

from slack_bolt.authorization import AuthorizeResult
from slack_bolt.logger import get_bolt_logger
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.middleware.middleware import Middleware


class IgnoringSelfEvents(Middleware):
    def __init__(self):
        """Ignores the events generated by this bot user itself."""
        self.logger = get_bolt_logger(IgnoringSelfEvents)

    def process(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
        next: Callable[[], BoltResponse],
    ) -> BoltResponse:
        auth_result = req.context.authorize_result
        if self._is_self_event(auth_result, req.context.user_id, req.body):
            print("This is a self event")
            self._debug_log(req.body)
            return req.context.ack()
        else:
            return next()

    # -----------------------------------------

    # Its an Events API event that isn't of type message,
    # but the user ID might match our own app. Filter these out.
    # However, some events still must be fired, because they can make sense.
    events_that_should_be_kept = ["member_joined_channel", "member_left_channel"]

    @classmethod
    def _is_self_event(
        cls, auth_result: AuthorizeResult, user_id: str, body: Dict[str, Any]
    ):
        return (
            auth_result is not None
            and user_id is not None
            and user_id == auth_result.bot_user_id
            and body.get("event") is not None
            and body.get("event", {}).get("type") not in cls.events_that_should_be_kept
        )

    def _debug_log(self, body: dict):
        if self.logger.level <= logging.DEBUG:
            event = body.get("event")
            self.logger.debug(f"Skipped self event: {event}")
