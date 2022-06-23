from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from ref.mysql_connection import get_connection

import pandas as pd
import numpy as np

class MovieRecommendResource(Resource) :
    # 영화 추천 서비스
    @jwt_required()
    def get(self):
        # 유저 식별
        user_id = get_jwt_identity()

        # 추천을 위한 상관계수 데이터프레임 호출
        df = pd.read_csv('data/movie_correlations.csv', index_col='title')

        # 유저의 별점 정보를 DB에서 호출
        try :
            connection = get_connection()
            query = ''' select r.user_id, r.movie_id, r.rating, m.title from rating r
                        join movie m on r.movie_id = m.id and r.user_id = %s; '''
            record = (user_id, ) # tuple
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

        # 나의 별점 정보를 DB에서 가져오고 데이터프레임에 저장
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할 데이터프레임 초기화
        similar_movie_list = pd.DataFrame()
        for i in range( len(df_my_rating) ) :
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns= ['Correlations']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlations']
            similar_movie_list = pd.concat([similar_movie_list, similar_movie])
        
        # 영화 제목(이름이 같은 다른 영화) 중복 제거, Weight가 가장 큰 값(Max)으로 선택
        similar_movie_list.reset_index(inplace=True)
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 평점을 남긴 영화 목록을 확인하고 추천 리스트에서 제외
        similar_movie_list = similar_movie_list.reset_index()
        title_list = df_my_rating['title'].tolist()
        recommend_movie_list = similar_movie_list.loc[ ~similar_movie_list['title'].isin(title_list),]
        #print(recommend_movie_list.iloc[0:20,])

        return {
                "추천 영화 리스트" : recommend_movie_list.iloc[0 : 20 , ].to_dict("records")
                }
