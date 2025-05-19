import random

from faker import Faker
from locust import HttpUser, between, task

fake = Faker()


class ApiTestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """テスト開始時に実行される初期化処理"""
        self.auth_token = self.login()
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    def login(self):
        """認証トークンを取得"""
        response = self.client.post(
            "/api/auth/login", json={"username": "testuser", "password": "testpass123"}
        )
        return response.json().get("access_token")

    @task(3)
    def get_items(self):
        """商品一覧の取得"""
        params = {
            "page": random.randint(1, 5),
            "per_page": random.choice([10, 20, 50]),
            "sort_by": random.choice(["id", "price", "created_at"]),
            "order": random.choice(["asc", "desc"]),
        }
        with self.client.get(
            "/api/items", params=params, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get items: {response.text}")

    @task(2)
    def get_item_detail(self):
        """商品詳細の取得"""
        item_id = random.randint(1, 1000)
        with self.client.get(
            f"/api/items/{item_id}", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 404:
                response.success()  # 存在しないIDでもエラーとしない
            elif response.status_code != 200:
                response.failure(f"Failed to get item {item_id}: {response.text}")

    @task(1)
    def create_item(self):
        """商品の作成"""
        item_data = {
            "name": fake.catch_phrase(),
            "description": fake.paragraph(),
            "price": round(random.uniform(10, 1000), 2),
            "stock": random.randint(0, 1000),
            "category_id": random.randint(1, 10),
        }
        with self.client.post(
            "/api/items", json=item_data, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Failed to create item: {response.text}")

    @task(1)
    def search_items(self):
        """商品検索"""
        search_terms = ["phone", "laptop", "monitor", "keyboard", "mouse"]
        query = random.choice(search_terms)
        params = {"q": query, "page": 1, "per_page": 20}
        with self.client.get(
            "/api/items/search",
            params=params,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Search failed for '{query}': {response.text}")

    @task(1)
    def get_user_profile(self):
        """ユーザープロフィール取得"""
        with self.client.get(
            "/api/users/me", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get user profile: {response.text}")
