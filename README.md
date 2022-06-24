# 영화 추천 시스템 API 
**기능 설명**
- 회원가입, 로그인, 로그아웃, 내 정보보기 기능
- 영화 목록 보기, 특정 영화 상세보기, 영화 검색 기능
- 리뷰 작성, 보기 기능
- 즐겨찾기 추가, 해제, 나의 즐겨찾기 목록 보기 기능
- 실시간 영화 추천 기능
---
# DB 구조
### Table : movie
- Columns
  - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
  - title : 영화 제목 (VARCHAR(100)
  - genre : 영화 장르 (VARCHAR(100)
  - summary : 영화 설명 (VARCHAR(500)
  - attendance : 관람객 (INT)
  - year : 개봉일 (TIMESTAMP)
- Foreign Keys
  - memo table : user_id -> user table : id
### Table : user
- Columns
  - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
  - email : 이메일 (VARCHAR(45)/ UQ)
  - password : 비밀번호 (VARCHAR200)
  - name : 사용자 이름 (VARCHAR45)
  - gender : 성별 (VARCHAR(10)
### Table : favorite
- Columns
   - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
   - user_id : 사용자 식별 ID (INT/ UN)
   - movie_id : 영화 식별 ID (INT/ UN)
   - created_at : 즐겨찾기지정일 (TIMESTAMP)/ Default=now()
   - favorite : 즐겨찾기여부 (TINYINT/ NN, UN)/ Default=False
- Foreign Keys
  - favorite table : user_id -> user table : id
  - favorite table : movie_id -> movie table : id
### Table : rating
- Columns
   - id : 기본 인덱스 (INT/ PK, NN, UN, AI)
   - user_id : 사용자 식별 ID (INT/ UN)
   - movie_id : 영화 식별 ID (INT/ UN)
   - created_at : 리뷰 작성일 (TIMESTAMP)/ Default=now()
   - updated_at : 리뷰 수정일 (TIMESTAMP)/ Default=now() on update now()
---

# 파일 구조
- app.py : API 메인 파일
  - resources 폴더
    - favorite.py : 즐겨찾기 추가, 해제, 목록보기 기능
    - movie.py : 영화 목록, 상세 정보, 검색 기능
    - user.py : 회원가입, 로그인, 로그아웃, 나의 정보 보기 기능
  - ref 폴더
    - config.py : 가상환경 설정 (토큰)
    - mysql_connection.py : DB 연동 설정
    - utils.py : 비밀번호 암호화, 식별 ID 토큰화 설정
  - data 폴더
    - movie_correlations.csv : 영화 추천 시스템의 상관관계 계수를 가지는 데이터 프레임 (실시간에서는 사용 X)
---
# 각 파일 설명
**app.py**
- API의 기본 틀이 되는 메인 파일
- 가상 환경 셋팅
- JWT 토큰을 생성과 파괴
- 리소스화 된 클래스들의 경로 설정 (API 기능)

---
**mysql_connection.py**
- DB 연동에 관련된 함수를 정의한 파일
  - 해당 코드는 개개인의 환경에 따라 다르므로 파일은 미첨부
  - 아래의 코드로 파일을 생성하여 자신의 환경에 맞게 코딩
``` python
import mysql.connector
def get_connection() :
    connection = mysql.connector.connect(
        host='hostname',
        database='databasename',
        user='username',
        password='password' )
    return connection
```
---
**config.py**
- 가상 환경의 값을 설정하는 파일
  - 토큰의 암호화 방식 설정
    - 토큰의 시크릿 키는 원래 비공개이나 테스트용이기 때문에 공개처리
    - 토큰은 유저의 개인 식별 ID를 암호화하여 사용

**utils.py**
- 사용자로부터 입력받은 비밀번호를 암호화하는 파일
  - 입력 받은 비밀번호를 해시로 매핑하여 암호화
  - 암호화된 비밀번호와 새로 입력 받은 값이 같은지 확인

---

**user.py**
- Class UserRegisterResource
  - 회원가입을 하면 DB에 입력한 정보가 등록되는 기능
    - 이메일과 비밀번호 유효성 검사
    - 비밀번호 암호화, 식별 ID 토큰화
- class UserLoginResource
  - 로그인
    - DB에 입력한 이메일 존재 유무와 비밀번호 동일 유무 확인
    - 입력한 데이터가 DB의 정보와 일치하면 식별 ID 토큰 생성
- class UserLogoutResource
  - 로그아웃
    - 생성된 토큰을 파괴  

---
 **movie.py**
- class MovieListResource
  - 전체 영화 목록 페이지당 25개씩 출력
- class MovieDetailResource
  - 특정 영화 상세 보기
    - 영화명, 개봉일, 관람객, 별점평균
- class MovieSearchResource
  - 영화 검색
    - 검색어가 포함된 영화 출력
---
**favorite.py**
- class FavoriteResource
    - 즐겨찾기 추가, 해제, 즐겨찾기 목록 보기
 ---
**recommend.py**
- class MovieRecommendResource
  - 전체 영화의 상관관계를 구한 csv파일을 이용하여 유사도 높은 영화를 추천
- class MovieRecommendRealTimeResource
  - DB의 데이터를 가공하여 상관관계를 구하고 유사도 높은 
 영화를 실시간으로 추천