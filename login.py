import logging
from requests import Session

class KrxSessionManager:
    def __init__(self, login_id: str, login_pw: str):
        self.session = Session()
        self.login_id = login_id
        self.login_pw = login_pw
        self._UA = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        self.session.headers.update({"User-Agent": self._UA})

    def patch_pykrx(self, webio_module):
        """pykrx의 webio 모듈에 현재 세션을 주입합니다 (클로저 활용)."""
        def _session_post_read(webio_self, **params):
            return self.session.post(webio_self.url, headers=webio_self.headers, data=params)

        def _session_get_read(webio_self, **params):
            return self.session.get(webio_self.url, headers=webio_self.headers, params=params)

        webio_module.Post.read = _session_post_read
        webio_module.Get.read = _session_get_read

    def is_authenticated(self) -> bool:
        """
        현재 세션이 유효한지 검증합니다.
        가장 단순하게는 JSESSIONID 쿠키 존재 여부를 확인하며,
        더 엄격하게는 로그인 필수 API를 찔러보고 HTTP 상태 코드나 응답값을 확인할 수 있습니다.
        """
        cookies = self.session.cookies.get_dict()
        return "JSESSIONID" in cookies

    def login(self) -> bool:
        """세션이 유효하지 않은 경우에만 로그인을 수행합니다."""
        if self.is_authenticated():
            logging.info("기존 세션이 유효하여 로그인을 생략합니다.")
            return True

        _LOGIN_PAGE = "https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001.cmd"
        _LOGIN_JSP  = "https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc"
        _LOGIN_URL  = "https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd"

        try:
            # 초기 세션 발급
            self.session.get(_LOGIN_PAGE, timeout=15)
            self.session.get(_LOGIN_JSP, headers={"Referer": _LOGIN_PAGE}, timeout=15)

            payload = {
                "mbrNm": "", "telNo": "", "di": "", "certType": "",
                "mbrId": self.login_id, "pw": self.login_pw,
            }
            headers = {"Referer": _LOGIN_PAGE}

            # 로그인 POST
            resp = self.session.post(_LOGIN_URL, data=payload, headers=headers, timeout=15)
            data = resp.json()
            error_code = data.get("_error_code", "")

            # 중복 로그인(CD011) 처리
            if error_code == "CD011":
                payload["skipDup"] = "Y"
                resp = self.session.post(_LOGIN_URL, data=payload, headers=headers, timeout=15)
                data = resp.json()
                error_code = data.get("_error_code", "")

            success = (error_code == "CD001")
            if success:
                logging.info("KRX 로그인 성공")
            else:
                logging.error(f"KRX 로그인 실패. 코드: {error_code}")
            return success

        except Exception as e:
            logging.error(f"로그인 중 예외 발생: {e}")
            return False