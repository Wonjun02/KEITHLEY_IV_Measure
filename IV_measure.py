import pyvisa
import time

# 1. 설정값 입력
device_address = 'USB0::0x05E6::0x2470::04530182::INSTR'
file_name = "E01_24_IV.csv"

start_v = 0
stop_v = -1100
step_v = -5      # 측정 완료 지점
delay = 1.0      # delay seconds[s]
i_limit = 1e-6   # 전류 리미트 [A] : 1uA로 설정

# 2. 장비 연결
rm = pyvisa.ResourceManager()
inst = rm.open_resource(device_address)
#inst.write : 명령 전달
#inst.query : 질문 후 답변

results = [] # 데이터 저장을 위해 try 바깥에 선언

try:
    # 3. 장비 초기화 및 고전압 설정
    inst.write("reset()")
    inst.write("smu.terminals = smu.TERMINALS_REAR")
    inst.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
    inst.write("smu.measure.func = smu.FUNC_DC_CURRENT")
    
    inst.write(f"smu.source.ilimit.level = {i_limit}") # 1uA 리미트
    inst.write("smu.measure.range = 1e-6")           # 측정 범위를 1uA에 고정
    inst.write("smu.source.range = 1100")            # 전압 소스 범위를 1100V로 설정

    # 4. 측정 시작
    inst.write("smu.source.output = smu.ON") 
    print(f"측정 시작: {file_name}")
    print("Voltage(V), Current(A)")

    # 0V에서 -1100V까지 반복 (부동소수점 오차 방지를 위해 보정치 추가)
    current_v = start_v
    while current_v >= stop_v - 0.001:
        inst.write(f"smu.source.level = {current_v}")
        time.sleep(delay)
        
        # 데이터 읽기
        raw_data = inst.query("print(smu.measure.read())").strip()
        current_read = float(raw_data) # 비교를 위해 숫자로 변환
        
        print(f"{current_v:>7}V, {current_read:e}A")
        results.append(f"{current_v},{current_read}")
        
        # 리미트 도달 여부 확인 (절대값 기준)
        if abs(current_read) >= i_limit * 0.99:
            print("전류 리미트(Compliance)에 도달하여 측정을 조기 종료합니다.")
            break
            
        # 다음 스텝으로 이동
        current_v += step_v

except KeyboardInterrupt:
    # 측정 조기 종료
    print("\n사용자에 의해 측정이 중단되었습니다.")

finally:
    # 5. 안전한 종료 (전압을 0V로 되돌리고 종료)
    # try 내부에서 오류가 나거나 중단되어도 무조건 실행됩니다.
    inst.write("smu.source.level = 0")
    inst.write("smu.source.output = smu.OFF")
    inst.close()
    print("측정이 안전하게 종료되었습니다.")

    # 6. CSV 파일 저장 (finally 안으로 옮겨 중단 시에도 저장되게 함)
    if results:
        with open(file_name, "w") as f:
            f.write("Voltage(V),Current(A)\n")
            for line in results:
                f.write(line + "\n")
        print(f"파일 저장 완료: {file_name} (총 {len(results)}개 데이터)")
    else:
        print("저장할 데이터가 없습니다.")

# 6. CSV 파일 저장
with open(file_name, "w") as f:
    f.write("Voltage(V),Current(A)\n")
    for line in results:
        f.write(line + "\n")

print(f"파일 저장 완료: {file_name}")
