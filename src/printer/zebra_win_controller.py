"""
Zebra 프린터 제어 (zebra 라이브러리 사용)
시스템 프린터 큐를 통한 제어
"""

from typing import Optional, List
from zebra import Zebra


class ZebraWinController:
    """
    시스템 프린터 큐를 사용한 Zebra 프린터 제어
    zebra 라이브러리 사용
    """

    def __init__(self, queue_name: Optional[str] = None):
        """
        Args:
            queue_name: 시스템 프린터 큐 이름 (예: "ZDesigner ZT231-203dpi ZPL")
                       None이면 나중에 설정
        """
        self.zebra = Zebra(queue_name)
        self.queue_name = queue_name
        self._is_connected = False

    def get_available_printers(self) -> List[str]:
        """
        사용 가능한 모든 프린터 큐 목록 반환

        Returns:
            프린터 큐 이름 리스트
        """
        return self.zebra.getqueues()

    def get_zebra_printers(self) -> List[str]:
        """
        Zebra 프린터만 필터링하여 반환

        Returns:
            Zebra 프린터 큐 이름 리스트
        """
        all_queues = self.get_available_printers()
        return [
            q for q in all_queues
            if 'zebra' in q.lower() or 'zdesigner' in q.lower() or 'zpl' in q.lower()
        ]

    def connect(self, queue_name: Optional[str] = None) -> bool:
        """
        프린터에 연결

        Args:
            queue_name: 연결할 프린터 큐 이름
                       None이면 첫 번째 Zebra 프린터에 자동 연결

        Returns:
            연결 성공 여부

        Raises:
            ValueError: 프린터를 찾을 수 없는 경우
        """
        if queue_name:
            # 지정된 프린터로 연결
            self.zebra.setqueue(queue_name)
            self.queue_name = queue_name
            self._is_connected = True
            return True

        # 자동 연결: 첫 번째 Zebra 프린터 찾기
        zebra_printers = self.get_zebra_printers()

        if not zebra_printers:
            raise ValueError("시스템 프린터 큐에서 Zebra 프린터를 찾을 수 없습니다")

        # 첫 번째 Zebra 프린터 사용
        self.queue_name = zebra_printers[0]
        self.zebra.setqueue(self.queue_name)
        self._is_connected = True

        return True

    def is_connected(self) -> bool:
        """
        프린터 연결 상태 확인

        Returns:
            연결 여부
        """
        return self._is_connected and self.queue_name is not None

    def send_zpl(self, zpl_command: str) -> bool:
        """
        ZPL 명령 전송

        Args:
            zpl_command: ZPL 명령 문자열

        Returns:
            전송 성공 여부

        Raises:
            RuntimeError: 프린터 미연결 상태
        """
        if not self.is_connected():
            raise RuntimeError("Printer not connected. Call connect() first.")

        try:
            self.zebra.output(zpl_command)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send ZPL command: {e}")

    def print_label(self, zpl_command: str) -> bool:
        """
        라벨 출력 (send_zpl의 별칭)

        Args:
            zpl_command: ZPL 명령 문자열

        Returns:
            출력 성공 여부
        """
        return self.send_zpl(zpl_command)

    def test_print(self) -> bool:
        """
        테스트 라벨 출력

        Returns:
            출력 성공 여부
        """
        from datetime import datetime

        test_zpl = f"""^XA
^FO50,50^A0N,50,50^FDZebra Test Print^FS
^FO50,120^A0N,30,30^FDQueue: {self.queue_name}^FS
^FO50,170^A0N,30,30^FDTime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}^FS
^XZ"""

        return self.send_zpl(test_zpl)

    def get_printer_info(self) -> dict:
        """
        프린터 정보 반환

        Returns:
            프린터 정보 dict
        """
        return {
            "queue_name": self.queue_name,
            "is_connected": self._is_connected,
            "library": "zebra",
            "method": "System Print Queue"
        }

    def __str__(self) -> str:
        """문자열 표현"""
        if self.queue_name:
            return f"ZebraWinController(queue='{self.queue_name}')"
        return "ZebraWinController(not connected)"

    def __repr__(self) -> str:
        """개발자용 표현"""
        return self.__str__()
