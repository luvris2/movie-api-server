from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from ref.mysql_connection import get_connection

class MovieListResource(Resource) :
    # 최대 25개의 영화 목록 출력, 리뷰와 별점은 내림차순
    # 페이지당 25개의 영화 목록을 출력
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            user_id = get_jwt_identity()
            page = request.args.get('page')
            page = str((int(page)-1)*25)
            order_var = request.args.get('order_var')
            query = '''
                        select m.title as '영화명', count(r.movie_id) as '리뷰갯수', avg(r.rating) as '별점평균',
                        if(f.user_id = ''' +str(user_id)+''', 1, 0) as '즐겨찾기'
                        from movie m join rating r on r.movie_id=m.id
                        left join favorite f on f.movie_id=m.id
                        group by m.title order by '''+ order_var +''' desc
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

class MovieDetailResource(Resource) :
    # 특정 영화 상세 정보 보기
    def get(self, movie_id) :
        try :
            connection = get_connection()
            query = '''
                        select m.title as'영화명', m.year as '개봉일', m.attendance as '관객수', avg(r.rating) as '별점평균'
                        from movie m join rating r on r.movie_id=m.id
                        where movie_id= %s;
                    '''
            record = (movie_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            i = 0
            for record in result_list :
                result_list[i]['개봉일'] = record['개봉일'].isoformat()
                result_list[i]['별점평균'] = float(record['별점평균'])
                i += 1
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return {"영화 상세 정보 보기" : result_list}, 200

class MovieSearchResource(Resource) :
    # 영화 검색
    def get(self) :
        try :
            connection = get_connection()
            keyword = request.args.get('keyword')
            query = '''
                        select m.title as '영화명', count(r.movie_id) as '리뷰갯수', avg(r.rating) as '별점평균'
                        from movie m join rating r on r.movie_id=m.id
                        where m.title like '%{}%'
                        group by m.title;
                    '''.format(keyword)
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

        return {"검색 결과" : result_list}, 200