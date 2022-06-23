from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required

import mysql.connector
from ref.mysql_connection import get_connection

from ref.utils import check_password, hash_password
from email_validator import validate_email, EmailNotValidError

class UserRegisterResource(Resource) :
    # 회원가입
    def post(self) :
        # 데이터 교환 형식
        # {
        #     "email": "abc@naver.com",
        #     "password": "1234"
        #     "name" : "홍길동"
        #     "gender": "Male"
        # }
        data = request.get_json()

        # 이메일 주소 형식 확인, email_validator 사용
        try :
            validate_email( data['email'] )
        except EmailNotValidError as e:
            print(str(e))
            return {'error' : str(e) }, 400
        
        # 비밀번호의 길이 유효 체크, 4~12자리
        if len(data['password']) < 4 or len(data['password']) > 12 :
            return { "error" : "비밀번호의 길이를 확인해주세요 (4-12자리)" }, 400

        # 비밀번호 암호화, passlib 사용
        hashed_password = hash_password( data['password'] )
        
        try :
            query = '''
            insert into user
                (email, password, name, gender)
            values
                (%s ,%s ,%s, %s);
            '''
            record = (data['email'], hashed_password, data['name'], data['gender'])
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return {
            "알림" : data['name']+"님 회원가입이 완료되었습니다.",
         }

class UserLoginResource(Resource) :
    # 로그인
    def post(self) :
        data = request.get_json()
        connection = get_connection()

        try :
            query = '''
                        select * from user
                        where email = %s;
                    '''
            record = ( data['email'], )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        # result_list = 1 : 유저 데이터 존재, 0 : 데이터 없음
        if len(result_list) != 1 :
            return {"error" : "존재하지 않는 회원입니다."}, 400

        # 비밀번호 확인
        user_info = result_list[0]
        check = check_password( data['password'], user_info['password'] )
        if check == False :
            return {"error" : "비밀번호가 맞지 않습니다."}, 400

        access_token = create_access_token(user_info['id'])

        return { "알림" : "로그인에 성공하였습니다.", "테스트용 토큰" : access_token }, 200
        
jwt_blocklist = set()

class UserLogoutResource(Resource) :
    # 로그아웃
    @jwt_required()
    def post(self) :

        jti = get_jwt()['jti']
        print(jti)

        jwt_blocklist.add(jti)

        return { "알림" : "로그아웃이 정상처리되었습니다."}

class MyInfoResource(Resource) :
    # 내 정보 보기
    @jwt_required()
    def get(self) :
        connection = get_connection()
        user_id = get_jwt_identity()
        try :
            query = '''select email, name, gender from user where id = %s;'''
            record = (user_id, ) # tuple
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_my_info = cursor.fetchall()

            query = ''' select m.title, r.rating from movie m
						join rating r on r.movie_id=m.id
                        where r.user_id = %s; '''
            record = (user_id, ) # tuple
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_my_review_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{
            "내 정보 보기" : result_my_info,
            "내 리뷰 보기" : result_my_review_list
        }, 200