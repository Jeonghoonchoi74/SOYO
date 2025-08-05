import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase.json')
        print("파일 확인 완료")
        firebase_admin.initialize_app(cred)
        print("파이어베이스 초기화 완료")
    
    return firestore.client()

# 전역 db 인스턴스
db = None

def get_db():
    """데이터베이스 인스턴스 반환"""
    global db
    if db is None:
        db = initialize_firebase()
    return db