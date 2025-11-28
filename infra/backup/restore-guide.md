# Database Restore Guide (from Supabase Backup)

> 이 문서는 Supabase 백업으로부터 데이터베이스를 복구하는 절차를 안내합니다.

## 1. 백업 파일 다운로드

1.  [Supabase Dashboard](https://app.supabase.io/)에 접속합니다.
2.  해당 프로젝트의 `Database` -> `Backups` 섹션으로 이동합니다.
3.  복구를 원하는 시점의 백업 파일을 다운로드합니다.

## 2. 로컬에서 데이터베이스 복구

1.  로컬에 Docker와 PostgreSQL이 설치되어 있는지 확인합니다.
2.  다운로드한 백업 파일(`backup.sql.gz`)의 압축을 해제합니다.
    ```bash
    gunzip backup.sql.gz
    ```
3.  PostgreSQL Docker 컨테이너를 실행합니다.
    ```bash
    docker run --name local-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres
    ```
4.  백업 파일을 로컬 데이터베이스에 복원합니다.
    ```bash
    psql -h localhost -p 5432 -U postgres -d postgres -f backup.sql
    ```

## 3. Supabase 프로젝트에 복구 (주의!)

**경고: 이 작업은 기존의 모든 데이터를 덮어씁니다. 신중하게 진행하세요.**

1.  기존 Supabase 프로젝트를 완전히 초기화하거나 새로운 프로젝트를 생성합니다.
2.  새로운 프로젝트의 연결 정보를 확인합니다.
3.  로컬의 `psql`을 사용하여 백업 파일을 원격 Supabase DB에 복원합니다.
    ```bash
    psql "postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]" -f backup.sql
    ```
