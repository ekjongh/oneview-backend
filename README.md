# Oneview Backend 개발
- 2022.05.16 START

# Fastapi Process
![initial](https://user-images.githubusercontent.com/64005035/168970027-ddb82624-163f-4e1c-8942-7f2b0f782835.png)
# Directory 구조 설명(구축중...)
```
ㅇ. https://github.com/tiangolo/full-stack-fastapi-postgresql 참조..
.env # 배포 시 OS 환경변수 설정용
.gitignore # github push 예외파일 작성
requirements.txt # python package 리스트
-------------------------------------------------------
app --  core        --  config.py # CONFIG 설정
                        security.py # 보안 관련 CONFIG 저장
    --  crud        --  # 작성중 / DB MODEL CRUD용
    --  db          --  base.py
                    --  base_class.py
                    --  session.py
    --  errors      --  exceptions.py # HTTP EXCEPTION 정리
    --  middleware  # middleware 정리
    --  models      -- xxx.py # xxx api 서비스 용 DB 모델 생성
    --  routers     -- api.py # api routing 설정
                    -- endpoints  -- xxx.py # ~/xxx api 요청 처리
    --  utils       -- api 처리 로직 중 복잡한 로직 개발 및 정리.
    --  schemas     -- xxx.py # xxx model 스키마 정의
        dependencies.py # endpoints 별 Dependency를 가지는 로직(EX. api1 에 get 요청을 하기 위해서는 TOKEN1을 가져야 한다)
        main.py # fastapi app 실행 main 파일.
```