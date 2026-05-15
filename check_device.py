import pyvisa

# 리소스 매니저 생성
rm = pyvisa.ResourceManager()

# 연결된 장비 목록 출력
print("연결된 장비 리스트:", rm.list_resources())
