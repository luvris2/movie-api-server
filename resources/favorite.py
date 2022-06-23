from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from ref.mysql_connection import get_connection

class FavoriteResource(Resource) :
    #  즐겨찾기 추가
    @jwt_required()
    def post(self, movie_id) :
        try :
            user_id = get_jwt_identity()
            favorite = request.args.get('favorite')

            query = ''' insert into favorite
                        (movie_id, user_id, favorite)
                    values
                        (%s ,%s ,%s);
                    '''
            record = (movie_id, user_id, favorite)
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

        return{ "알림" : "즐겨찾기가 추가되었습니다." }, 200

    # 즐겨찾기 해제
    @jwt_required()
    def delete(self, movie_id) :
        try :
            connection = get_connection()
            user_id = get_jwt_identity()
            query = ''' delete from favorite where movie_id = %s and user_id = %s; '''
            record = (movie_id, user_id)
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

        return{ "알림" : "즐겨찾기가 해제되었습니다." }, 200

    # 나의 즐겨찾기 목록 보기
class MyFavoriteResource(Resource) :
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            user_id = get_jwt_identity()
            page = request.args.get('page')
            page = str((int(page)-1)*25)
            query = '''
                        select m.title as '영화명', count(r.movie_id) as '리뷰갯수', avg(r.rating) as '별점평균',
                        if(f.user_id = ''' +str(user_id)+''', 1, 0) as '즐겨찾기'
                        from movie m join rating r on r.movie_id=m.id
                        join favorite f on f.movie_id=m.id
                        group by m.title
                        limit
                    ''' + page + ''', 25;'''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            i = 0
            for record in result_list:
                result_list[i]['별점평균'] = float(record['별점평균'])
                i += 1
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{
            "영화 정보" : result_list
        }, 200   