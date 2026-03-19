#!/bin/bash
# Test: Can we reliably parse ancestor-path from notion-fetch results
# to determine if a page belongs to the "CLAUDE [Jonah]" workspace?

ALLOWED_ROOT="3190f22f7b6e80188099e1454419dfec"

# Test 1: Deep nested page (task in Tasks Tracker → Database → Root)
echo "=== Test 1: Deep nested page (3 ancestors) ==="
TOOL_RESULT='<ancestor-path>
<parent-data-source url="collection://3190f22f-7b6e-80c6-ba9c-000b9942d257" name="Tasks Tracker"/>
<ancestor-2-database url="https://www.notion.so/3190f22f7b6e8053838fd88198146c4f" title=""/>
<ancestor-3-page url="https://www.notion.so/3190f22f7b6e80188099e1454419dfec" title="CLAUDE [Jonah]"/>
</ancestor-path>'
ROOT_ID=$(echo "$TOOL_RESULT" | grep -oP '(ancestor-\d+-page|parent-page) url="https://www.notion.so/\K[a-f0-9]+' | tail -1)
echo "Root ID: $ROOT_ID"
echo "Expected: $ALLOWED_ROOT"
echo "Match: $([ "$ROOT_ID" = "$ALLOWED_ROOT" ] && echo PASS || echo FAIL)"

# Test 2: Direct child of root page (parent-page tag)
echo ""
echo "=== Test 2: Direct child of root page ==="
TOOL_RESULT2='<ancestor-path>
<parent-page url="https://www.notion.so/3190f22f7b6e80188099e1454419dfec" title="CLAUDE [Jonah]"/>
</ancestor-path>'
ROOT_ID2=$(echo "$TOOL_RESULT2" | grep -oP '(ancestor-\d+-page|parent-page) url="https://www.notion.so/\K[a-f0-9]+' | tail -1)
echo "Root ID: $ROOT_ID2"
echo "Match: $([ "$ROOT_ID2" = "$ALLOWED_ROOT" ] && echo PASS || echo FAIL)"

# Test 3: Empty ancestor path (workspace-level page, NOT in workspace)
echo ""
echo "=== Test 3: Workspace-level page (should NOT match) ==="
TOOL_RESULT3='<ancestor-path></ancestor-path>'
ROOT_ID3=$(echo "$TOOL_RESULT3" | grep -oP '(ancestor-\d+-page|parent-page) url="https://www.notion.so/\K[a-f0-9]+' | tail -1)
echo "Root ID: '$ROOT_ID3'"
echo "Match: $([ "$ROOT_ID3" = "$ALLOWED_ROOT" ] && echo FAIL - false positive || echo PASS - correctly rejected)"

# Test 4: Page under different root
echo ""
echo "=== Test 4: Different root (should NOT match) ==="
TOOL_RESULT4='<ancestor-path>
<parent-page url="https://www.notion.so/aaaa1111bbbb2222cccc3333dddd4444" title="Someone Else"/>
<ancestor-2-page url="https://www.notion.so/ffff5555eeee6666dddd7777cccc8888" title="Other Root"/>
</ancestor-path>'
ROOT_ID4=$(echo "$TOOL_RESULT4" | grep -oP '(ancestor-\d+-page|parent-page) url="https://www.notion.so/\K[a-f0-9]+' | tail -1)
echo "Root ID: $ROOT_ID4"
echo "Match: $([ "$ROOT_ID4" = "$ALLOWED_ROOT" ] && echo FAIL - false positive || echo PASS - correctly rejected)"

# Test 5: Simulating create-pages tool input - check parent IDs
echo ""
echo "=== Test 5: create-pages with known data_source_id ==="
KNOWN_IDS="3190f22f7b6e80188099e1454419dfec 3190f22f7b6e80be8065ea5656df56b2 3190f22f7b6e8053838fd88198146c4f 3190f22f7b6e806cbe36000b0c4091ac 3190f22f7b6e80c6ba9c000b9942d257"
CREATE_INPUT='{"parent":{"data_source_id":"3190f22f-7b6e-80c6-ba9c-000b9942d257"},"pages":[{"properties":{"Task name":"Test"}}]}'
# Extract parent ID (could be page_id, database_id, or data_source_id)
PARENT_ID=$(echo "$CREATE_INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
parent = data.get('parent', {})
pid = parent.get('page_id') or parent.get('database_id') or parent.get('data_source_id') or ''
print(pid.replace('-', ''))
")
echo "Parent ID (normalized): $PARENT_ID"
echo "In allowlist: $(echo "$KNOWN_IDS" | grep -qw "$PARENT_ID" && echo PASS || echo FAIL)"

# Test 6: create-pages with page_id parent (root page itself)
echo ""
echo "=== Test 6: create-pages under root page_id ==="
CREATE_INPUT2='{"parent":{"page_id":"3190f22f-7b6e-8018-8099-e1454419dfec"},"pages":[{"properties":{"title":"Test subpage"}}]}'
PARENT_ID2=$(echo "$CREATE_INPUT2" | python3 -c "
import sys, json
data = json.load(sys.stdin)
parent = data.get('parent', {})
pid = parent.get('page_id') or parent.get('database_id') or parent.get('data_source_id') or ''
print(pid.replace('-', ''))
")
echo "Parent ID (normalized): $PARENT_ID2"
echo "In allowlist: $(echo "$KNOWN_IDS" | grep -qw "$PARENT_ID2" && echo PASS || echo FAIL)"

# Test 7: create-pages with NO parent (workspace level - should block)
echo ""
echo "=== Test 7: create-pages with no parent (should block) ==="
CREATE_INPUT3='{"pages":[{"properties":{"title":"Orphan page"}}]}'
PARENT_ID3=$(echo "$CREATE_INPUT3" | python3 -c "
import sys, json
data = json.load(sys.stdin)
parent = data.get('parent', {})
pid = parent.get('page_id') or parent.get('database_id') or parent.get('data_source_id') or ''
print(pid.replace('-', ''))
")
echo "Parent ID: '$PARENT_ID3'"
echo "In allowlist: $([ -z "$PARENT_ID3" ] && echo 'PASS - correctly empty, would ask' || echo "$PARENT_ID3")"

# Test 8: create-pages with unknown parent
echo ""
echo "=== Test 8: create-pages under unknown page (should NOT be in allowlist) ==="
CREATE_INPUT4='{"parent":{"page_id":"deadbeef-1234-5678-9abc-def012345678"},"pages":[{"properties":{"title":"Wrong place"}}]}'
PARENT_ID4=$(echo "$CREATE_INPUT4" | python3 -c "
import sys, json
data = json.load(sys.stdin)
parent = data.get('parent', {})
pid = parent.get('page_id') or parent.get('database_id') or parent.get('data_source_id') or ''
print(pid.replace('-', ''))
")
echo "Parent ID (normalized): $PARENT_ID4"
echo "In allowlist: $(echo "$KNOWN_IDS" | grep -qw "$PARENT_ID4" && echo FAIL - false positive || echo PASS - correctly rejected)"
