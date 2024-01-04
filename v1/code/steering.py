import cv2  
from ultralytics import YOLO
import socket  # 소켓 통신


model = YOLO('yolov8n.pt')  

# 영상 수신 설정
URL = 'tcp://192.168.0.13:8080'  # 영상 소스의 URL (변경해야함)
cap = cv2.VideoCapture(URL)  # 객체 생성
fps_limit = 5  # 프레임 제한
frame_count = 0  # 프레임 카운트 초기화

# 조향값 송신 설정
HOST = '192.168.0.13'  # 서버 IP 주소
PORT = 8081  # 송신용 서버 포트 (수신 포트와 상이함!)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
client_socket.connect((HOST, PORT))  # 서버에 연결

# 영상 처리
while cap.isOpened():
    success, frame = cap.read()  # 영상에서 한 프레임 읽기
    height, width = frame.shape[:2]  # 프레임의 높이와 너비 저장

    if success:
        frame_count += 1  

        if frame_count % fps_limit == 0:
            # 일정 간격으로 YOLO 모델로 객체 감지 수행
            results = model.predict(frame, classes=[0])  # YOLOv8 모델로 객체(0 = 사람) 감지 수행 및 결과 저장
            annotated_frame = results[0].plot()  # 감지 결과를 시각화한 프레임 저장

            # 가장 넓은 영역의 객체(사람) 위치 계산
            boxes = results[0].boxes  # 감지된 객체의 바운딩 박스 정보
            wide_area = 0  # 가장 넓은 영역 초기화
            w_x1, w_y1, w_x2, w_y2 = 0, 0, 0, 0  # 가장 넓은 영역의 좌표 초기화
            print("--box--")

            for box in boxes:
                # 박스 크기 계산
                x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
                print(f"l_up = ({x1},{y1})")
                print(f"r_down = ({x2},{y2})")
                area = abs((x2 - x1) * (y2 - y1))

                # 가장 넓은 영역의 객체 정보 업데이트
                if area > wide_area:
                    wide_area = area
                    w_x1, w_y1, w_x2, w_y2 = x1, y1, x2, y2

            # 가장 가까운 사람 위치 중앙값 계산
            cv2.circle(annotated_frame, (w_x1, w_y1), 10, (0, 255, 255), -1)
            cv2.circle(annotated_frame, (w_x2, w_y2), 10, (0, 255, 255), -1)
            cent = (w_x1 + w_x2) / 2
            print(f"center = {cent}")

            # 화면 출력
            cv2.imshow("YOLOv8 Inference", annotated_frame)

            # 조향 계산 중앙 기준으로 단순 조향 -> 추후 개선 필요
            if width * 3/7 < cent and cent < width * 4/7:
                print("직진")
                ste = 50
                vel = 0
            elif cent <= width * 3/7:
                print("좌회전")
                ste = 0
                vel = 100
            else:
                print("우회전")
                ste = 100
                vel = 100

            motor = str(1000 * ste + vel)  # 조향값과 속도를 조합하여 문자열로 변환
            client_socket.send(motor.encode())  # 서버로 조향값 및 속도 전송

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break  # 'q' 키를 누르면 루프 종료

    else:
        print("카메라 오류")

cap.release()  # 영상 수신 종료 시 웹캠을 해제
cv2.destroyAllWindows()  # OpenCV 창 닫기
