from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from ref.mysql_connection import get_connection

class ReviewDetailResource(Resource) :
    # 리뷰 보기
    def get(self, movie_id) :
        try :
            connection = get_connection()
            query = ''' select title from movie where id = %s; '''
            record = (movie_id, ) # tuple
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            movie_name = cursor.fetchall()

            page = request.args.get('page')
            page = str((int(page)-1)*25)
            query = '''
                        select m.title as '영화명', u.name as '유저', u.gender as '성별', r.rating as '별점'
                        from user u join rating r on r.user_id=u.id
                        join movie m on r.movie_id=m.id
                        where m.id = %s
                        limit
                    ''' + page + ''', 25;'''
            record = (movie_id, )
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

        return{
            "리뷰" : movie_name[0]['title']+" 리뷰",
            "리뷰 목록" : result_list
        }, 200

class AddReviewResource(Resource) :
    # 특정 영화에 리뷰 작성
    @jwt_required()
    def post(self, movie_id) :
        data = request.get_json()
        try :
            connection = get_connection()
            user_id = get_jwt_identity()
            query = '''insert into rating (movie_id, rating, content, user_id)
                        values(%s, %s, %s, %s);'''
            record = (movie_id, data['rating'], data['content'], user_id)
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
                    "알림" : "리뷰가 작성되었습니다.",
                    "작성된 리뷰" : data
                }, 200