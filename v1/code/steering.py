#11_23
import _thread
import socket
import RPi.GPIO as GPIO
from gpiozero import Servo
import time

end = 0
print("!")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#Buzzer Setup
BuzzerPin = 4
GPIO.setup(BuzzerPin, GPIO.OUT)

global Buzz
Buzz = GPIO.PWM(BuzzerPin, 440)
Buzz.start(0)

#Servo Setup
servoPin = 12
val = 0
		
SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 3

#DC Pin Setup
Motor1A = 7
Motor1B = 8
Motor1E = 25
Motor2A = 15
Motor2B = 18
Motor2E = 14


GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1E, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2E, GPIO.OUT)

DCM1=GPIO.PWM(Motor1E, 100)
DCM2=GPIO.PWM(Motor2E, 100)
DCM1.start(0)
DCM2.start(0)

GPIO.setup(servoPin, GPIO.OUT)
servo = GPIO.PWM(servoPin, 50)  
servo.start(0)  

def setServoPos(degree):
	
	if degree > 180:
		degree = 180

	duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
	print("Degree: {} to {}(Duty)".format(degree, duty))

	servo.ChangeDutyCycle(duty)
	

def threaded(client_socket, addr):
	print("Connected by: ", addr[0], ':', addr[1])

	while True:
		try:
			data = client_socket.recv(1024)
			if not data:
				print('Disconnected by ' + addr[0], ':', addr[1])
				break
			
			print('Received from ' + addr[0], ':', addr[1], data.decode())
			
			num = int(data.decode())
			num_stop = int(num/1000000%10)
			num_servo = int(num/1000)
			num_DC = num%1000
			
			
			#if (num_stop == 1)
			#stop the whole operation and let the dino shout
			if num_stop == 1:
				Buzz.start(10)
				#set the servo neutral
				setServoPos(90)
				#stop the dino
				GPIO.output(Motor1A, GPIO.LOW)
				GPIO.output(Motor1E, GPIO.LOW)
				GPIO.output(Motor2A, GPIO.LOW)
				GPIO.output(Motor2E, GPIO.LOW)

				print("!!!Groooooar!!!")
				#shout
				x = 1500
				while(x<3000):
					Buzz.ChangeFrequency(x)
					time.sleep(0.01)
					x+=40
				  
				while(x>2000):
					Buzz.ChangeFrequency(x)
					time.sleep(0.05)
					x-=20
				Buzz.start(0)



			#elif num_stop == 0
			#follow the person and play the song
			else:
				# control the servo
				val = num_servo*180/100
				setServoPos(val)

				#control the DC
				if num_DC > 100: 		#Max value ctrl
					num_DC = 100
				GPIO.output(Motor1A, GPIO.HIGH) #M1
				GPIO.output(Motor1B, GPIO.LOW)
				GPIO.output(Motor1E, GPIO.HIGH)
				GPIO.output(Motor2A, GPIO.HIGH) #M2
				GPIO.output(Motor2B, GPIO.LOW)
				GPIO.output(Motor2E, GPIO.HIGH)
				# DC speed ctrl
				DCM1.ChangeDutyCycle(num_DC)
				DCM2.ChangeDutyCycle(num_DC)

				if num_DC <= 2:
					GPIO.output(Motor1E, GPIO.LOW)
					GPIO.output(Motor2E, GPIO.LOW)
				
		except ConnectionResetError as e:
			print('Disconnected by', addr[0], ':', addr[1])
			print(f"e: {e}")
	
ip = '192.168.0.78'
port = 8081

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen()
print('server start')

while True:
	if end == 1:
		break
	print("wait")
	cs, addr = server_socket.accept()
	_thread.start_new_thread(threaded, (cs, addr))
