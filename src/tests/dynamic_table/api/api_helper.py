import logging
from tests.dynamic_table.api.reversed_urls import ReversedUrl

logger = logging.getLogger(__name__)


class APIHelper(ReversedUrl):

    def is_success(self, resp):
        logger.debug(f"response data {getattr(resp, 'data', None)}")
        self.assertEqual(resp.status_code, 200)

    def is_created(self, resp):
        logger.debug(f"response data {resp.data}")
        self.assertEqual(resp.status_code, 201)

    def is_bad_request(self, resp):
        logger.debug(f"response data {resp.data}")
        self.assertEqual(resp.status_code, 400)
