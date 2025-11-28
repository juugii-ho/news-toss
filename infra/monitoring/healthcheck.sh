#!/bin/bash

# API Health Check
API_URL="your_api_url/health"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ "$API_STATUS" -eq 200 ]; then
  echo "API is healthy."
else
  echo "API is down! HTTP status code: $API_STATUS"
  exit 1
fi

# DB Health Check (예시: Supabase)
# 실제로는 더 정교한 방법이 필요할 수 있습니다.
DB_URL="your_supabase_url"
if curl -s $DB_URL > /dev/null; then
  echo "DB connection seems ok."
else
  echo "DB connection failed."
  exit 1
fi

echo "All services are healthy."
exit 0
