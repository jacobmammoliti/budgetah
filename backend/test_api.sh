#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}/api/v1"
PASS=0
FAIL=0

CATEGORY_ID=""
CATEGORY2_ID=""
TRANSACTION_ID=""
BUDGET_ID=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass()   { echo -e "${GREEN}PASS${NC} $1"; PASS=$((PASS + 1)); }
fail()   { echo -e "${RED}FAIL${NC} $1 — $2"; FAIL=$((FAIL + 1)); }
header() { echo -e "\n${YELLOW}=== $1 ===${NC}"; }

assert_status() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$actual" == "$expected" ]]; then
    pass "$label (HTTP $actual)"
  else
    fail "$label" "expected HTTP $expected, got $actual"
  fi
}

# curl wrappers that never abort the script on connection errors
req() {
  local tmpfile
  tmpfile=$(mktemp)
  local status
  status=$(curl -sL -w "%{http_code}" -o "$tmpfile" "$@" || echo "000")
  printf '%s\n%s' "$(cat "$tmpfile")" "$status"
  rm -f "$tmpfile"
}

req_status() {
  curl -sL -o /dev/null -w "%{http_code}" "$@" || echo "000"
}

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
server_root="${BASE_URL%/api/v1}"
if ! curl -s -o /dev/null --max-time 3 "$server_root/docs" 2>/dev/null; then
  echo -e "${RED}Cannot reach server at $server_root — is it running?${NC}"
  exit 1
fi

# ---------------------------------------------------------------------------
# Cleanup (runs on EXIT)
# ---------------------------------------------------------------------------
cleanup() {
  header "Cleanup"
  local errors=0

  if [[ -n "$TRANSACTION_ID" ]]; then
    s=$(req_status -X DELETE "$BASE_URL/transactions/$TRANSACTION_ID")
    [[ "$s" == "204" ]] && echo "  deleted transaction $TRANSACTION_ID" \
      || { echo "  failed to delete transaction $TRANSACTION_ID (HTTP $s)"; errors=$((errors + 1)); }
  fi

  if [[ -n "$BUDGET_ID" ]]; then
    s=$(req_status -X DELETE "$BASE_URL/budgets/$BUDGET_ID")
    [[ "$s" == "204" ]] && echo "  deleted budget $BUDGET_ID" \
      || { echo "  failed to delete budget $BUDGET_ID (HTTP $s)"; errors=$((errors + 1)); }
  fi

  if [[ -n "$CATEGORY_ID" ]]; then
    s=$(req_status -X DELETE "$BASE_URL/categories/$CATEGORY_ID")
    [[ "$s" == "204" ]] && echo "  deleted category $CATEGORY_ID" \
      || { echo "  failed to delete category $CATEGORY_ID (HTTP $s)"; errors=$((errors + 1)); }
  fi

  if [[ -n "$CATEGORY2_ID" ]]; then
    s=$(req_status -X DELETE "$BASE_URL/categories/$CATEGORY2_ID")
    [[ "$s" == "204" ]] && echo "  deleted category $CATEGORY2_ID" \
      || { echo "  failed to delete category $CATEGORY2_ID (HTTP $s)"; errors=$((errors + 1)); }
  fi

  if [[ $errors -eq 0 ]]; then
    echo -e "  ${GREEN}All test data removed${NC}"
  else
    echo -e "  ${RED}$errors cleanup error(s)${NC}"
  fi
}

trap cleanup EXIT

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
header "Categories"

response=$(req -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Category","description":"Created by test_api.sh"}')
http_status=$(echo "$response" | tail -1)
json_body=$(echo "$response" | sed '$d')
assert_status "POST /categories" "201" "$http_status"
CATEGORY_ID=$(echo "$json_body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*' || true)

response=$(req -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Category 2","description":"Created by test_api.sh"}')
http_status=$(echo "$response" | tail -1)
json_body=$(echo "$response" | sed '$d')
assert_status "POST /categories (second)" "201" "$http_status"
CATEGORY2_ID=$(echo "$json_body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*' || true)

assert_status "GET /categories" "200" \
  "$(req_status "$BASE_URL/categories")"

assert_status "GET /categories/$CATEGORY_ID" "200" \
  "$(req_status "$BASE_URL/categories/$CATEGORY_ID")"

assert_status "GET /categories/999999 (not found)" "404" \
  "$(req_status "$BASE_URL/categories/999999")"

update='{"name":"Test Category Updated","description":"Updated by test_api.sh"}'
assert_status "PUT /categories/$CATEGORY_ID" "200" \
  "$(req_status -X PUT "$BASE_URL/categories/$CATEGORY_ID" -H "Content-Type: application/json" -d "$update")"

assert_status "PUT /categories/999999 (not found)" "404" \
  "$(req_status -X PUT "$BASE_URL/categories/999999" -H "Content-Type: application/json" -d "$update")"

# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------
header "Transactions"

today=$(date +%Y-%m-%d)

tx_body="{\"amount\":50.00,\"type\":\"expense\",\"description\":\"Test expense\",\"date\":\"$today\",\"category_id\":$CATEGORY_ID}"
response=$(req -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" -d "$tx_body")
http_status=$(echo "$response" | tail -1)
json_body=$(echo "$response" | sed '$d')
assert_status "POST /transactions" "201" "$http_status"
TRANSACTION_ID=$(echo "$json_body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*' || true)

assert_status "GET /transactions" "200" \
  "$(req_status "$BASE_URL/transactions")"

assert_status "GET /transactions?type=expense" "200" \
  "$(req_status "$BASE_URL/transactions?type=expense")"

assert_status "GET /transactions?type=income" "200" \
  "$(req_status "$BASE_URL/transactions?type=income")"

assert_status "GET /transactions?category_id=$CATEGORY_ID" "200" \
  "$(req_status "$BASE_URL/transactions?category_id=$CATEGORY_ID")"

assert_status "GET /transactions?start_date=$today&end_date=$today" "200" \
  "$(req_status "$BASE_URL/transactions?start_date=$today&end_date=$today")"

assert_status "GET /transactions/$TRANSACTION_ID" "200" \
  "$(req_status "$BASE_URL/transactions/$TRANSACTION_ID")"

assert_status "GET /transactions/999999 (not found)" "404" \
  "$(req_status "$BASE_URL/transactions/999999")"

tx_update='{"amount":75.00,"description":"Updated by test_api.sh"}'
assert_status "PUT /transactions/$TRANSACTION_ID" "200" \
  "$(req_status -X PUT "$BASE_URL/transactions/$TRANSACTION_ID" -H "Content-Type: application/json" -d "$tx_update")"

assert_status "PUT /transactions/999999 (not found)" "404" \
  "$(req_status -X PUT "$BASE_URL/transactions/999999" -H "Content-Type: application/json" -d "$tx_update")"

# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------
header "Budgets"

source_month="2099-01"
target_month="2099-02"

budget_body="{\"category_id\":$CATEGORY_ID,\"month\":\"$source_month\",\"limit_amount\":500.00}"
response=$(req -X POST "$BASE_URL/budgets" \
  -H "Content-Type: application/json" -d "$budget_body")
http_status=$(echo "$response" | tail -1)
json_body=$(echo "$response" | sed '$d')
assert_status "POST /budgets" "201" "$http_status"
BUDGET_ID=$(echo "$json_body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*' || true)

assert_status "POST /budgets (duplicate → 409)" "409" \
  "$(req_status -X POST "$BASE_URL/budgets" -H "Content-Type: application/json" -d "$budget_body")"

assert_status "GET /budgets" "200" \
  "$(req_status "$BASE_URL/budgets")"

assert_status "GET /budgets/$BUDGET_ID" "200" \
  "$(req_status "$BASE_URL/budgets/$BUDGET_ID")"

assert_status "GET /budgets/999999 (not found)" "404" \
  "$(req_status "$BASE_URL/budgets/999999")"

copy_body="{\"source_month\":\"$source_month\",\"target_month\":\"$target_month\"}"
assert_status "POST /budgets/copy" "200" \
  "$(req_status -X POST "$BASE_URL/budgets/copy" -H "Content-Type: application/json" -d "$copy_body")"

bad_copy="{\"source_month\":\"$source_month\",\"target_month\":\"$source_month\"}"
assert_status "POST /budgets/copy (same month → 422)" "422" \
  "$(req_status -X POST "$BASE_URL/budgets/copy" -H "Content-Type: application/json" -d "$bad_copy")"

# Remove budgets copied into target_month (not tracked by ID)
budgets_json=$(curl -s "$BASE_URL/budgets" || true)
copied_ids=$(echo "$budgets_json" \
  | grep -o '"id":[0-9]*,"category_id":[0-9]*,"month":"'"$target_month"'"' \
  | grep -o '"id":[0-9]*' | grep -o '[0-9]*' || true)
for bid in $copied_ids; do
  curl -s -o /dev/null -X DELETE "$BASE_URL/budgets/$bid" || true
  echo "  pre-cleaned copied budget $bid"
done

assert_status "DELETE /budgets/$BUDGET_ID" "204" \
  "$(req_status -X DELETE "$BASE_URL/budgets/$BUDGET_ID")"
BUDGET_ID=""

assert_status "DELETE /budgets/999999 (not found)" "404" \
  "$(req_status -X DELETE "$BASE_URL/budgets/999999")"

# ---------------------------------------------------------------------------
# Delete endpoints
# ---------------------------------------------------------------------------
header "Delete endpoints"

assert_status "DELETE /transactions/$TRANSACTION_ID" "204" \
  "$(req_status -X DELETE "$BASE_URL/transactions/$TRANSACTION_ID")"
TRANSACTION_ID=""

assert_status "DELETE /transactions/999999 (not found)" "404" \
  "$(req_status -X DELETE "$BASE_URL/transactions/999999")"

assert_status "DELETE /categories/$CATEGORY_ID" "204" \
  "$(req_status -X DELETE "$BASE_URL/categories/$CATEGORY_ID")"
CATEGORY_ID=""

assert_status "DELETE /categories/999999 (not found)" "404" \
  "$(req_status -X DELETE "$BASE_URL/categories/999999")"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
header "Results"
total=$((PASS + FAIL))
echo -e "  Passed: ${GREEN}$PASS${NC} / $total"
[[ $FAIL -gt 0 ]] && echo -e "  Failed: ${RED}$FAIL${NC} / $total"
[[ $FAIL -eq 0 ]] && echo -e "${GREEN}All tests passed.${NC}" \
  || { echo -e "${RED}$FAIL test(s) failed.${NC}"; exit 1; }
