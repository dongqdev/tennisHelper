import threading
from datetime import datetime



class Reservation:
    def __init__(self, callback):
        self.callback = callback
        self.timer = None
        self.timer_running = False  # 타이머 실행 상태를 나타내는 플래그

    def do_auto_reserve(self):
        self.auto_reserve_stop_timer()
        self.callback()  # 콜백 함수 실행 : do_reserve
        return True

    def auto_reserve_check_time(self, auto_Time_Value):
        if not self.timer_running:  # 타이머가 중지된 경우 함수 실행을 중단
            return

        current_time = datetime.now().strftime("%H:%M:%S")
        run_at_time = auto_Time_Value


        if current_time == run_at_time:
            self.do_auto_reserve()
        # 다음 분에 대한 체크를 위해 1초 후에 함수를 다시 호출
        # auto_reserve_check_time 함수의 경우, auto_Time_Value 인자가 필요하므로 뒤에 argument를 추가한다.
        # 두 개의 인자가 필요하다면 [value1, value2]
        self.timer = threading.Timer(1, self.auto_reserve_check_time, [auto_Time_Value])
        self.timer.start()

    def auto_reserve_start_timer(self, auto_Time_Value):
        self.timer_running = True
        self.auto_reserve_check_time(auto_Time_Value)

    def auto_reserve_stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
        self.timer_running = False


