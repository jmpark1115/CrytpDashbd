import os
try:
    from .common import BASE_DIR
except :
    raise ValueError

# 로그 디렉토리 경로 정의
log_dir = os.path.join(BASE_DIR, 'logs')

# 로그 디렉토리가 존재하지 않으면 생성
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOGGING = {
    'version': 1,
    # 기존의 로깅 설정을 비활성화 할 것인가?
    'disable_existing_loggers': False,

    # 포맷터
    # 로그 레코드는 최종적으로 텍스트로 표현됨
    # 이 텍스트의 포맷 형식 정의
    # 여러 포맷 정의 가능
    'formatters': {
        'format1': {
            'format': '[%(asctime)s] [%(module)s:%(lineno)s] %(message)s',
        },
        'format2': {
            'format': '[%(asctime)s] [%(module)s:%(lineno)s]  %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s',
        },
    },

    # 핸들러
    # 로그 레코드로 무슨 작업을 할 것인지 정의
    # 여러 핸들러 정의 가능
    'handlers': {
        # 로그 파일을 만들어 텍스트로 로그레코드 저장
        'file': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'logfile.txt'),
            'maxBytes': 1024*1024*10, # 5 MB
            'backupCount': 20,
            'formatter': 'format1',
            'encoding': 'UTF-8',
        },
        # 콘솔(터미널)에 출력
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'format2',
        }
    },
    # 로거
    # 로그 레코드 저장소
    # 로거를 이름별로 정의
    'loggers': {
        'optionbd': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },'exchange': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}