# CI Demo API

REST API nhỏ để quản lý bài viết và tài khoản người dùng, xây dựng bằng FastAPI, SQLAlchemy và PostgreSQL.

Dự án được phát triển từ [fastapi-sqlalchemy-postgres-template](https://github.com/mdhishaamakhtar/fastapi-sqlalchemy-postgres-template) của mdhishaamakhtar và đã được chỉnh sửa so với bản gốc. Giấy phép GPLv3, xem chi tiết tại [LICENSE](LICENSE).

## Mục lục

- [Chọn cách chạy](#chọn-cách-chạy)
- [Chạy bằng Docker](#chạy-bằng-docker)
- [Chạy ở local](#chạy-ở-local)
- [Thêm dữ liệu](#thêm-dữ-liệu)
- [API](#api)
- [Phát triển](#phát-triển)
- [Xử lý lỗi thường gặp](#xử-lý-lỗi-thường-gặp)
- [CI/CD](#cicd)

## Chọn cách chạy

| | Docker | Local |
| --- | --- | --- |
| **Cần cài** | Docker | Python 3.10+ và PostgreSQL |
| **Database** | Được tạo tự động khi khởi động | Bạn tạo thủ công trước khi chạy |
| **Dữ liệu mẫu** | Được nạp tự động ở lần chạy đầu | Bạn nạp thủ công bằng `psql` |
| **Khi sửa code** | Phải build lại | Server tự tải lại |
| **Phù hợp khi** | Muốn chạy nhanh | Đang phát triển tính năng |

Nếu chỉ muốn chạy thử, hãy dùng Docker.

## Chạy bằng Docker

1. Tạo file cấu hình:

   ```bash
   cp .env.example .env
   ```

2. Mở `.env` và đặt giá trị cho `POSTGRES_PASSWORD`. Tránh các ký tự như `@`, `:`, `/` hoặc `#` vì mật khẩu được ghép trực tiếp vào chuỗi kết nối.

3. Khởi động API và database:

   ```bash
   docker compose up --build -d
   ```

4. Kiểm tra cả `ci_demo_api` và `ci_demo_db` đều ở trạng thái `running`:

   ```bash
   docker compose ps
   ```

5. Mở <http://127.0.0.1:8000/docs>.

Ở lần chạy đầu, database sẽ có sẵn 10 bài viết và 5 người dùng mẫu.

### Các lệnh thường dùng

| Mục đích | Lệnh |
| --- | --- |
| Xem log của API | `docker compose logs -f api` |
| Build lại sau khi sửa code | `docker compose up --build -d` |
| Dừng dự án, giữ dữ liệu | `docker compose down` |
| Dừng dự án và **xóa toàn bộ dữ liệu** | `docker compose down -v` |

## Chạy ở local

Bạn cần cài sẵn Python 3.10+ và PostgreSQL, đồng thời PostgreSQL phải đang chạy.

1. Tạo và kích hoạt môi trường ảo:

   ```bash
   python -m venv .venv

   # macOS/Linux
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

2. Cài các thư viện:

   ```bash
   pip install -r requirements.txt
   ```

3. Tạo tài khoản và database. Kết nối bằng tài khoản quản trị của PostgreSQL (thường là `postgres`), rồi thay `<password>` bằng mật khẩu của bạn:

   ```sql
   CREATE USER admin WITH PASSWORD '<password>';
   CREATE DATABASE demo_db OWNER admin;
   ```

4. Tạo file cấu hình:

   ```bash
   cp .env.example .env
   ```

5. Mở `.env` và sửa `DATABASE_URL` cho đúng database của bạn. Nếu mật khẩu có ký tự đặc biệt, hãy mã hóa URL cho mật khẩu đó (ví dụ `@` thành `%40`):

   ```env
   DATABASE_URL=postgresql://admin:<password>@localhost:5432/demo_db
   ```

6. Khởi động server. Các bảng sẽ được tạo tự động:

   ```bash
   uvicorn main:app --reload
   ```

7. Mở <http://127.0.0.1:8000/docs>.

Database lúc này còn trống. Để có dữ liệu mẫu, hãy làm theo phần [Thêm dữ liệu](#thêm-dữ-liệu).

## Thêm dữ liệu

Dữ liệu mẫu nằm trong [`database/seed.sql`](database/seed.sql). Muốn thêm dữ liệu, hãy thêm dòng vào file này với ID tiếp theo, rồi chạy lệnh tương ứng:

**Docker**

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/01-seed.sql'
```

**Local**

```bash
psql "postgresql://admin:<password>@localhost:5432/demo_db" -f database/seed.sql
```

Có thể chạy file này nhiều lần mà không tạo dữ liệu trùng. Những dòng đã tồn tại sẽ được bỏ qua, nên việc sửa một dòng trong file sẽ không cập nhật dòng đó trong database.

Nếu chỉ cần thêm vài bản ghi, bạn có thể dùng `POST /articles` hoặc `POST /users` ngay trong trang `/docs`.

### Tài khoản mẫu

Mọi người dùng mẫu đều có mật khẩu `Password123!`, vì vậy không nên nạp dữ liệu mẫu lên môi trường thật.

| ID | Email | Tên |
| --- | --- | --- |
| 1 | `alice@example.com` | Alice Nguyen |
| 2 | `bob@example.com` | Bob Tran |
| 3 | `chi@example.com` | Chi Le |
| 4 | `dung@example.com` | Dung Pham |
| 5 | `emma@example.com` | Emma Vo |

## API

Khi server đang chạy, tài liệu API có tại `/docs` và `/redoc`.

| Phương thức | Đường dẫn | Chức năng |
| --- | --- | --- |
| GET | `/` | Kiểm tra trạng thái server |
| POST | `/articles` | Tạo bài viết |
| GET | `/articles` | Lấy danh sách bài viết |
| GET | `/articles/{article_id}` | Xem một bài viết |
| PATCH | `/articles/{article_id}` | Sửa bài viết |
| DELETE | `/articles/{article_id}` | Xóa bài viết |
| POST | `/users` | Tạo tài khoản |
| GET | `/users` | Lấy danh sách người dùng |
| GET | `/users/{user_id}` | Xem một người dùng |
| PATCH | `/users/{user_id}` | Sửa người dùng (chỉ gửi các trường cần đổi) |
| DELETE | `/users/{user_id}` | Xóa người dùng |

- **ID:** là số nguyên tự tăng, ví dụ `/articles/1`.
- **Mật khẩu:** được lưu dưới dạng hash scrypt có salt và không bao giờ được trả về.
- **Bảo mật:** API chưa có chức năng đăng nhập, nên bất kỳ ai truy cập được API đều có thể gọi các endpoint này. Đừng để API mở ra internet khi chưa bổ sung xác thực.

## Phát triển

```bash
pytest     # dùng file SQLite cục bộ, trừ khi DATABASE_URL đã được đặt trong shell
black .    # định dạng code
```

## Xử lý lỗi thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
| --- | --- | --- |
| Trình duyệt báo `ERR_CONNECTION_REFUSED` | API chưa chạy, hoặc `docker compose up -d db` chỉ khởi động database | Chạy `docker compose up -d`, nếu vẫn lỗi thì xem `docker compose logs api` |
| Docker báo cổng `5432` hoặc `8000` đang được dùng | Dịch vụ khác đang chiếm cổng, ví dụ PostgreSQL cài trên máy | Tắt dịch vụ đó hoặc đổi cổng trong `docker-compose.yml` |
| Seed báo `column "id" is of type uuid` | Database được tạo từ phiên bản cũ dùng UUID | Sao lưu nếu cần, rồi tạo lại database. Với Docker, chạy `docker compose down -v` rồi `docker compose up --build -d` |
| Không thấy dữ liệu mẫu trong Docker | Seed chỉ tự nạp khi volume được tạo lần đầu | Chạy lệnh trong phần [Thêm dữ liệu](#thêm-dữ-liệu) |

## CI/CD

GitHub Actions chạy các workflow trong `.github/workflows/`:

| Workflow | Khi nào chạy | Việc thực hiện |
| --- | --- | --- |
| `tests.yml` | Khi có pull request hoặc push lên các nhánh khác | Kiểm tra định dạng code, rồi chạy unit test và integration test với PostgreSQL |
| `docker.yml` | Khi push lên `main` hoặc `master` | Chạy `tests.yml`, nếu đạt thì đăng Docker image lên `ghcr.io` |
